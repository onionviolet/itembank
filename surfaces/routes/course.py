"""Course routes; daemon-owned helpers are imported at request time."""
from model import load
from surfaces import course_ops
from surfaces import ia
from surfaces import presentation
from surfaces import session
from surfaces import settings
from surfaces import storage
from surfaces import theme
import json
import os
import re
import urllib.parse
import urllib.request
import uuid


def handle_course_area_post(handler, course_id, area):
    """Handle course forms without accepting a file path from HTML."""
    from surfaces.daemon import (
        QUIZ_SESSION_LOCK,
        _active_missed_session,
        _course_banks,
        _course_not_found,
        _quiz_path,
        _reject_cross_origin_write,
    )

    if area not in ("agent", "build", "evidence", "test", "practice"):
        handler.send_error(405, "this course area is read-only")
        return
    if _reject_cross_origin_write(handler):
        return
    fields = handler.read_form()
    if area == 'practice':
        from surfaces import course_workbench
        import course
        base = ia.course_dir_for(handler.root, course_id)
        if base is None:
            _course_not_found(handler)
            return
        if (set(fields) != {'action', 'bank', 'objective'} or
                any(len(value) != 1 for value in fields.values()) or fields['action'] != ['start_due']):
            handler.send_error(400, 'choose one current due activity')
            return
        try:
            banks = _course_banks(handler, base)
            guidance = course_workbench.course_guidance(handler.root, base, course.read_course(base)['doc'], banks)
            query = urllib.parse.parse_qs(urllib.parse.urlsplit(guidance['href']).query)
            bank, objective = fields['bank'][0], fields['objective'][0]
            if (guidance['kind'] != 'due' or query.get('bank') != [bank] or guidance['objective'] != objective):
                raise ValueError('The recommended activity changed. Reload the course before starting.')
            path = dict(banks)[bank]
            out = os.path.join(os.path.abspath(handler.root), '_attempts', 'session_%s.json' % uuid.uuid4().hex[:12])
            count = min(5, sum(q.get('objective') == objective for q in load(path)))
            created = session.do_start(path, {'objective': objective, 'count': count, 'seed': 0,
                                             'selection_mode': 'practice'}, 'practice', out, False)
        except (OSError, ValueError, KeyError, SystemExit) as exc:
            handler.send_error(400, str(getattr(exc, 'code', exc)))
            return
        handler.send_redirect(_quiz_path(bank, 'practice', session_id=created['session_id'], course_id=course_id))
        return
    if area == "test":
        course_dir = ia.course_dir_for(handler.root, course_id)
        if course_dir is None:
            _course_not_found(handler)
            return
        bank = (fields.get("bank") or [""])[-1]
        path = dict(_course_banks(handler, course_dir)).get(bank)
        if path is None or fields.get("action") != ["start_mock"]:
            handler.send_error(400, "choose a course bank for the mock test")
            return
        available = {q.get("type") for q in load(path)}
        expected = {"action", "bank", "minutes"} | {
            "mix_" + name for name in available}
        if set(fields) != expected or any(len(value) != 1 for value in fields.values()):
            handler.send_error(400, "mock test mix is incomplete")
            return
        try:
            mix = {name: int(fields["mix_" + name][0]) for name in available}
            minutes = int(fields["minutes"][0])
            if any(amount < 0 for amount in mix.values()):
                raise ValueError("negative amount")
            if not 0 <= minutes <= 240:
                raise ValueError("invalid minutes")
            mix = {name: amount for name, amount in mix.items() if amount}
            if not mix:
                raise ValueError("empty mix")
            out = os.path.join(os.path.abspath(handler.root), "_attempts",
                               "session_%s.json" % uuid.uuid4().hex[:12])
            result = session.do_start(
                path, {"selection_mode": "exam", "type_counts": mix,
                       "count": sum(mix.values()), "seed": 0},
                "exam", out, False,
                time_limit_minutes=minutes or None)
        except ValueError:
            handler.send_error(400, "choose whole-number counts and a time limit from 0 to 240 minutes")
            return
        except SystemExit as exc:
            handler.send_error(400, str(exc.code))
            return
        except Exception as exc:
            handler.send_server_error(exc)
            return
        handler.send_redirect(_quiz_path(
            bank, "exam", session_id=result["session_id"],
            course_id=course_id))
        return
    if area == "evidence":
        if set(fields) != {"action", "bank"} or \
                fields.get("action") != ["review_missed"] or \
                len(fields.get("bank", ())) != 1:
            handler.send_error(400, "choose a recorded bank to review")
            return
        course_dir = ia.course_dir_for(handler.root, course_id)
        if course_dir is None:
            _course_not_found(handler)
            return
        bank = fields["bank"][0]
        path = dict(_course_banks(handler, course_dir)).get(bank)
        if path is None:
            handler.send_error(400, "bank is unavailable in this course")
            return
        try:
            with QUIZ_SESSION_LOCK:
                active = _active_missed_session(handler, path)
                if active:
                    session_id = active
                else:
                    out = os.path.join(os.path.abspath(handler.root), "_attempts",
                                       "session_%s.json" % uuid.uuid4().hex[:12])
                    result = session.do_start(
                        path, {"selection_mode": "missed", "count": len(load(path)),
                               "seed": 0}, "practice", out, False)
                    session_id = result["session_id"]
        except SystemExit as exc:
            handler.send_error(400, str(exc.code))
            return
        except Exception as exc:
            handler.send_server_error(exc)
            return
        handler.send_redirect(_quiz_path(
            bank, "practice", session_id=session_id,
            course_id=course_id))
        return
    request = {"course_id": course_id,
               "action": (fields.get("action") or [""])[-1]}
    for name in ("skill", "proposal_id", "reason", "before_paragraph",
                 "after_paragraph", "expected_draft_fingerprint"):
        value = (fields.get(name) or [""])[-1]
        if value:
            request[name] = value
    try:
        result = course_ops.run(handler.root, "agent_operation", request,
                                actor_kind="human", actor_name="course-build-review")
    except Exception as exc:
        code = getattr(exc, "code", "agent.operation_failed")
        message = getattr(exc, "message", str(exc))
        if (message == "agent.draft_stale" and
                _send_outline_decision_recovery(handler, course_id, request["action"], fields)):
            return
        handler.send_error(400, "%s: %s" % (code, message))
        return
    destination = "/course/%s/%s" % (urllib.parse.quote(course_id, safe=""), area)
    if result.get("proposal_id"):
        destination += "?proposal=" + urllib.parse.quote(result["proposal_id"], safe="")
    handler.send_redirect(destination)


