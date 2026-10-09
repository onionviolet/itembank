"""Pages routes; daemon-owned helpers are imported at request time."""
from model import parse_key_blocks
from model import parse_lesson
from surfaces import home
from surfaces import ia
from surfaces import lesson
from surfaces import looks
from surfaces import palette
from surfaces import presentation
from surfaces import settings
from surfaces import theme
from surfaces import update
import html
import json
import os
import sample_course


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
        back={"href": "/courses", "label": "Back to courses"}).encode("utf-8"))


def handle_palette(handler):
    """`GET /palette` -- the command palette's index, as JSON.

    Built from the shipped surfaces on every request rather than cached: the
    bank scan, the course shelf and the parser are the same three sources the
    rest of the daemon reads, and a palette that answered from a snapshot
    would offer a course that had been removed. It performs no write and
    reaches nothing a GET does not already reach.
    """
    from surfaces.daemon import (
        _refresh_discovery,
    )

    _refresh_discovery(handler)
    cfg = settings.load_settings(handler.root)
    handler.send_bytes(
        palette.palette_json(handler.root, handler.banks,
                             selected_look=looks.resolve(cfg.get("look")))
        .encode("utf-8"),
        "application/json; charset=utf-8")


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
    from surfaces.daemon import (
        session_index,
    )

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


def _desk_loose_banks(banks, cards):
    """Bank stems whose file sits outside every course directory on the shelf.

    Once a course exists the desk replaces the old stem list, so a bank a
    learner or agent drops into the workspace had no visible route except
    `/banks`. Membership is by resolved path only; nothing is parsed here.
    """
    course_dirs = [os.path.realpath(card["path"]) for card in cards
                   if card.get("path")]
    loose = []
    for stem in sorted(banks or {}, key=str.lower):
        path = os.path.realpath(banks[stem])
        if not any(path.startswith(folder.rstrip(os.sep) + os.sep)
                   for folder in course_dirs):
            loose.append(stem)
    return loose


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
    from surfaces.daemon import (
        EMPTY_STATE,
        SHELF_NOSCRIPT,
        SHELF_SCRIPT,
        _course_shelf_body,
        _refresh_discovery,
    )

    _refresh_discovery(handler)
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
        profile, _notice = settings.resolve_presentation_profile(cfg)
        handler.send_html(presentation.surface_shell(
            "Your desk",
            _course_shelf_body(shelf, ia.walkthrough_state(handler.root),
                               sample, loose_banks=_desk_loose_banks(
                                   banks, shelf["cards"])),
            theme_css=theme_block,
            noscript=SHELF_NOSCRIPT, tail=SHELF_SCRIPT,
            palette=True, presentation_profile=profile).encode("utf-8"))
        return
    if not banks and not plans:
        served_dir = html.escape(os.path.abspath(handler.root))
        body = EMPTY_STATE.replace("__DIR__", served_dir)
    else:
        mode, note = home.resolve_mode(
            cfg.get("home") if isinstance(cfg, dict) else None)
        state = home.build_state(handler.root, banks, plans,
                                 handler.collisions)
        profile, _notice = settings.resolve_presentation_profile(cfg)
        body = home.render_home(state, mode, note=note,
                                presentation_profile=profile)
    profile, _notice = settings.resolve_presentation_profile(cfg)
    page = presentation.surface_shell(
        "itembank", body,
        theme_css=theme_block + home.HOME_CSS, palette=True,
        presentation_profile=profile)
    handler.send_html(page.encode("utf-8"))


def handle_banks(handler):
    """`GET /banks` -- the file list that used to be `GET /`: every bank
    and day-plan stem this daemon found at startup, plus the labelled
    warning naming any files it could not serve because another file
    shares their stem. The home links here instead of duplicating the
    list, because this is the only view that shows a collision."""
    from surfaces.daemon import (
        BANK_ROW,
        EMPTY_STATE,
        PLAN_ROW,
        _refresh_discovery,
    )

    banks, plans, _collisions = _refresh_discovery(handler)
    cfg = settings.load_settings(handler.root)
    theme_block = theme.theme_css(cfg)
    profile, _notice = settings.resolve_presentation_profile(cfg)
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


def handle_key_review(handler, key_id):
    """`POST /key/<id>/review` -- add a [!KEY] card to review. The key id is
    resolved against the daemon's scanned banks' parsed key blocks (never
    joined to a filesystem path), the existing loopback authority gate
    applies, and a `key_review` event is recorded through the one evidence
    writer (D-19, T-031-11). The status region announces `Added to review.`
    once -- no streak, no count-up, no celebration (C17)."""
    from surfaces.daemon import (
        _reject_cross_origin,
    )

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

