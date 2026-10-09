"""JSON API routes; daemon-owned helpers are imported at request time."""
from model import lesson_slug
from model import load
from model import parse_lesson
from runtime import PolynomialRefusal
from runtime import explain_payload
from runtime import read_session
from runtime import submission_feedback
from surfaces import audio as audio_surface
from surfaces import course_ops
from surfaces import evidence_cli
from surfaces import ia
from surfaces import lesson
from surfaces import session
from surfaces import settings
import evidence
import json
import os
import retention
import runner
import selection
import source_adapters
import subjects
import uuid


def handle_api_shelf(handler):
    """`POST /api/shelf` -- the one mutating route Phase 16B adds.

    First-run actions keep their action-only body. ``reorder_courses`` carries
    only the ordered stable ids and the expected workspace fingerprint. The
    server resolves paths and members from the current shelf, never from the
    request. Loopback-only and same-origin, like every other mutating route.
    """
    from surfaces.daemon import (
        SHELF_ACTION_ALLOWED_FIELDS,
        SHELF_REORDER_ALLOWED_FIELDS,
        _reject_cross_origin_write,
        api_read_json,
    )

    if _reject_cross_origin_write(handler):
        return
    data, failed = api_read_json(handler)
    if failed:
        return
    action = data.get("action")
    allowed = (SHELF_REORDER_ALLOWED_FIELDS
               if action == ia.SHELF_REORDER_ACTION
               else SHELF_ACTION_ALLOWED_FIELDS)
    extra = sorted(k for k in data if k not in allowed)
    if extra:
        handler.send_error(400, "body may carry only: %s"
                                % ", ".join(allowed))
        return
    if action not in ia.SHELF_ACTIONS:
        handler.send_error(400, "action must be one of %s"
                                % "|".join(ia.SHELF_ACTIONS))
        return
    if action == ia.SHELF_REORDER_ACTION:
        if set(data) != set(SHELF_REORDER_ALLOWED_FIELDS):
            handler.send_error(
                400, "reorder_courses requires course_ids and expected_fingerprint")
            return
        try:
            result = ia.reorder_shelf(
                handler.root, data.get("course_ids"),
                data.get("expected_fingerprint"))
        except Exception as exc:
            code = getattr(exc, "code", "workspace.invalid_order")
            status = 409 if code in (
                "workspace.conflict", "workspace.stale_preflight",
                "workspace.stale_courses", "journal.conflict",
                "journal.stale_preflight") else 400
            handler.send_error(status, "%s: %s" % (code, str(exc)))
            return
        handler.send_json(result)
        return
    handler.send_bytes(
        json.dumps(ia.apply_shelf_action(handler.root, action)).encode("utf-8"),
        "application/json")


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
    from surfaces.daemon import (
        SOURCE_IMPORT_ALLOWED_FIELDS,
        _reject_cross_origin_write,
        api_read_json,
    )

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
    from surfaces.daemon import (
        SOURCE_RECHECK_ALLOWED_FIELDS,
        _reject_cross_origin,
        api_read_json,
    )

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
    from surfaces.daemon import (
        SESSION_MODES,
        _reject_cross_origin,
        api_read_json,
    )

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
    type_counts = data.get("type_counts")
    if type_counts is not None and not isinstance(type_counts, dict):
        handler.send_error(400, "type_counts must map item types to counts")
        return
    count = data.get("count", sum(type_counts.values()) if type_counts and all(
        isinstance(value, int) and not isinstance(value, bool)
        for value in type_counts.values()) else 10)
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
    if type_counts is not None:
        spec["type_counts"] = type_counts
    minutes = data.get("time_limit_minutes")
    if minutes is not None and data.get("preview") is True:
        handler.send_error(400, "a selection preview has no time limit")
        return
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
                                      profile_id=profile_id,
                                      time_limit_minutes=minutes)
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
    from surfaces.daemon import (
        SESSION_MODES,
        _reject_cross_origin,
        api_read_json,
    )

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
    from surfaces.daemon import (
        _reject_cross_origin,
        api_read_json,
    )

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
    from surfaces.daemon import (
        _reject_cross_origin,
        api_read_json,
        api_session_path,
    )

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
    from surfaces.daemon import (
        API_ACTION_FORBIDDEN_FIELDS,
        CONFIDENCE_LEVELS,
        RENDERER_META_MAX_BYTES,
        _check_refusal_body,
        _fill_entry_error_body,
        _refresh_attempt_view,
        _refusal_from_exit,
        _reject_cross_origin,
        api_read_json,
        api_reject_path_fields,
        api_session_path,
    )

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
        submit_action = {"kind": "submit", "answer": answer}
        binding_source = action if action is not None else data
        for name in ("activity_id", "child_id", "submission_token"):
            if action is not None and name in data and name in action:
                handler.send_error(400, "%s given both top-level and inside action" % name)
                return
            if name in binding_source:
                submit_action[name] = binding_source[name]
        result = session.do_action(
            path, submit_action,
            confidence=confidence, renderer_meta=renderer_meta)
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
    result = submission_feedback(result, mode)
    if cfg is not None and result.get("accepted") and qs:
        _refresh_attempt_view(cfg, session_id, qs, bank_path)
    handler.send_json(result)


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
    from surfaces.daemon import (
        LESSON_RUN_FIELDS,
        LESSON_RUN_FORBIDDEN,
        LESSON_SOURCE_MAX_BYTES,
        _reject_cross_origin,
        api_read_json,
        api_session_path,
        execution_refusal,
    )

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
    from surfaces.daemon import (
        _reject_cross_origin,
        api_read_json,
        api_session_path,
    )

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