def _send_outline_decision_recovery(handler, course_id, action, fields):
    """Offer read-only review only for a current, course-local outline identity."""
    if action not in ("accept", "reject") or any(len(values) != 1 for values in fields.values()):
        return False
    try:
        import course
        import graph
        from surfaces import agent_operation
        base = ia.course_dir_for(handler.root, course_id)
        if base is None:
            return False
        read = course.read_course(base)
        pid = (fields.get("proposal_id") or [""])[0]
        record = agent_operation.status(base, pid)
        if (read["state"] != "clean" or record.get("skill") != "course-outline" or
                record.get("state") != "proposed" or record.get("disposition") != "proposed" or
                record.get("kind") != "course" or record.get("target") != course.COURSE_SIDECAR_FILENAME or
                record.get("expected_fingerprint") != read["fingerprint"] or
                not isinstance(record.get("draft"), str)):
            return False
        draft = graph.parse_course(record["draft"])
        if draft["header"].get("course_object_id") != read["object_id"]:
            return False
        destination = "/course/%s/build" % urllib.parse.quote(course_id, safe="")
        review = destination + "?outline=" + urllib.parse.quote(pid, safe="") + "#course-outline-proposal"
        body = ('<section aria-labelledby="decision-recovery"><h2 id="decision-recovery">'
                'Proposal needs a fresh review</h2>'
                '<p role="alert">No decision was applied. This form does not identify the current saved draft.</p>'
                '<p>Review its current preview and diff before choosing Accept or Reject.</p>'
                '<p><a class="go primary" href="%s">Review current proposal</a></p>'
                '<details><summary>Technical details</summary><p><code>agent.draft_stale</code></p></details></section>'
                % presentation.esc(review))
        cfg = settings.load_settings(handler.root)
        profile, _notice = settings.resolve_presentation_profile(cfg)
        page = presentation.surface_shell("Review the changed proposal", body,
            theme_css=theme.theme_css(cfg), presentation_profile=profile,
            back={"href": destination, "label": "Back to Build"})
    except Exception:
        return False
    handler.send_html(page.encode("utf-8"), 400)
    return True


