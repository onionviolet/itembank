"""Day routes; daemon-owned helpers are imported at request time."""
from model import load
from model import parse_lesson
from runtime import assessment_feedback_released
from runtime import read_session
from surfaces import day
from surfaces import ia
from surfaces import lesson
from surfaces import presentation
from surfaces import retention_view
from surfaces import session
from surfaces import settings
from surfaces import study
from surfaces import theme
import datetime
import evidence
import hashlib
import html
import json
import os
import retention
import secrets
import urllib.parse
import urllib.request


def _report_figure(field, value, label):
    """One labelled figure (`data-field` names which of `session_summary()`'s
    three top-level counts it carries) -- a stable marker
    `check_api_cli_parity`-style page-versus-command tests can regex against
    instead of scraping prose that copywriting could change later.
    """
    shown = 'Withheld until completion' if value is None else str(value)
    return ('<div class="figure" data-field="%s"><div class="figure-value">%s</div>'
            '<div class="figure-label">%s</div></div>'
            % (field, html.escape(shown), html.escape(label)))


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
            "<tr><td>%s</td><td>%d</td><td>%s</td><td>%d</td></tr>"
            % (html.escape(name), bucket["attempts"],
               "Withheld until completion" if bucket["correct"] is None
               else str(bucket["correct"]), bucket["pending"]))
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
    pct = round(correct / attempts * 100) if correct is not None and attempts else 0
    headline = ("Withheld until completion" if correct is None
                else "%d%%" % pct)
    headline_label = ("auto-marked result" if correct is None
                      else "auto-marked accuracy")
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
                   'still need human review. Auto-graded totals exclude them. '
                   'Reopen this report after a reviewer records the marks.</p>')
    rows = _report_objective_rows(summary["objectives"])
    return (
        '<div class="card" data-status="%s">'
        '<div class="headline" data-field="pct">%s</div>'
        '<p class="headline-label">%s</p>'
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
        % (html.escape(status), html.escape(headline), headline_label,
           progress, partial, figures, rows))


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
    from surfaces.daemon import (
        REPORT_EMPTY,
        REPORT_FAILURE_COPY,
        api_session_path,
    )

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
            from runtime import learner_evidence
            from surfaces.home import feedback_sessions
            events = learner_evidence(events, feedback_sessions(handler.root))
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
            back={"href": "/", "label": "itembank"}, palette=True)
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
    cfg = settings.load_settings(handler.root)
    theme_block = theme.theme_css(cfg)
    profile, _notice = settings.resolve_presentation_profile(cfg)
    if summary["auto_attempts"] == 0 and summary["pending_manual"] == 0:
        body = ("<div class=\"empty\"><h2>No answers were submitted before "
                "time ran out.</h2><p>Return to the course Test area to start "
                "another mock sitting.</p></div>"
                if result.get("timed_out") else REPORT_EMPTY)
    else:
        position = total = None
        if status == "active":
            # Position/total come from the session's own cursor and item
            # count -- the same session data `session_summary()` was itself
            # computed from -- never recomputed from the responses list.
            data = read_session(path)
            position, total = data["cursor"], len(data["items"])
        body = _report_card(summary, status, position, total)
    if result.get("timed_out"):
        body = ('<p class="status" role="status">Time is up. %d item%s '
                'went unanswered. Accuracy below counts only submitted '
                'auto-marked answers.</p>' %
                (result["unanswered"],
                 "" if result["unanswered"] == 1 else "s")) + body
    # The gate outcome split (06.2-UI-SPEC section 11, GATE-06): the
    # report-surface readout, derived from the evidence log at request
    # time -- never stored, and never rendered in the reading column.
    # The lesson's declared check->mode map is what marks a pair as a
    # required gate (a recommended gate is excluded by construction).
    data = read_session(path)
    bank_path = data.get("bank")
    gate_html = ""
    if bank_path and os.path.exists(bank_path) and assessment_feedback_released(
            data.get('mode'), data):
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
    report_back = {"href": "/", "label": "itembank"}
    try:
        matches = []
        bank_real = os.path.realpath(bank_path) if bank_path else None
        for card in ia.course_shelf_state(handler.root).get('cards', []):
            if card.get('degraded') or not card.get('available'):
                continue
            if any(row.get('session_id') == session_id and
                   os.path.realpath(row.get('bank', '')) == bank_real
                   for row in card.get('resume', {}).get('sessions', ())):
                matches.append(card)
        if len(matches) == 1:
            report_back = {"href": "/course/" + matches[0]['course_id'],
                           "label": "Back to course"}
    except Exception:
        pass
    page = presentation.surface_shell(
        "itembank report", body + gate_html, theme_css=theme_block,
        back=report_back)
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
    from surfaces.daemon import (
        DAY_AMBIGUOUS_BODY,
    )

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
    from surfaces.daemon import (
        _reject_cross_origin_write,
    )

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
    from surfaces.daemon import (
        _reject_cross_origin_write,
    )

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


def handle_day_task(handler, stem):
    """Update one server-resolved assignment row through its owner adapter."""
    from surfaces.daemon import (
        _reject_cross_origin_write,
    )

    if _reject_cross_origin_write(handler):
        return
    if stem not in handler.plans:
        handler.send_not_found(stem)
        return
    try:
        result = day.apply_task_post(_plan_day_state(handler, stem),
                                     handler.read_json())
    except Exception as exc:
        handler.send_server_error(exc)
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
    from surfaces.daemon import (
        DAY_EDIT_ALLOWED_FIELDS,
        _reject_cross_origin_write,
    )

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

