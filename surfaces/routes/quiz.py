"""Quiz routes; daemon-owned helpers are imported at request time."""
from model import load
from model import parse_lesson
from runtime import PolynomialRefusal
from runtime import explain_payload
from runtime import read_session
from runtime import submission_feedback
from surfaces import ia
from surfaces import presentation
from surfaces import quiz
from surfaces import quiz_page
from surfaces import session
from surfaces import settings
from surfaces import theme
import datetime
import email.message
import evidence
import json
import os
import re
import secrets
import time
import urllib.parse
import urllib.request
import uuid
import threading


QUIZ_GET_RE = re.compile(r"^/quiz/(?P<stem>[^/]+)$")
QUIZ_ANSWER_RE = re.compile(r"^/quiz/(?P<stem>[^/]+)/answer$")


def handle_quiz_get(handler, stem):
    """`GET /quiz/<stem>` -- the quiz page for one bank, resolved through the
    startup allowlist and rendered by the existing `quiz.page_for()`. No key
    data is sent: `serve=True` is what makes `page_for` omit it. The page
    receives the same per-render theme block as index/report/settings, so
    every surface reads the one palette (D-04, plan 04-04 Task 2).
    """
    from surfaces.daemon import (
        _ensure_quiz_session,
    )

    path = handler.banks.get(stem)
    if path is None:
        handler.send_not_found(stem)
        return
    try:
        launch_mode = _quiz_launch_mode(handler)
    except ValueError as exc:
        handler.send_error(400, str(exc))
        return
    qs = load(path)
    lesson = parse_lesson(path)
    lesson_slugs = set(h["slug"] for h in lesson["headings"]) if lesson else set()
    sess = _quiz_session_config(handler, stem, launch_mode, path)
    view = teaching = None
    try:
        session_file = _ensure_quiz_session(handler, stem, path, qs, sess)
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
    if view and view.get("status") == "active" and not (flash or {}).get("interaction_result"):
        try:
            saved_feedback = session.do_check_feedback(session_file, view)
        except (OSError, ValueError, SystemExit):
            # Optional review data cannot make the current public item unusable.
            saved_feedback = None
        if saved_feedback:
            flash = dict(flash or {}, **saved_feedback)
    if view and view.get("status") == "active" and not flash:
        try:
            flash = session.do_pending_feedback(session_file, view)
        except (OSError, ValueError, SystemExit):
            # Optional saved status never makes the public question unusable.
            pass
    _send_quiz_page(handler, stem, path, qs, sess, view, teaching, lesson_slugs,
                    flash, prefill=(flash or {}).get("prefill"),
                    launch_mode=launch_mode)


def _quiz_launch_mode(handler):
    """The optional allowlisted course-area launch mode in the request URL."""
    values = urllib.parse.parse_qs(
        urllib.parse.urlsplit(handler.path).query).get("mode", [])
    if not values:
        return None
    if len(values) != 1 or values[0] not in ("practice", "exam"):
        raise ValueError("quiz mode must be practice or exam")
    return values[0]