def handle_course_outline_post(handler, course_id, action):
    """Native reviewed outline form, under the existing loopback write gate."""
    from surfaces.daemon import (
        _course_not_found,
        _reject_cross_origin_write,
    )

    if _reject_cross_origin_write(handler):
        return
    course_dir = ia.course_dir_for(handler.root, course_id)
    if course_dir is None:
        _course_not_found(handler)
        return
    try:
        from surfaces import course_workbench
        raw = handler.read_form()
        if any(len(values) != 1 for values in raw.values()):
            raise ValueError("agent.duplicate_outline_field")
        result = course_workbench.outline_action(
            course_dir, action, {key: values[0] for key, values in raw.items()},
            settings.load_settings(handler.root), reviewer="course-build-review")
    except Exception as exc:
        if (str(exc) == "agent.draft_stale" and
                _send_outline_decision_recovery(handler, course_id, action, raw)):
            return
        handler.send_error(400, str(exc))
        return
    destination = "/course/%s/build" % urllib.parse.quote(course_id, safe="")
    if result.get("proposal_id"):
        destination += "?outline=" + urllib.parse.quote(result["proposal_id"], safe="")
    handler.send_redirect(destination + "#course-outline-proposal")


def _send_course_research(handler, course_dir, result=None, retained=None, error=None):
    import course
    from surfaces import research_context
    try:
        body = research_context.panel(course_dir, result, retained)
        if error:
            body = '<p role="alert">%s. Your submitted selection remains below; no change was accepted.</p>' % presentation.esc(error) + body
        cfg = settings.load_settings(handler.root)
        profile, _notice = settings.resolve_presentation_profile(cfg)
        cid = course.read_course(course_dir)["object_id"]
        page = presentation.surface_shell("Selected research context", body,
            theme_css=theme.theme_css(cfg), presentation_profile=profile,
            back={"href": "/course/%s/sources" % cid, "label": "Back to sources"})
        handler.send_html(page.encode("utf-8"), 400 if error else 200)
    except Exception as exc:
        handler.send_error(400, "Research context unavailable: " + str(exc))


def handle_course_research_get(handler, course_id):
    """Read native local selection controls without source or note mutation."""
    from surfaces.daemon import (
        NATIVE_COURSE_TOOL_ERRORS,
        _course_not_found,
        _reject_cross_origin_write,
    )

    if _reject_cross_origin_write(handler):
        return
    course_dir = ia.course_dir_for(handler.root, course_id)
    if course_dir is None:
        _course_not_found(handler)
        return
    params = urllib.parse.parse_qs(urllib.parse.urlsplit(handler.path).query, keep_blank_values=True)
    if not params:
        _send_course_research(handler, course_dir)
        return
    expected = {"source_id", "locator_id", "fingerprint"}
    if (set(params) != expected or any(len(values) != 1 or not values[0] or len(values[0]) > 1024
                                     for values in params.values())):
        handler.send_error(400, "Choose one exact admitted source occurrence.")
        return
    fields = {"operation": ["preview"],
              "source": [json.dumps({"source_id": params["source_id"][0],
                                     "fingerprint": params["fingerprint"][0]})],
              "locator": [params["locator_id"][0]]}
    try:
        from surfaces import research_context
        result = research_context.apply(course_dir, fields)
        _send_course_research(handler, course_dir, result=result, retained=fields)
    except NATIVE_COURSE_TOOL_ERRORS as exc:
        _send_course_research(handler, course_dir, retained=fields, error=str(exc))