def _teach_reject_authority(handler, obj, where):
    """Refuse an authority-shaped field on `/api/teach` BY NAME, before any
    policy work. `API_ACTION_FORBIDDEN_FIELDS` names `tier` explicitly, which
    is the single field this route exists to keep out of a client's hands.
    Returns True when a response has already been sent.
    """
    from surfaces.daemon import (
        API_ACTION_FORBIDDEN_FIELDS,
    )

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
    from surfaces.daemon import (
        TEACH_ACTION_FIELDS,
        TEACH_BODY_FIELDS,
        _reject_cross_origin,
        api_read_json,
        api_reject_path_fields,
        api_session_path,
    )

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
    from surfaces.daemon import (
        _reject_cross_origin,
        api_read_json,
        api_session_path,
    )

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
    from surfaces.daemon import (
        _reject_cross_origin,
        api_read_json,
        api_session_path,
    )

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


def handle_api_course_create(handler):
    """`POST /api/course/create` -- mint a course.

    The browser twin of `itembank course create`, and the cell the
    2026-09-05 surface grid named first: "a course is created by calling
    course.create_course from Python. Neither a person nor an agent client
    can start a course from a surface." Reaches `course.create_course`,
    which is `journal.commit_operation` as a mint, and writes nothing else.
    """
    from surfaces.daemon import _course_operation

    _course_operation(handler, "create")


def handle_api_course_register_source(handler):
    """Register one bounded local source through the journal mint path."""
    from surfaces.daemon import _course_operation

    _course_operation(handler, "register_source")


def handle_api_course_rename(handler):
    """`POST /api/course/rename` -- retitle a course.

    `course / change` on the same grid. One `edit_in_place` through
    `course.write_course`: the title is display, so identity, bindings and
    evidence are untouched, and a caller that states an
    `expected_fingerprint` gets the real compare-and-swap refusal by name
    rather than a last-writer-wins overwrite.
    """
    from surfaces.daemon import _course_operation

    _course_operation(handler, "rename")


def handle_api_course_add_source(handler):
    """`POST /api/course/add-source` -- record a source in a course sidecar.

    The step between importing a source and binding it, and the one function
    in the source-binding family that had no door at all: the journal
    registry held the object and the course's own Sources section was written
    by `graph.add_source`, which nothing called. A source that a course
    cannot name is a source its package manifest, its Sources area and its
    `bind list` cannot see.

    It consumes no right, because naming a file is not using it. The
    response reports the source's seven rights anyway, so a client learns in
    the same breath that the row exists and that binding it still refuses
    until `read` is granted.
    """
    from surfaces.daemon import _course_operation

    _course_operation(handler, "add_source")