def _quiz_session_config(handler, stem, launch_mode=None, bank_path=None):
    """Return a mode-specific runtime configuration without mutating another.

    The ordinary bank route keeps its established per-stem configuration.
    Explicit course-area launches get a process-persistent slot keyed by bank
    and mode, so Practice and Test cannot reuse or rewrite one another's
    sitting. The runtime session file remains the authority for the mode.
    """
    base = handler.sessions.get(stem)
    if base is None:
        raise ValueError("quiz session configuration is unavailable")
    params = urllib.parse.parse_qs(urllib.parse.urlsplit(handler.path).query)
    requested = params.get("session", [])
    course_ids = params.get("course", [])
    if len(requested) > 1 or len(course_ids) > 1:
        raise ValueError("quiz context is ambiguous")
    requested_id = requested[0] if requested else None
    course_id = course_ids[0] if course_ids else None
    if requested_id and (not launch_mode or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", requested_id)):
        raise ValueError("saved session needs one valid course mode")
    if course_id:
        course_dir = ia.course_dir_for(handler.root, course_id)
        if not course_dir or not bank_path or os.path.commonpath(
                [os.path.realpath(course_dir), os.path.realpath(bank_path)]) != os.path.realpath(course_dir):
            raise ValueError("quiz does not belong to this course")
    if launch_mode is None:
        return base
    store = handler.quiz_mode_sessions
    key = (stem, launch_mode, requested_id)
    if (key not in store or
            (bank_path is not None and
             store[key].get("_bank_path") != os.path.abspath(bank_path))):
        cfg = dict(base)
        cfg.pop("api_session_id", None)
        cfg["session_id"] = uuid.uuid4().hex
        cfg["mode"] = launch_mode
        cfg["selection_mode"] = launch_mode
        cfg["seed"] = 0
        cfg["mode_specific"] = True
        cfg["requested_session_id"] = requested_id
        cfg["course_id"] = course_id
        cfg["_bank_path"] = (os.path.abspath(bank_path)
                             if bank_path is not None else None)
        store[key] = cfg
    return store[key]


def _send_quiz_page(handler, stem, path, qs, sess, view, teaching, lesson_slugs,
                    flash=None, prefill=None, status=200, launch_mode=None):
    """Render and send `GET /quiz/<stem>`'s page for the state it is in.

    Shared with the POST failure paths (plan item 2, 2026-08-24): a submit
    that does not go through comes back as this page with a fresh token and
    the learner's own answer echoed into the controls, instead of the bare
    error document that ate a written response during the 13.9 sitting.
    """
    from surfaces.daemon import (
        _course_source_return,
        _quiz_path,
    )

    tokens = (dict((kind, _mint_quiz_token(handler, view, kind))
                   for kind in ("submit", "hint", "stumped")) if view else None)
    cfg = settings.load_settings(handler.root)
    theme_block = theme.theme_css(cfg)
    profile, _notice = settings.resolve_presentation_profile(cfg)
    session_id = sess.get('requested_session_id')
    course_id = sess.get('course_id')
    source_return = _course_source_return(handler, course_id)
    return_source = source_return["source_id"] if source_return else None
    return_path = _quiz_path(stem, launch_mode, session_id=session_id,
                             course_id=course_id, return_source=return_source)
    lesson_base = "/lesson/%s" % stem
    if source_return and session_id:
        lesson_base += "?" + urllib.parse.urlencode({
            "course": course_id, "return_source": return_source,
            "return": return_path})
    _, page = quiz.page_for(path, qs, serve=True, reveal=False,
                            post_path=_quiz_path(stem, launch_mode, answer=True,
                                                 session_id=session_id, course_id=course_id,
                                                 return_source=return_source),
                            bank_stem=stem, mode=sess.get("mode", "practice"),
                            lesson_base=lesson_base,
                            lesson_slugs=lesson_slugs, theme_css=theme_block,
                            assist=True,
                            home_href=(source_return["href"] if source_return else
                                       "/course/%s" % course_id if course_id else "/"),
                            presentation_profile=profile,
                            symbol_return=return_path,
                            home_label=source_return["label"] if source_return else "")
    # A form POST records and moves the runtime cursor before its PRG redirect.
    # Show the just-answered public item and runtime-issued verdict first. The
    # Continue link then renders the live cursor without replaying the answer.
    rendered_view = view
    continue_href = None
    continue_label = None
    if isinstance(flash, dict) and flash.get("action") in ("advance", "complete", "defer_feedback"):
        before = flash.get("before")
        if isinstance(before, dict) and before.get("item"):
            advanced = (before.get('position') != view.get('position') or
                        view.get('status') == 'complete')
            opening_reason = (flash.get('action') == 'defer_feedback'
                              and (before.get('activity') or {}).get('stage') == 'answer'
                              and (view.get('activity') or {}).get('stage') == 'reason')
            if (flash.get('action') != 'defer_feedback' or advanced) and not opening_reason:
                rendered_view = before
            if flash.get('action') == 'defer_feedback':
                flash = dict(flash, advanced=advanced)
            if advanced and view.get('status') != 'complete' and not opening_reason:
                continue_href = return_path
                try:
                    continue_label = "Next question, %d of %d" % (
                        int(view.get("position", 0) or 0) + 1,
                        int(view.get("total", 0) or 0))
                except (AttributeError, TypeError, ValueError):
                    continue_label = "Continue"
            elif view.get('status') == 'complete':
                continue_href = "/report?session=%s" % urllib.parse.quote(
                    str(before.get("session_id", "")))
                continue_label = "View summary"
    # The shared quiz shell starts with Item 1 for the client-started/offline
    # path.  Served redirects render the current public runtime view again,
    # so carry its cursor into the server-rendered context band as well.
    if rendered_view is not None:
        try:
            position = int(rendered_view.get("position", 0) or 0) + 1
        except (TypeError, ValueError):
            position = 1
        page = page.replace('<b id="pos">1</b>',
                            '<b id="pos">%d</b>' % position, 1)
        # A selected sitting may contain fewer items than its source bank.
        # The runtime view owns this denominator after selection and resume.
        page = page.replace('<b id="tot">%d</b>' % len(qs),
                            '<b id="tot">%d</b>' % view["total"], 1)
    if rendered_view is not None:
        timing = view.get("timing")
        if timing and view.get("status") == "active":
            deadline = str(timing["deadline"])
            remaining_ms = max(0, int((
                datetime.datetime.fromisoformat(deadline.replace("Z", "+00:00"))
                - datetime.datetime.fromisoformat(
                    evidence.utc_now().replace("Z", "+00:00"))
            ).total_seconds() * 1000))
            report_href = "/report?session=" + urllib.parse.quote(
                view["session_id"], safe="")
            timer_html = (
                '<style>.quiz-timer{display:flex;flex-wrap:wrap;gap:.45rem;'
                'align-items:baseline;padding:.65rem .9rem;margin:.7rem 0;'
                'border:1px solid currentColor;border-radius:.65rem}'
                '.quiz-timer strong{font-variant-numeric:tabular-nums;'
                'font-size:1.15em}</style>'
                '<p class="quiz-timer" role="timer" aria-live="off">'
                'Time left <strong id="mock-time-left">calculating</strong>'
                '<span>Closes at <time datetime="%s">%s UTC</time></span></p>'
                '<script>(function(){const end=performance.now()+%d;'
                'const target=document.getElementById("mock-time-left");'
                'function tick(){const seconds=Math.max(0,Math.ceil('
                '(end-performance.now())/1000));const minutes=Math.floor(seconds/60);'
                'target.textContent=String(minutes).padStart(2,"0")+":"+'
                'String(seconds%%60).padStart(2,"0");'
                'if(seconds===0){window.location.replace(%s);}}'
                'tick();setInterval(tick,1000);})();</script>' %
                (presentation.esc(deadline),
                 presentation.esc(deadline[:16].replace("T", " ")),
                 remaining_ms, json.dumps(report_href)))
            page = page.replace('<div id="host"></div>',
                                timer_html + '<div id="host"></div>', 1)
        symbol_help = quiz.question_symbol_help(
            path, qs, stem, serve=True,
            return_path=return_path)
        baseline = quiz_page.baseline_for(rendered_view, teaching,
                                          _quiz_path(stem, launch_mode, answer=True,
                                                     session_id=session_id,
                                                     course_id=course_id,
                                                     return_source=return_source),
                                          tokens, flash,
                                          prefill, continue_href, continue_label,
                                          symbol_help)
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


def _mint_quiz_flash(handler, before, after, result, prefill=None):
    receipt = secrets.token_urlsafe(24)
    target = ((result.get("next") or {}).get("item") or {}).get("id")
    if target is None:
        target = (after.get("item") or {}).get("id")
    with handler.quiz_state_lock:
        _prune_quiz_store(handler.quiz_flash_receipts)
        handler.quiz_flash_receipts[receipt] = {
            "session_id": before.get("session_id"), "source_item_id": (before.get("item") or {}).get("id"),
            "cursor": after.get("position"), "status": after.get("status"), "target": target,
            "result": result, "before": before,
            "expires": time.monotonic() + QUIZ_TOKEN_TTL}
        if result.get("action") == "hold" and isinstance(prefill, dict):
            # Retry controls live only in the expiring in-memory receipt.
            handler.quiz_flash_receipts[receipt]["prefill"] = dict(prefill)
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
        if rec["target"] is not None or current is not None:
            return None
    elif current not in (rec["source_item_id"], rec["target"]):
        return None
    payload = dict(rec["result"])
    payload["before"] = rec["before"]
    if rec.get("prefill") is not None:
        payload["prefill"] = rec["prefill"]
    return payload


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
        return dict((str(row.get("id", i)), one("row_%d" % i)) for i, row in enumerate(item.get("rows") or []) if one("row_%d" % i))
    if t == "build":
        blocks = item.get("blocks") if "ordering" in item else item.get("steps")
        return [one("step_%d" % i) for i, _ in enumerate(blocks or []) if one("step_%d" % i)]
    if t == "fill":
        return dict((str(field.get("id", "")), one("fill_" + str(field.get("id", ""))))
                    for field in item.get("fields") or [])
    return one("answer")


def _echo_quiz_failure(handler, stem, path, qs, session_file, fields, message,
                      status=403, sess=None, launch_mode=None):
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
    sess = sess or handler.sessions.get(stem) or {}
    lesson = parse_lesson(path)
    lesson_slugs = set(h["slug"] for h in lesson["headings"]) if lesson else set()
    try:
        view = session.do_next(session_file)
        teaching = session.do_teach(session_file)
    except Exception:
        handler.send_error(status, message)
        return
    _send_quiz_page(handler, stem, path, qs, sess, view, teaching, lesson_slugs,
                    flash={"refused": message}, prefill=fields, status=status,
                    launch_mode=launch_mode)


def handle_quiz_answer(handler, stem):
    """`POST /quiz/<stem>/answer` -- the legacy served-page answer route,
    now a compatibility wrapper over the one session adapter (06-02 Task 3):
    it resolves the API session `/api/start` created for this bank stem and
    submits through `session.do_action`, so there is exactly one scoring,
    persistence and policy path for the served browser. `cmd_serve`'s
    progress line and attempt-file regeneration are preserved through the
    scoped session config's `_refresh_attempt_view`.
    """
    from surfaces.daemon import (
        _check_refusal_body,
        _course_source_return,
        _ensure_quiz_session,
        _fill_entry_error_body,
        _quiz_path,
        _refresh_attempt_view,
        _refusal_from_exit,
        _reject_cross_origin,
        api_read_json,
        api_session_path,
    )

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
        launch_mode = _quiz_launch_mode(handler)
        sess = _quiz_session_config(handler, stem, launch_mode, path)
    except ValueError as exc:
        handler.send_error(400, str(exc))
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
            session_file = _ensure_quiz_session(handler, stem, path, qs, sess)
            before = session.do_next(session_file)
            if before.get("status") == "complete":
                handler.send_redirect("/report?session=" + urllib.parse.quote(
                    before["session_id"], safe=""))
                return
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
                    "Submit it again.", sess=sess, launch_mode=launch_mode)
                return
            q = by_id.get(expected["item_id"])
            refusal = _check_refusal_body(handler, q) if action == "submit" else None
            try:
                if refusal is not None:
                    result = refusal
                elif action == "submit":
                    submit_action = {"kind": "submit", "answer": _form_answer(before["item"], fields)}
                    if before.get("activity"):
                        for name in ("activity_id", "child_id", "submission_token"):
                            submit_action[name] = (fields.get(name) or [None])[0]
                    result = session.do_action(session_file, submit_action,
                                               confidence=None, renderer_meta=None, elapsed_ms=None)
                else:
                    result = session.do_teach(session_file, action)
            except PolynomialRefusal as exc:
                _echo_quiz_failure(handler, stem, path, qs, session_file,
                                   fields, str(exc), status=400,
                                   sess=sess, launch_mode=launch_mode)
                return
            except SystemExit as exc:
                result = _refusal_from_exit(exc.code, q)
                if result is None:
                    _echo_quiz_failure(handler, stem, path, qs, session_file,
                                       fields, str(exc.code), status=400,
                                       sess=sess, launch_mode=launch_mode)
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
                cfg = sess
                _refresh_attempt_view(cfg, cfg.get("api_session_id"), qs, path)
            after = session.do_next(session_file)
            receipt = _mint_quiz_flash(
                handler, before, after, result,
                prefill=fields if result.get("action") == "hold" else None)
            source_return = _course_source_return(handler, sess.get("course_id"))
            handler.send_redirect(_quiz_path(
                stem, launch_mode, receipt=receipt,
                session_id=sess.get("requested_session_id"),
                course_id=sess.get("course_id"),
                return_source=source_return["source_id"] if source_return else None))
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
        answer = data.get("response")
        submit_action = {"kind": "submit", "answer": answer}
        for name in ("activity_id", "child_id", "submission_token"):
            if name in data:
                submit_action[name] = data[name]
        result = session.do_action(
            session_file, submit_action,
            confidence=None, renderer_meta=None, elapsed_ms=elapsed_ms)
        try:
            pre3 = read_session(session_file)
            legacy_mode = pre3.get("mode")
        except Exception:
            legacy_mode = None
        if result.get("action") in ("advance", "complete") and q is not None:
            # The rebuild applies the reveal policy, and for a check item it
            # must carry the one run's per-case result (05-05 Task 1) or the
            # actual output would be dropped from the page's explanation.
            result["explain"] = explain_payload(
                q, bool(sess.get("reveal")),
                run_result=result.get("run_result"))
        _refresh_attempt_view(sess, api_id, qs, path)
        payload = submission_feedback(result, legacy_mode)
    except SystemExit as exc:
        body = _refusal_from_exit(exc.code, q)
        if body is None:
            body = _fill_entry_error_body(exc.code, q, answer)
        if body is not None:
            handler.send_json(body)
        else:
            handler.send_error(400, str(exc.code))
        return
    except PolynomialRefusal as exc:
        handler.send_json({"entry_error": str(exc), "entry_state": exc.state})
        return
    except Exception as exc:                    # never let a bad POST kill the daemon
        handler.send_server_error(exc)
        return
    handler.send_json(payload)