def handle_course_research_post(handler, course_id):
    """Explicit local context/quote-note forms, using existing CAS owners."""
    from surfaces.daemon import (
        _course_not_found,
        _reject_cross_origin_write,
    )

    if _reject_cross_origin_write(handler):
        return
    course_dir = ia.course_dir_for(handler.root, course_id)
    if course_dir is None:
        _course_not_found(handler)
        return
    fields = handler.read_form()
    try:
        from surfaces import research_context
        result = research_context.apply(course_dir, fields)
    except Exception as exc:
        _send_course_research(handler, course_dir, retained=fields, error=str(exc))
        return
    _send_course_research(handler, course_dir, result)


def _send_course_context_help(handler, course_dir, course_id, result=None, retained=None, error=None):
    from surfaces import context_help
    cfg = settings.load_settings(handler.root)
    profile, _notice = settings.resolve_presentation_profile(cfg)
    body = context_help.panel(course_dir, result=result, retained=retained,
                              settings_data=cfg, course_id=course_id)
    if error:
        body = '<p role="alert">%s. Your input remains below.</p>' % presentation.esc(error) + body
    page = presentation.surface_shell("Ask about selected sources", body,
        theme_css=theme.theme_css(cfg), presentation_profile=profile,
        back={"href": "/course/%s/sources" % urllib.parse.quote(course_id, safe=""),
              "label": "Back to sources"})
    handler.send_html(page.encode("utf-8"), 400 if error else 200)


def handle_course_context_help_get(handler, course_id):
    from surfaces.daemon import (
        NATIVE_COURSE_TOOL_ERRORS,
        _course_not_found,
        _reject_cross_origin_write,
    )

    if _reject_cross_origin_write(handler):
        return
    base = ia.course_dir_for(handler.root, course_id)
    if base is None:
        _course_not_found(handler)
        return
    try:
        _send_course_context_help(handler, base, course_id)
    except NATIVE_COURSE_TOOL_ERRORS as exc:
        handler.send_error(400, str(exc))


def handle_course_context_help_post(handler, course_id):
    from surfaces.daemon import (
        NATIVE_COURSE_TOOL_ERRORS,
        _course_not_found,
        _reject_cross_origin_write,
    )

    if _reject_cross_origin_write(handler):
        return
    base = ia.course_dir_for(handler.root, course_id)
    if base is None:
        _course_not_found(handler)
        return
    fields = handler.read_form()
    try:
        from surfaces import context_help
        result = context_help.form_apply(base, fields, settings.load_settings(handler.root))
        _send_course_context_help(handler, base, course_id, result=result)
    except NATIVE_COURSE_TOOL_ERRORS as exc:
        _send_course_context_help(handler, base, course_id, retained=fields, error=str(exc))


def handle_course_context_help_api(handler, action):
    from surfaces.daemon import (
        NATIVE_COURSE_TOOL_ERRORS,
        _course_not_found,
        _reject_cross_origin_write,
        api_read_json,
    )

    if _reject_cross_origin_write(handler):
        return
    body, failed = api_read_json(handler)
    if failed:
        return
    cid = body.pop("course_id", None)
    if not isinstance(cid, str) or not re.fullmatch(r"[A-Za-z0-9_.-]{1,64}", cid):
        handler.send_error(400, "Choose one admitted course identity.")
        return
    base = ia.course_dir_for(handler.root, cid)
    if base is None:
        _course_not_found(handler)
        return
    try:
        from surfaces import context_help
        result = context_help.apply(base, action, body, settings.load_settings(handler.root))
        handler.send_json(result)
    except NATIVE_COURSE_TOOL_ERRORS as exc:
        handler.send_error(400, str(exc))