def handle_api_course_bind_treatment(handler):
    """`POST /api/course/bind-treatment` -- choose HOW an objective is taught.

    The treatment family's own write, and a typing of what `POST
    /api/course/bind` already did rather than a second writer: both reach
    `course.bind_treatment` and write the identical row. What this route has
    that the other cannot is a required `treatment`. The published node is
    the generated MCP tool signature and `schema_validate` has no
    `if`/`then`, so on the `bind` node `treatment` has to stay optional while
    the runtime insists on it, and a tool that advertises an optional field
    the runtime requires fails at call time rather than at type time.

    The right consumed is the treatment's, not the caller's to name: an
    excerpt refuses on `quote`, a guided lesson on `transform`, and a direct
    reading needs only `read`. It is read from the journal registry at the
    moment of the write, so a revoked grant takes effect on the next binding
    rather than staying effective behind a stale snapshot.
    """
    from surfaces.daemon import _course_operation

    _course_operation(handler, "bind_treatment")


def handle_api_course_treatments(handler):
    """`POST /api/course/treatments` -- which of the eleven treatments this
    source's rights actually allow, and why.

    A READ, so it is gated by the read-side check. It is the first reader
    `graph.TREATMENT_RIGHTS` has ever had, which was the treatment family's
    real gap: the eleven-kind mapping decides which treatments a course may
    use for a given source, and until this route existed the only way to
    learn it was to attempt a binding and be refused. A learner who had
    granted `read` and not `transform` could bind a direct reading and not a
    guided lesson, and no surface said so first.

    It reports and never grants. A `transform` that reads `unknown` comes
    back refusing, because unknown is restrictive and finding a file never
    granted permission to use it; the way to change the answer is to record
    the right, which is a different operation with a different authority
    behind it.
    """
    from surfaces.daemon import _course_operation

    _course_operation(handler, "treatments")


def handle_api_course_autonomy(handler):
    """`POST /api/course/autonomy` -- what this installation permits an agent
    operation to do.

    A READ, gated by the read-side check. `director.autonomy_level` and
    `director.authorize_write` had no reader on any surface, so the only way
    to learn the configured authority was to declare a level and be refused.
    All three levels are dry-run, so the answer is the shape of what is open
    rather than a yes or a no, and the binding cap comes back beside the
    level because raising the level alone still writes nothing.

    It grants nothing, and there is deliberately no route in this namespace
    that could: raising the authority is a person editing
    `settings.agent_policy`, which is the whole of AGENT-02's protection
    against an agent expanding its own authority.
    """
    from surfaces.daemon import _course_operation

    _course_operation(handler, "autonomy")


def handle_api_course_begin_operation(handler):
    """`POST /api/course/begin-operation` -- declare intent before acting.

    Step one of the thirteen-step operation protocol and the only record
    written before the attempt, so an operation that crashes after this entry
    and before any other is legible as one that declared and then stopped.
    Writes one journal entry and no course file.

    The declared autonomy is not checked here on purpose. Declaring an
    intention is not exercising it; `authorize_write` runs in whichever write
    follows, and the declaration is exactly the thing worth having on disk
    when that answer turns out to be no.
    """
    from surfaces.daemon import _course_operation

    _course_operation(handler, "begin_operation")


def handle_api_course_replay(handler):
    """`POST /api/course/replay` -- replay one operation against the protocol,
    and say where an interrupted one resumes.

    A READ. It reads the journal and nothing else, which is RELIABILITY-02's
    claim made checkable: an operation resumes because its history is on
    disk, not because a conversation is still open, so this takes an
    operation id and no in-memory operation can be handed to it.

    It is also the first reader the egress record has ever had. Every phase
    that reached a backend wrote down what left this machine, to whom, how
    many bytes, and what was deliberately held back and why, and no surface
    showed any of it. `left_this_machine` is that list, narrowed to the
    phases whose destination was not local.
    """
    from surfaces.daemon import _course_operation

    _course_operation(handler, "replay")


def handle_api_course_reverse_operation(handler):
    """`POST /api/course/reverse-operation` -- undo an operation's writes.

    Reaches `journal.undo` through `director.reverse_operation` and adds no
    restore path of its own, because a second way to put bytes back would
    make the old-or-new guarantee depend on two implementations agreeing
    about what the old state was. Entries that wrote no bytes are skipped and
    reported as skipped, so a reversal that restored nothing reads as an
    operation that had written nothing.
    """
    from surfaces.daemon import _course_operation

    _course_operation(handler, "reverse_operation")


def handle_api_course_recommend(handler):
    """`POST /api/course/recommend` -- ask a backend to recommend a treatment
    for one objective.

    Writes journal entries and no course file: the recommendation comes back
    as a validated record for a reviewer, and binding it is a separate route
    with its own live rights gate, because a recommendation that could bind
    itself would be a model choosing what its own output authorizes.

    A backend that is absent, disabled, or times out is an expected state and
    comes back `unavailable` with its typed adapter code rather than as a
    500: the objective stays untreated and the core loop is unaffected, which
    is the degrade-never-block rule at this route. Only the spans the
    objective's bound sources actually grant are sent, capped and disclosed
    in the journal's egress record, and no code path here can put learner
    evidence in a payload.
    """
    from surfaces.daemon import _course_operation

    _course_operation(handler, "recommend")


def handle_api_course_recommend_pass(handler):
    """`POST /api/course/recommend-pass` -- one pass over many objectives.

    One entry per objective, in the order given, each carrying one of three
    outcomes, and no objective skipped: a pass whose gaps were invisible is
    the failure this surface exists to prevent. The authority check runs once
    before the first objective, so an over-declaring pass is refused before
    any binding lands rather than after the first one already has.
    """
    from surfaces.daemon import _course_operation

    _course_operation(handler, "recommend_pass")


def handle_api_course_apply_recommendation(handler):
    """`POST /api/course/apply-recommendation` -- bind an accepted
    recommendation, or refuse it against the live rights.

    The state written is `director.classify_coverage`'s and never the
    provider's: a model asserting its own coverage is the self-certification
    AGENT-02 forbids, so the provider's value is kept beside the computed one
    as history. And no rights value travels in the request, so there is no
    parameter through which a stale grant could authorize this write; the
    right the treatment consumes is read from the registry at the moment of
    the bind. A refusal is journaled like a success, because dropping it
    would make the journal a log of successes.
    """
    from surfaces.daemon import _course_operation

    _course_operation(handler, "apply_recommendation")


def handle_api_course_bindings(handler):
    """`POST /api/course/bindings` -- read every binding, with its effective
    reading.

    The family's one read, and the answer to `source binding / explain` on
    the surface grid: a binding carried a state, a confidence and a rights
    snapshot, and no surface read any of them back. Each row comes back
    through `graph.validate_binding`, so a state this build cannot read
    degrades to unknown and never to covered, and the right the binding
    consumes is re-read through `course.rights_for_binding` and reported
    beside the snapshot the row stored.

    That pair is the point. A snapshot saying `granted` after the grant was
    revoked is history, and a coverage claim resting on it cannot notice by
    itself. This route names the divergence; it never acts on it, because
    the decision is the learner's and the enforcement is the next write's.
    """
    from surfaces.daemon import _course_operation

    _course_operation(handler, "bindings")


def handle_api_course_add_container(handler):
    """`POST /api/course/add-container` -- add one structural container.

    Adds zero edges. Where a container sits in the outline is structure, and
    structure is not a prerequisite claim (GRAPH-01): a course whose week 2
    follows week 1 has said nothing about what must be learned first, and a
    surface that inferred otherwise would end up gating a learner on a guess.
    """
    from surfaces.daemon import _course_operation

    _course_operation(handler, "add_container")