def _send_restore_workspace(handler, result=None, retained=None, error=None):
    from surfaces import restore_workspace
    cfg = settings.load_settings(handler.root)
    profile, _notice = settings.resolve_presentation_profile(cfg)
    body = restore_workspace.panel(handler.root, result=result, retained=retained,
                                   action_url="/restore")
    if error:
        body = '<p role="alert">%s. Review the retained choices before trying again.</p>' % presentation.esc(error) + body
    page = presentation.surface_shell("Restore a workspace copy", body,
        theme_css=theme.theme_css(cfg), presentation_profile=profile,
        back={"href": "/courses", "label": "Back to courses"})
    handler.send_html(page.encode("utf-8"), 400 if error else 200)


def _restore_reopen_result(handler, fields):
    """Validate the same exact destination selector for native reads and forms."""
    expected = {"destination_root", "destination_name", "course_object_id",
                "course_fingerprint", "destination_device", "destination_inode"}
    if set(fields) != expected or any(len(values) != 1 for values in fields.values()):
        raise ValueError("Choose the exact validated recovery copy.")
    body = {key: values[0] for key, values in fields.items()}
    if any(not re.fullmatch(r"[0-9]{1,24}", body[key])
           for key in ("destination_device", "destination_inode")):
        raise ValueError("The recovery destination identity is invalid.")
    return course_ops.reopen_merged_restore(handler.root, body["destination_root"],
        body["destination_name"], body["course_object_id"], body["course_fingerprint"],
        [int(body["destination_device"]), int(body["destination_inode"])])


def handle_restore_get(handler):
    from surfaces.daemon import (
        NATIVE_COURSE_TOOL_ERRORS,
        _reject_cross_origin_write,
    )

    if _reject_cross_origin_write(handler):
        return
    try:
        fields = urllib.parse.parse_qs(urllib.parse.urlsplit(handler.path).query, keep_blank_values=True)
        result = None
        if fields:
            result = dict(_restore_reopen_result(handler, fields), status="recovery_ready",
                          next_action="Open the exact read-only recovered course below.")
            result["direct_course_reopen"] = not course_ops.workspace.read_workspace(result["destination"])["present"]
        _send_restore_workspace(handler, result=result)
    except NATIVE_COURSE_TOOL_ERRORS as exc:
        handler.send_error(400, str(exc))


def handle_restore_post(handler):
    from surfaces.daemon import (
        NATIVE_COURSE_TOOL_ERRORS,
        _reject_cross_origin_write,
    )

    if _reject_cross_origin_write(handler):
        return
    fields = handler.read_form()
    try:
        from surfaces import restore_workspace
        result = restore_workspace.apply(handler.root, fields,
                                         actor_kind="human", actor_name="local learner")
        if result.get("status") == "restored":
            # A successful copy opens a stable read view, never a replayable write.
            selector = {key: result[key] for key in
                        ("destination_root", "destination_name", "course_object_id", "course_fingerprint")}
            selector.update(destination_device=result["destination_identity"][0],
                            destination_inode=result["destination_identity"][1])
            handler.send_redirect("/restore?" + urllib.parse.urlencode(selector))
        else:
            _send_restore_workspace(handler, result=result)
    except NATIVE_COURSE_TOOL_ERRORS as exc:
        _send_restore_workspace(handler, retained=fields, error=str(exc))


def handle_restored_workspace_open(handler):
    """Reopen one exact validated recovery copy, without current-root enrollment."""
    from surfaces.daemon import (
        NATIVE_COURSE_TOOL_ERRORS,
        _reject_cross_origin_write,
    )

    if _reject_cross_origin_write(handler):
        return
    fields = handler.read_form()
    try:
        result = _restore_reopen_result(handler, fields)
        doc = result["course_view"]
        esc = presentation.esc
        content = '<h2>%s</h2><p role="status">Opened the validated recovery copy.</p>' % esc(doc["header"]["title"])
        content += '<p>This view reads the recovery copy directly. The original workspace is unchanged. Learning and review navigation remain in a separately opened workspace.</p>'
        content += '<h2>Objectives</h2><ol>%s</ol>' % ''.join(
            '<li>%s</li>' % esc(row.get("statement") or row["id"]) for row in doc.get("objectives", []))
        content += '<h2>Sources</h2><ul>%s</ul>' % ''.join(
            '<li>%s</li>' % esc(row.get("title") or row["source_object_id"]) for row in doc.get("sources", []))
        content += '<h2>Activity bindings</h2><ul>%s</ul>' % ''.join(
            '<li>%s: %s (%s)</li>' % (esc(row.get("objective", "")),
                esc(row.get("treatment_kind") or row.get("binding_kind", "")), esc(row.get("state", "unknown")))
            for row in doc.get("bindings", []))
        cfg = settings.load_settings(handler.root)
        page = presentation.surface_shell("Recovered workspace", content,
            theme_css=theme.theme_css(cfg), back={"href": "/restore", "label": "Back to recovery"})
        handler.send_html(page.encode("utf-8"))
    except NATIVE_COURSE_TOOL_ERRORS as exc:
        handler.send_error(400, str(exc))