def handle_api_course_add_objective(handler):
    """`POST /api/course/add-objective` -- add one objective.

    `objective / create` on the surface grid, which read "objectives are
    authored by hand into objectives.md and the sidecar; no surface adds
    one". Always recorded with origin `local`: the node carries no origin
    field, so no client can claim `imported` and make a hand-authored row
    un-editable for a reason that was never true.
    """
    from surfaces.daemon import _course_operation

    _course_operation(handler, "add_objective")


def handle_api_course_add_edge(handler):
    """`POST /api/course/add-edge` -- record one relation.

    The three refusals belong to `graph.add_edge`: a self edge, a duplicate
    (source, edge_type, target) key, and an endpoint the graph does not hold.
    A prerequisite that points backwards through the authored order is NOT a
    refusal; it is recorded and returned as a warning, because the authored
    order is the human's and this daemon does not reorder it.
    """
    from surfaces.daemon import _course_operation

    _course_operation(handler, "add_edge")


def handle_api_course_structure(handler):
    """`POST /api/course/structure` -- read the outline, the edges, and the
    warnings the authored order earns.

    The second READ under this namespace, so it is gated by the read-side
    check. `graph.validate_edge` gives each edge its effective reading, and
    an edge type this build cannot read comes back downgraded to advisory
    with the original kept beside it: a relation a human wrote down is
    evidence about the course even when this build cannot act on it, and
    nothing degraded can ever reach `hard-gate`.
    """
    from surfaces.daemon import _course_operation

    _course_operation(handler, "structure")


def handle_api_course_rename_objective(handler):
    """`POST /api/course/rename-objective` -- restate an objective as a
    reviewed proposal.

    `objective / change` on the grid. A new row plus a migration relation,
    never an edit to the original, because the identity the learner's
    evidence was recorded against has to stay in the file or that evidence
    stops naming anything. The migration is recorded `proposed`; settling it
    is plan 19A-07's family.
    """
    from surfaces.daemon import _course_operation

    _course_operation(handler, "rename_objective")


def handle_api_course_split_objective(handler):
    """`POST /api/course/split-objective` -- split one objective into
    several, as a reviewed proposal. Adds rows and deletes none."""
    from surfaces.daemon import _course_operation

    _course_operation(handler, "split_objective")


def handle_api_course_merge_objectives(handler):
    """`POST /api/course/merge-objectives` -- merge several objectives into
    one, as a reviewed proposal. Every merged-from row stays in the file."""
    from surfaces.daemon import _course_operation

    _course_operation(handler, "merge_objectives")


def handle_api_course_overlay_objective(handler):
    """`POST /api/course/overlay-objective` -- record a local revision of an
    imported objective as a sibling row.

    The way GRAPH-01's immutable imported scope stays immutable AND revisable
    at once: no code path here opens the imported row for writing, and the
    revision is joined to it by an `overlays` reference and a migration.
    """
    from surfaces.daemon import _course_operation

    _course_operation(handler, "overlay_objective")


def handle_api_course_accept_migration(handler):
    from surfaces.daemon import _course_operation

    _course_operation(handler, "accept_migration")


def handle_api_course_reject_migration(handler):
    from surfaces.daemon import _course_operation

    _course_operation(handler, "reject_migration")


def handle_api_course_bind_blueprint(handler):
    from surfaces.daemon import _course_operation

    _course_operation(handler, "bind_blueprint")


def handle_api_course_blueprint_gate(handler):
    from surfaces.daemon import _course_operation

    _course_operation(handler, "blueprint_gate")


def handle_api_course_audit(handler):
    from surfaces.daemon import _course_operation

    _course_operation(handler, "audit")


def handle_api_course_staleness(handler):
    from surfaces.daemon import _course_operation

    _course_operation(handler, "staleness")


def handle_api_course_export_package(handler):
    from surfaces.daemon import _course_operation

    _course_operation(handler, "export_package")


def handle_api_course_verify_package(handler):
    from surfaces.daemon import _course_operation

    _course_operation(handler, "verify_package")