def _artifact_context(handler, course_id, fields, bank_stem):
    from surfaces.daemon import (
        _course_banks,
        api_session_path,
    )

    import course
    import reading_desk
    from surfaces import learner_artifacts
    base = ia.course_dir_for(handler.root, course_id)
    if base is None:
        raise ValueError("Choose an admitted course.")
    admitted = dict(_course_banks(handler, base))
    if bank_stem not in admitted:
        raise ValueError("Choose a short activity from this course.")
    body = learner_artifacts.form_body(fields)
    session_id = body.get("session_id") or None
    session_file = api_session_path(handler, session_id) if session_id else None
    if session_id and session_file is None:
        raise ValueError("This sitting is unavailable. Reopen the original activity.")
    return {"bank_path": admitted[bank_stem], "note_root": reading_desk.note_root(base),
            "course_id": course.read_course(base)["object_id"],
            "item_ref": body.get("item_ref", ""), "session_file": session_file}, body


def _send_course_artifacts(handler, course_id, bank_stem, context, view, *, message="", preview=False, preserved_wording=None, status=200):
    from surfaces.daemon import (
        NATIVE_COURSE_TOOL_ERRORS,
        _quiz_path,
    )

    from surfaces import learner_artifacts
    objective_label = None
    base = ia.course_dir_for(handler.root, course_id)
    if base:
        try:
            doc = course_ops.course_module.read_course(base)["doc"]
            objective_label = next((row.get("statement") for row in doc.get("objectives", [])
                                    if row["id"] == view.get("objective")), None)
        except NATIVE_COURSE_TOOL_ERRORS:
            pass
    query = urllib.parse.urlencode({"bank": bank_stem})
    action_url = "/course/%s/artifacts?%s" % (urllib.parse.quote(course_id, safe=""), query)
    back = (_quiz_path(bank_stem, "practice", session_id=view["session_id"], course_id=course_id)
            if view.get("session_id") else "/course/%s/learn" % urllib.parse.quote(course_id, safe=""))
    page = learner_artifacts.render(view, action_url=action_url, return_href=back,
        panel_href=action_url, message=message, preview=preview,
        preserved_wording=preserved_wording,
        reviewer_href=back if view.get("session_id") else None,
        objective_label=objective_label,
        theme_css=theme.theme_css(settings.load_settings(handler.root)))
    handler.send_html(page.encode("utf-8"), status)