def handle_api_course_restore_package(handler):
    from surfaces.daemon import _course_operation

    _course_operation(handler, "restore_package")


def handle_api_course_package_losses(handler):
    from surfaces.daemon import _course_operation

    _course_operation(handler, "package_losses")


def handle_api_course_agent_operation(handler):
    """One token-gated lifecycle route. The closed request document admits
    identities and review decisions, never proposal bytes or authority."""
    from surfaces.daemon import _course_operation

    _course_operation(handler, "agent_operation")


def handle_api_bind(handler):
    """`POST /api/bind` -- bind a source or a treatment to an objective.

    The browser twin of `itembank bind source` and `itembank bind
    treatment`, and the first write route under a course. The surface grid
    measured this cell as empty and called it the central act of building a
    course: `course.bind_source` has been implemented, rights-gated and
    journaled since 14B, and until now the only way to call it was to import
    Python.

    This composes no authority of its own. The rights gate is
    `course._require_right`, which refuses unless the right the treatment
    consumes is exactly granted and names the one edit that fixes it; the
    vocabularies are `graph`'s closed ones; the write is
    `course.write_course`'s compare-and-swap against the sidecar's own
    fingerprint. A refusal comes back as its code and its sentence, because
    "you may not build a course out of this file yet" is the answer, not an
    error to hide.

    Since 19A-02 the body is validated against
    `schemas/course_operation.schema.json#/$defs/bind` before a file is read,
    so a state outside the vocabulary is refused by the published document
    rather than by a hand-written check three calls later, and the response
    envelope is unchanged.
    """
    from surfaces.daemon import _course_operation

    _course_operation(handler, "bind", envelope=("bound", "binding"))


def handle_api_rights(handler):
    """`POST /api/rights` -- record what may be done with one source.

    The browser twin of `itembank bind rights`. A learner's declaration
    about their own file, written through `journal.op_grant_rights`, which
    touches no bytes and refuses a name or value outside the closed
    vocabularies. It is the same act `source import --grant` performs at link
    time; having it only at link time meant a source bound before the
    decision was made could never be used, which is the dead end this route
    removes.

    `denied` is recorded by the same call, because a decision not to use
    something is as much a decision as its opposite.

    Since 19A-02 the seven right names and their three states are the
    published `grants` node rather than a check in this handler, so an
    unrecognised right is refused by the same document the CLI and the MCP
    tool signature read, and the response envelope is unchanged.
    """
    from surfaces.daemon import _course_operation

    _course_operation(handler, "rights", envelope=("recorded", "source"))


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
    from surfaces.daemon import (
        _reject_cross_origin,
        api_read_json,
        api_session_path,
    )

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
    from surfaces.daemon import (
        _reject_cross_origin,
        api_read_json,
        api_session_path,
    )

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
    from surfaces.daemon import (
        _reject_cross_origin,
        api_read_json,
    )

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


def handle_api_course_create_reading(handler):
    """Journal an accepted reading graph operation."""
    from surfaces.daemon import _course_operation

    _course_operation(handler, "create_reading")


def handle_api_course_confirm_reading(handler):
    """Record an explicit learner confirmation."""
    from surfaces.daemon import _course_operation

    _course_operation(handler, "confirm_reading")


def handle_api_course_declare_reading(handler):
    """Persist or replay a confirmed scoreless declaration."""
    from surfaces.daemon import _course_operation

    _course_operation(handler, "declare_reading")


def handle_api_course_revise_reading(handler):
    """Journal an accepted reading graph operation."""
    from surfaces.daemon import _course_operation

    _course_operation(handler, "revise_reading")


def handle_api_course_place_reading(handler):
    """Journal an accepted reading graph operation."""
    from surfaces.daemon import _course_operation

    _course_operation(handler, "place_reading")


def handle_api_course_reading_view(handler):
    from surfaces.daemon import _course_operation

    _course_operation(handler, "reading_view")


def handle_api_course_save_reading_note(handler):
    from surfaces.daemon import _course_operation

    _course_operation(handler, "save_reading_note")