def handle_course_artifacts_get(handler, course_id):
    from surfaces.daemon import (
        NATIVE_COURSE_TOOL_ERRORS,
        _course_banks,
        _course_not_found,
        _reject_cross_origin_write,
    )

    if _reject_cross_origin_write(handler):
        return
    from surfaces import learner_artifacts
    params = urllib.parse.parse_qs(urllib.parse.urlsplit(handler.path).query)
    stems = params.pop("bank", [])
    if len(stems) > 1:
        handler.send_error(400, "Choose one admitted activity.")
        return
    if not stems:
        base = ia.course_dir_for(handler.root, course_id)
        if base is None:
            _course_not_found(handler)
            return
        choices = []
        for stem, path in _course_banks(handler, base):
            for q in load(path):
                if q.get("type") == "short":
                    query = urllib.parse.urlencode({"bank": stem, "item_ref": q["id"]})
                    href = "/course/%s/artifacts?%s" % (urllib.parse.quote(course_id, safe=""), query)
                    choices.append('<li><a href="%s">%s: %s</a></li>' % (
                        presentation.esc(href), presentation.esc(stem), presentation.esc(q["stem"])))
        body = '<p>Save a private text, proof or program draft. Submission and review stay with its existing short-response sitting.</p>'
        body += '<ul>%s</ul>' % ''.join(choices) if choices else '<p>No short-response activities are available in this course.</p>'
        cfg = settings.load_settings(handler.root)
        page = presentation.surface_shell("My original work", body,
            theme_css=theme.theme_css(cfg), back={"href": "/course/%s/learn" % course_id, "label": "Back to learning"})
        handler.send_html(page.encode("utf-8"))
        return
    try:
        context, body = _artifact_context(handler, course_id, params, stems[0])
        view = learner_artifacts.view(**context, note_id=body.get("note_id") or None,
                                      kind=body.get("kind", "explanation"))
        # Describe current saved state, never an untrusted success flag.
        message = ("Saved privately. Submission and review are shown separately below."
                   if view.get("draft") else
                   "This activity has a practice sitting. Saving still does not submit your work."
                   if view.get("session_id") else "")
        _send_course_artifacts(handler, course_id, stems[0], context, view, message=message)
    except NATIVE_COURSE_TOOL_ERRORS as exc:
        handler.send_error(400, str(exc))


def handle_course_artifacts_post(handler, course_id):
    from surfaces.daemon import (
        NATIVE_COURSE_TOOL_ERRORS,
        QUIZ_SESSION_LOCK,
        _reject_cross_origin_write,
    )

    if _reject_cross_origin_write(handler):
        return
    from surfaces import learner_artifacts
    query = urllib.parse.parse_qs(urllib.parse.urlsplit(handler.path).query)
    stems = query.get("bank", [])
    if set(query) != {"bank"} or len(stems) != 1:
        handler.send_error(400, "Choose one admitted activity.")
        return
    fields = handler.read_form()
    try:
        context, body = _artifact_context(handler, course_id, fields, stems[0])
        if body.get("action") == "start":
            current = learner_artifacts.view(**context, note_id=body.get("note_id") or None,
                                              kind=body.get("kind", "explanation"))
            if (context["session_file"] is not None or body.get("confirmed") != "yes" or
                    body.get("bank_revision") != current["bank_revision"] or current["target_changed"]):
                raise ValueError("Confirm this current activity before starting a separate practice sitting.")
            qs = load(context["bank_path"])
            others = [q for q in qs if q.get("type") == "short" and q["id"] != context["item_ref"]]
            if any(not q.get("item_id") for q in others):
                raise ValueError("Other short activities need stable item IDs before selecting this one exactly.")
            out = os.path.join(os.path.abspath(handler.root), "_attempts",
                               "session_%s.json" % uuid.uuid4().hex)
            with QUIZ_SESSION_LOCK:
                session.do_start(context["bank_path"], {"type": "short", "count": 1, "seed": 0,
                    "exclude_item_ids": [q["item_id"] for q in others]}, "practice", out, False)
            context["session_file"] = out
            result = {"view": learner_artifacts.view(**context, note_id=body.get("note_id") or None,
                                                       kind=body.get("kind", "explanation")),
                      "message": "Started this activity's practice sitting. Saving still does not submit your work."}
        else:
            result = learner_artifacts.apply(body.get("action", ""), body, **context)
        if body.get("action") in ("start", "save", "submit"):
            # Reload reads this exact sitting and draft instead of replaying a write.
            view = result["view"]
            query = urllib.parse.urlencode({"bank": stems[0], "item_ref": view["item_ref"],
                "kind": view["kind"], "session_id": view.get("session_id") or "",
                "note_id": (view.get("draft") or {}).get("note_id", "")})
            handler.send_redirect("/course/%s/artifacts?%s" % (
                urllib.parse.quote(course_id, safe=""), query))
        else:
            _send_course_artifacts(handler, course_id, stems[0], context, result["view"],
                                   message=result.get("message", ""), preview=result.get("preview", False))
    except (SystemExit,) + NATIVE_COURSE_TOOL_ERRORS as exc:
        try:
            view = learner_artifacts.view(**context, note_id=body.get("note_id") or None,
                                          kind=body.get("kind", "explanation"))
            _send_course_artifacts(handler, course_id, stems[0], context, view,
                message=str(exc), preserved_wording=body.get("wording"), status=400)
        except (UnboundLocalError,) + NATIVE_COURSE_TOOL_ERRORS:
            handler.send_error(400, str(exc))


def handle_course_read_get(handler, operation, course_id):
    """GET course read authority, shared by agent clients and page code."""
    from surfaces.daemon import (
        _reject_cross_origin,
    )

    if _reject_cross_origin(handler):
        return
    try:
        result = course_ops.run(handler.root, operation, {"course_id": course_id})
    except Exception as exc:
        code = getattr(exc, "code", None)
        if code:
            handler.send_error(404 if code == "course.unknown_course" else 400,
                               "%s: %s" % (code, getattr(exc, "message", str(exc))))
            return
        handler.send_server_error(exc)
        return
    handler.send_json(result)


def handle_storage_get(handler):
    """Inspect local storage on demand, without following linked roots."""
    from surfaces.daemon import (
        _client_is_loopback,
    )

    if not _client_is_loopback(handler):
        handler.send_error(403, "storage inspection is available on this device only")
        return
    try:
        report = storage.inspect(handler.root)
        css = theme.theme_css(settings.load_settings(handler.root))
        handler.send_html(storage.page(report, theme_css=css).encode("utf-8"))
    except (OSError, storage.StorageError, SystemExit) as exc:
        handler.send_server_error(exc)


def handle_storage_post(handler):
    """Clear only bytecode named by the unchanged, explicit storage preview."""
    from surfaces.daemon import (
        _reject_cross_origin_write,
    )

    if _reject_cross_origin_write(handler):
        return
    fields = handler.read_form()
    if set(fields) != {"cache_token"} or len(fields["cache_token"]) != 1 or not re.fullmatch(
            r"[a-f0-9]{64}", fields["cache_token"][0]):
        handler.send_error(400, "open storage use before clearing caches")
        return
    try:
        result = storage.clear_python_cache(handler.root, fields["cache_token"][0])
        report = storage.inspect(handler.root)
        css = theme.theme_css(settings.load_settings(handler.root))
        notice = "Removed %d cache file(s), %s. %s" % (
            result["removed_files"], storage.size_label(result["removed_bytes"]), result["notice"])
        handler.send_html(storage.page(report, theme_css=css, notice=notice).encode("utf-8"))
    except storage.StorageError as exc:
        handler.send_error(409, str(exc))
    except (OSError, SystemExit) as exc:
        handler.send_server_error(exc)


def handle_course_reading_get(handler, course_id, occurrence_id, revision_id):
    from surfaces.daemon import (
        _course_source_return,
        _reject_cross_origin_write,
    )

    if _reject_cross_origin_write(handler):
        return
    try:
        import course
        import reading_desk
        from surfaces import reading_desk as desk_surface
        base = course_ops.resolve_course(handler.root, course_id)
        read = course.read_course(base)
        view = reading_desk.snapshot(base, dict(expected_fingerprint=read['fingerprint'],
                                     occurrence_id=occurrence_id, revision_id=revision_id))
        origin = urllib.parse.parse_qs(urllib.parse.urlsplit(handler.path).query).get('from', ['learn'])[0]
        source_return = _course_source_return(handler, course_id)
        return_options = {"source_return": source_return} if source_return else {}
        handler.send_html(desk_surface.render(
            course_id, read, occurrence_id, revision_id, view,
            theme_css=theme.theme_css(settings.load_settings(handler.root)),
            origin='overview' if origin == 'overview' else 'learn',
            **return_options).encode('utf-8'))
    except Exception:
        handler.send_error(400, 'Reading unavailable. Refresh the course or inspect recovery.')

