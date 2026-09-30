"""Read-only course context for the map, sources, and evidence areas."""

import os
import re
import urllib.parse
import contextlib
import io

import course
import evidence
import graph
import identity
import journal
import model
from surfaces import ia, presentation
from surfaces.reading_desk import href as reading_href


def _artifact_path(base, relative):
    root = os.path.realpath(base)
    path = os.path.realpath(os.path.join(root, relative))
    if os.path.isabs(relative) or os.path.commonpath([root, path]) != root:
        raise ValueError("course.artifact_outside_root")
    return path


def readiness(course_dir, banks):
    """Join existing checks without repairing, accepting, or claiming mastery.

    A failed check is an error row, never a successful check with zero findings.
    Paths and lint locations are repair pointers. No keyed text is returned.
    """
    rows = []
    def add(kind, location, state, code, repair):
        rows.append({"kind": kind, "location": location, "state": state,
                     "code": code, "repair": repair})
    try:
        read = course.read_course(course_dir)
        doc = read["doc"]
        add("course", "course-graph.md", read["state"], "journal.object_state",
            "Reconcile the course revision before accepting edits.")
    except Exception:
        add("course", "course-graph.md", "error", "course.check_failed",
            "Repair the course record, then run readiness again.")
        return {"state": "error", "rows": rows, "read_only": True}
    try:
        registry = journal.read_registry(course_dir)
    except Exception:
        add("registry", "_journal", "error", "registry.check_failed",
            "Repair the local object registry, then run readiness again.")
        registry = None
    if registry is not None:
        ids = {row["source_object_id"] for row in doc.get("sources") or []}
        ids.update(oid for oid, row in registry.items() if row.get("kind") == "lesson")
        for oid in sorted(ids):
            entry = registry.get(oid)
            kind = (entry or {}).get("kind") or "source"
            location = (entry or {}).get("path") or "source:" + oid
            try:
                state = journal.object_state(course_dir, oid)
                add(kind, location, state, "journal.object_state",
                    "Restore a missing file or reconcile its changed revision.")
                if entry and kind == "lesson" and state == "clean":
                    path = _artifact_path(course_dir, entry["path"])
                    lesson = model.parse_lesson(path)
                    if not lesson:
                        add("lesson", location, "empty", "lesson.absent", "Add the missing lesson section through a reviewed draft.")
                    elif lesson.get("error"):
                        add("lesson", location, "invalid", lesson["error"], "Repair the linked lesson source.")
                    else:
                        errors, _warnings = model.lint([], lesson=lesson)
                        for finding in errors:
                            add("lesson", location, "invalid", finding.code, "Correct this lesson finding in a reviewed draft.")
            except Exception:
                add(kind, location, "error", "artifact.check_failed", "Make the registered artifact readable, then rerun this check.")
        superseded = {b.get("supersedes_binding_revision_id") for b in doc.get("bindings") or []}
        for index, binding in enumerate(doc.get("bindings") or []):
            if binding.get("binding_revision_id") and binding["binding_revision_id"] in superseded:
                continue
            location = "course-graph.md: Bindings row %d" % (index + 1)
            start_count = len(rows)
            try:
                graph.validate_binding(binding)
                source_id = binding.get("source_object_id")
                if source_id not in registry or source_id not in {s["source_object_id"] for s in doc["sources"]}:
                    add("link", location, "invalid", "binding.source_missing", "Register and align the exact source before rebinding.")
                else:
                    right = (graph.treatment_right(binding["treatment_kind"])
                             if binding.get("binding_kind") == "treatment" else "read")
                    rights = course.rights_for_binding(course_dir, source_id, right)
                    if rights != "granted":
                        add("rights", location, rights, "binding.right_not_granted", "Review the source's current %s right." % right)
                if binding.get("treatment_kind") in ("guided-lesson", "practice", "formal-test"):
                    locator = binding.get("locator") or ""
                    match = re.match(r"^(.+?\.md)(?=$|[\s,;#:]|$)", locator, re.I)
                    if match is None:
                        add("link", location, "unknown", "binding.artifact_unresolved", "Record the exact lesson or bank path and locator.")
                    elif not os.path.isfile(_artifact_path(course_dir, match.group(1))):
                        add("link", location, "invalid", "binding.artifact_missing", "Restore or rebind the missing lesson or bank.")
                if binding.get("state") == "unknown":
                    add("link", location, "unknown", "binding.coverage_unknown", "Review source support and coverage; an assigned treatment does not prove coverage.")
                if len(rows) == start_count:
                    add("link", location, "clean", "binding.check_passed", "No repair needed for the checks run.")
            except Exception:
                add("link", location, "error", "binding.check_failed", "Repair this binding row, then run the check again.")
        try:
            import director
            texts = {}
            for source in doc["sources"]:
                sid = source["source_object_id"]
                text, _notice = _source_text(course_dir, sid, {os.path.realpath(path) for _stem, path in banks})
                if text is not None:
                    texts[sid] = text
            claims = director.coverage_claims_for(doc, texts)
            by_objective = {}
            for claim in claims:
                by_objective.setdefault(claim["objective_id"], claim["state"])
            for objective in doc["objectives"]:
                status = by_objective.get(objective["id"], director.classify_coverage([]))
                add("source-coverage", "course-graph.md: objective " + objective["id"],
                    "clean" if status == "covered" else status,
                    "director.coverage." + status,
                    "Review the source locator and cited coverage evidence; no binding is changed here.")
        except Exception:
            add("source-coverage", "course-graph.md: Bindings", "error", "coverage.check_failed",
                "Repair the source coverage inputs, then rerun this check.")
    for _stem, path in banks:
        location = os.path.relpath(path, course_dir)
        try:
            path = _artifact_path(course_dir, location)
            questions = model.load(path)
            if not questions:
                add("bank", location, "empty", "bank.empty", "Author the missing assessment through a reviewed draft.")
                continue
            errors, warnings = model.lint(questions, lesson=model.parse_lesson(path),
                                          terms=model.parse_terms(path), keys=model.parse_key_blocks(path),
                                          media=model.parse_media(path), activities=model.parse_activities(path))
            if not errors and not warnings:
                add("bank", location, "clean", "bank.lint_passed", "No repair needed for the checks run.")
            for finding in errors + warnings:
                add("lesson-link" if finding.code.startswith(("lesson.", "item.lesson")) else "bank",
                    location + ": " + str(finding.item),
                    "invalid" if finding in errors else "warning", finding.code,
                    "Inspect this lint code with itembank lint; correct the exact item or lesson reference.")
        except Exception:
            add("bank", location, "error", "bank.check_failed", "Restore readable bank bytes, then rerun lint.")
    state = ("error" if any(r["state"] == "error" for r in rows) else
             "needs-review" if any(r["state"] != "clean" for r in rows) else "clean")
    return {"state": state, "rows": rows, "read_only": True,
            "fingerprint": read["fingerprint"], "checks": "registry, current rights, bindings, bank and lesson lint"}


def readiness_panel(payload):
    rows = ['<li><strong>%s: %s</strong>. %s. %s</li>' % (
        presentation.esc(row["kind"]), presentation.esc(row["state"]),
        presentation.esc(row["location"] + " (" + row["code"] + ")"),
        presentation.esc(row["repair"])) for row in payload["rows"]]
    return ('<section id="course-readiness"><h3>Course readiness checks</h3>'
            '<p role="status">%s. Read-only checks; this is not a learning or mastery claim.</p>'
            '<ul>%s</ul></section>' % (presentation.esc(payload["state"]), ''.join(rows)))


def review_history(root, course_dir, doc, banks, cutoff=None):
    """A disposable joined view of saved responses, marks, readings and due work.

    Never load a bank key or emit learner answers. Detailed feedback remains
    behind the saved sitting's runtime route and release policy.
    """
    import retention
    import runtime
    from surfaces import settings

    cid = doc["header"]["course_object_id"]
    admitted_paths = {}
    for stem, path in banks:
        admitted_paths.setdefault(os.path.realpath(path), []).append(stem)
    paths = {path: stems[0] for path, stems in admitted_paths.items() if len(stems) == 1}
    logs = {os.path.realpath(evidence.log_path(course_dir))}
    logs.update(os.path.realpath(evidence.log_path(os.path.dirname(path))) for path in paths)
    events, failures = [], []
    if len(paths) != len(admitted_paths):
        failures.append("An artifact has ambiguous admitted routes; its review links are unavailable.")
    for log in sorted(logs):
        warnings = io.StringIO()
        try:
            with contextlib.redirect_stdout(warnings):
                current = list(evidence.live_events(log))
            if warnings.getvalue():
                failures.append("Evidence includes unreadable or unsupported records.")
            events.extend(current)
        except (OSError, ValueError):
            failures.append("Evidence check failed. Repair the local record, then reload.")
    unique_events = {}
    for event in events:
        eid = event.get("event_id")
        if not eid:
            failures.append("Evidence identity is unavailable; due work cannot be derived safely.")
            continue
        if eid in unique_events and unique_events[eid] != event:
            failures.append("Divergent records share an evidence identity. Reconcile them before reviewing due work.")
        unique_events[eid] = event
    events = list(unique_events.values())
    # Each admitted bank has its own evidence root. Session identity scopes
    # responses, including older events whose bank field is only a basename.
    saved = ia._course_resume_state(root, course_dir)
    if saved.get("state") == "unavailable":
        failures.append("Some saved sittings are unavailable; their history cannot be joined safely.")
    sessions = {s["session_id"]: s for s in saved["sessions"] if os.path.realpath(s["bank"]) in paths}
    responses = [e for e in events if e.get("event_type") == "response" and
                 e.get("session_id") in sessions and
                 e.get("bank") == os.path.basename(sessions[e["session_id"]]["bank"])]
    ids = {e["event_id"] for e in responses}
    relevant = [e for e in events if e.get("event_id") in ids or
                (e.get("session_id") in sessions and e.get("event_type") in ("mark", "hint", "selection"))]
    released = runtime.learner_evidence(relevant, sessions)
    marks = {e.get("marks_event"): e for e in released if e.get("event_type") == "mark"}
    rows = []
    counts = {"settled": 0, "missed": 0, "pending": 0, "withheld": 0, "reading_reported": 0}
    for event in responses:
        sitting = sessions[event["session_id"]]
        permitted = runtime.assessment_feedback_released(event.get("mode"), sitting)
        if permitted:
            verdict = retention._settled_verdict(event, marks)
            status = "pending" if verdict is None else "missed" if verdict is False else "settled-correct"
            counts["pending" if verdict is None else "settled"] += 1
            if verdict is False:
                counts["missed"] += 1
        else:
            status = "feedback-withheld"
            counts["withheld"] += 1
        stem = paths.get(os.path.realpath(sitting["bank"]))
        query = urllib.parse.urlencode({"mode": sitting["mode"], "session": event["session_id"], "course": cid})
        resume = '/quiz/' + urllib.parse.quote(stem, safe='') + '?' + query
        links = []
        for index, source in enumerate(doc.get("sources") or []):
            if any(b.get("objective") == event.get("objective") and
                   b.get("source_object_id") == source["source_object_id"] for b in doc.get("bindings") or []):
                links.append({"origin": "Source", "label": source.get("title") or source["source_object_id"],
                              "href": '/course/%s/sources?source=%d#source-%d' % (urllib.parse.quote(cid, safe=''), index, index)})
        for binding in doc.get("bindings") or []:
            if binding.get("objective") != event.get("objective") or binding.get("treatment_kind") != "guided-lesson":
                continue
            locator = binding.get("locator") or ""
            match = re.match(r"^(.+?\.md)(?=$|[\s,;#:]|$)", locator, re.I)
            if match:
                try:
                    lesson_stem = paths.get(_artifact_path(course_dir, match.group(1)))
                except ValueError:
                    lesson_stem = None
                if lesson_stem:
                    links.append({"origin": "Lesson", "label": "Linked explanation",
                                  "href": '/lesson/' + urllib.parse.quote(lesson_stem, safe='') + '?' +
                                  urllib.parse.urlencode({"return": resume, "course": cid})})
        rows.append({"event_id": event["event_id"], "session_id": event["session_id"],
                     "item_ref": event.get("item_ref"), "objective": event.get("objective"),
                     "status": status, "timestamp": event["ts"],
                     "feedback_href": resume if sitting["status"] == "active" else
                     '/report?' + urllib.parse.urlencode({"session": event["session_id"]}),
                     "resume_href": resume if sitting["status"] == "active" else None,
                     "confidence": event.get("confidence"),
                     "source_ref": event.get("source_ref") if permitted else None,
                     "context_links": links if permitted else []})
    readings = [e for e in events if e.get("event_type") == "reading_declared" and e.get("course_id") == cid]
    counts["reading_reported"] = len(readings)
    try:
        due = None if failures else retention.retention_report(released, cutoff=cutoff,
                                                              cfg=settings.load_settings(root))
    except (Exception, SystemExit):
        failures.append("Due-work derivation failed. No due recommendation is available.")
        due = None
    return {"state": "error" if failures else "empty" if not responses and not readings else "available",
            "rows": rows, "counts": counts, "due": due, "failures": failures,
            "session_state": saved.get("state", "unavailable"), "self_rating": "not-recorded",
            "read_only": True}


def outline_panel(course_dir, doc, proposal_id=None):
    """Native editable treatment rows over an unaccepted course proposal.

    The daemon supplies the write gate and routes the submitted fields to
    propose_course_outline. Each accepted file write uses its existing journal.
    """
    from surfaces import agent_operation

    cid = urllib.parse.quote(doc["header"]["course_object_id"], safe='')
    record = agent_operation.status(course_dir, proposal_id) if proposal_id else None
    choices = {c["objective"]: c for c in (record or {}).get("treatment_choices") or []}
    editable = graph.parse_course(record["draft"]) if record and record.get("disposition") == "proposed" else doc
    out = ['<section id="course-outline-proposal"><h3>Outline and treatments</h3>',
           '<p>Keep adequate direct readings. Add only a missing treatment; existing source and treatment bindings stay recorded.</p>',
           '<form method="post" action="/course/%s/outline/propose">' % cid]
    for name, value in (("expected_course_fingerprint", course.read_course(course_dir)["fingerprint"]),
                        ("proposal_id", proposal_id or ''),
                        ("expected_draft_fingerprint", agent_operation.draft_fingerprint(record["draft"]) if record and record.get("disposition") == "proposed" else '')):
        out.append('<input type="hidden" name="%s" value="%s">' % (name, presentation.esc(value)))
    for index, objective in enumerate(editable["objectives"]):
        oid = objective["id"]
        choice = choices.get(oid) or {}
        out.append('<fieldset><legend>%s</legend><p>Objective %s</p>' % (
            presentation.esc(objective["statement"]), presentation.esc(oid)))
        out.append('<label>Outline position <input type="number" min="1" name="order-%s" value="%d" required></label>' % (presentation.esc(oid), index + 1))
        out.append('<label>Missing treatment <select name="treatment-%s"><option value="">Keep current treatments</option>' % presentation.esc(oid))
        for kind in graph.TREATMENT_KINDS:
            out.append('<option value="%s"%s>%s</option>' % (presentation.esc(kind), ' selected' if choice.get("treatment") == kind else '', presentation.esc(kind)))
        out.append('</select></label><label>Source <select name="source-%s">' % presentation.esc(oid))
        for source in doc["sources"]:
            sid = source["source_object_id"]
            out.append('<option value="%s"%s>%s</option>' % (presentation.esc(sid), ' selected' if choice.get("source") == sid else '', presentation.esc(source.get("title") or sid)))
        out.append('</select></label><label>Exact source or artifact locator <input name="locator-%s" value="%s"></label></fieldset>' % (presentation.esc(oid), presentation.esc(choice.get("locator") or '')))
    out.append('<button type="submit">Preview proposal</button></form>')
    if record:
        out.append('<p role="status">%s</p>' % presentation.esc(record.get("disposition")))
        if record.get("disposition") == "proposed":
            out.append('<h4>Proposed outline</h4><pre>%s</pre><h4>Exact diff</h4><pre>%s</pre>' % (
                presentation.esc(graph.outline_projection(editable)),
                presentation.esc('\n'.join(record["diff"]["lines"]))))
            for action, label in (("accept", "Accept proposal"), ("reject", "Cancel proposal")):
                out.append('<form method="post" action="/course/%s/outline/%s"><input type="hidden" name="proposal_id" value="%s"><input type="hidden" name="expected_draft_fingerprint" value="%s"><button>%s</button></form>' % (cid, action, presentation.esc(proposal_id), agent_operation.draft_fingerprint(record["draft"]), label))
        elif record.get("disposition") == "accepted":
            out.append('<form method="post" action="/course/%s/outline/undo"><input type="hidden" name="proposal_id" value="%s"><button>Undo accepted proposal</button></form>' % (cid, presentation.esc(proposal_id)))
    out.append('</section>')
    return ''.join(out)


def outline_action(course_dir, action, fields, settings, reviewer=""):
    """Native form adapter; the daemon must resolve the course and gate writes.

    No caller can supply a target path, objective statement, or accepted score.
    This adapter uses the same proposal, CAS, rights and undo functions as
    direct callers. A5 needs only routing and the existing write guard.
    """
    from surfaces import agent_operation

    if action not in ("propose", "accept", "reject", "undo"):
        raise ValueError("agent.unknown_outline_action")
    if not all(isinstance(key, str) and isinstance(value, str) for key, value in fields.items()):
        raise ValueError("agent.invalid_outline_fields")
    pid = fields.get("proposal_id") or None
    if action == "propose":
        read = course.read_course(course_dir)
        expected = fields.get("expected_course_fingerprint")
        if not expected or expected != read["fingerprint"]:
            raise ValueError("agent.course_stale")
        choices, positions = [], []
        allowed = {"proposal_id", "expected_course_fingerprint", "expected_draft_fingerprint"}
        for objective in read["doc"]["objectives"]:
            oid = objective["id"]
            allowed.update(prefix + oid for prefix in ("order-", "treatment-", "source-", "locator-"))
            try:
                position = int(fields["order-" + oid])
            except (KeyError, ValueError):
                raise ValueError("agent.invalid_outline_order") from None
            if position < 1:
                raise ValueError("agent.invalid_outline_order")
            positions.append((position, oid))
            kind = fields.get("treatment-" + oid)
            if kind:
                choices.append({"objective": oid, "source": fields.get("source-" + oid, ""),
                                "treatment": kind, "locator": fields.get("locator-" + oid, "")})
        if set(fields) - allowed:
            raise ValueError("agent.invalid_outline_fields")
        if len({p for p, _oid in positions}) != len(positions):
            raise ValueError("agent.invalid_outline_order")
        return agent_operation.propose_course_outline(
            course_dir, choices, [oid for _p, oid in sorted(positions)], pid,
            fields.get("expected_draft_fingerprint"), expected)
    if set(fields) - {"proposal_id", "expected_draft_fingerprint"} or not pid:
        raise ValueError("agent.invalid_outline_fields")
    record = agent_operation.status(course_dir, pid)
    if record.get("skill") != "course-outline":
        raise ValueError("agent.course_proposal_unavailable")
    if action in ("accept", "reject") and record.get("disposition") == "proposed":
        if fields.get("expected_draft_fingerprint") != agent_operation.draft_fingerprint(record["draft"]):
            raise ValueError("agent.draft_stale")
    if action == "accept":
        return agent_operation.accept(pid, settings, base=course_dir, reviewer=reviewer,
                                      expected_draft_fingerprint=fields.get("expected_draft_fingerprint"))
    if action == "reject":
        return agent_operation.reject(course_dir, pid, reviewer=reviewer, reason="Canceled outline proposal")
    return agent_operation.undo(course_dir, pid, reviewer=reviewer)


def _link(href, label):
    return '<a href="%s">%s</a>' % (presentation.esc(href),
                                   presentation.esc(label))


def _source_text(course_dir, source_id, bank_paths):
    """Read only a clean, registered, rights-granted text source in this root."""
    try:
        row = journal.read_registry(course_dir).get(source_id)
    except (OSError, ValueError):
        return None, "Source registration is unavailable until its journal is repaired."
    if not row or row.get("kind") != "source":
        return None, "Source registration is unavailable."
    if not identity.rights_granted(row.get("rights"), "read"):
        return None, "Source reading is unavailable until its read right is granted."
    try:
        clean = journal.object_state(course_dir, source_id) == "clean"
    except (OSError, ValueError, KeyError):
        clean = False
    if not clean:
        return None, "Source reading is unavailable until this file is reconciled."
    relative = row.get("path") or ""
    root = os.path.realpath(course_dir)
    path = os.path.realpath(os.path.join(root, relative))
    if (os.path.isabs(relative) or
            os.path.commonpath([root, path]) != root or
            path in bank_paths or
            os.path.splitext(path)[1].lower() not in (".md", ".txt")):
        return None, "This source has no safe text preview here. Open an assigned reading when available."
    try:
        with open(path, "rb") as stream:
            raw = stream.read(65537)
    except OSError:
        return None, "Source file is unavailable."
    if len(raw) > 65536:
        return None, "This source is too long for the inline preview. Open an assigned reading."
    try:
        text = raw.decode("utf-8")
    except UnicodeError:
        return None, "This source is not readable as UTF-8 text."
    if model.parse_bank(text) or "CORRECT:" in text:
        return None, "Assessment source text is unavailable in this preview. Use the runtime's practice or test route."
    return text, None


def details(handler, state, course_dir, doc, banks):
    """Addressable context with back links and no assessment answers."""
    area = state["area"]
    cid = urllib.parse.quote(state["course_id"], safe="")
    if area not in ("map", "sources", "evidence"):
        return ""
    back = '<p>%s</p>' % _link('#' + (ia.anchor_slug(state["area_label"]) or 'area'),
                                'Back to ' + state["area_label"])
    bank_paths = {os.path.realpath(path) for _stem, path in banks}
    selected_source = urllib.parse.parse_qs(
        urllib.parse.urlsplit(getattr(handler, "path", "")).query).get("source", [""])[-1]
    source_titles = {row.get("source_object_id"): row.get("title") or row.get("source_object_id")
                     for row in doc.get("sources") or []}
    source_indexes = {row.get("source_object_id"): i
                      for i, row in enumerate(doc.get("sources") or [])}
    objective_titles = {row.get("id"): row.get("statement") or row.get("id")
                        for row in doc.get("objectives") or []}
    objective_indexes = {row.get("id"): i
                         for i, row in enumerate(doc.get("objectives") or [])}
    superseded_bindings = {row.get("supersedes_binding_revision_id")
                           for row in doc.get("bindings") or []}
    bindings = [row for row in doc.get("bindings") or []
                if not row.get("binding_revision_id") or
                row.get("binding_revision_id") not in superseded_bindings]
    readings = []
    try:
        validated = graph.validate_reading_graph(doc)
        superseded = {r["supersedes_revision_id"] for r in validated["occurrences"]
                      if r["supersedes_revision_id"]}
        readings = [r for r in validated["occurrences"]
                    if r["revision_id"] not in superseded]
    except (graph.GraphError, ValueError, KeyError):
        pass
    bank_activities = []
    banks_by_path = {}
    if area in ("map", "sources"):
        for stem, path in banks:
            try:
                objectives = {q.get("objective") for q in model.load(path)}
                lesson = model.parse_lesson(path)
                has_lesson = bool((lesson or {}).get("headings"))
            except Exception:
                continue
            banks_by_path.setdefault(os.path.realpath(path), []).append(
                (stem, objectives, has_lesson))

    def bound_bank(binding):
        """A treatment may open only the exact admitted bank its locator names."""
        locator = binding.get("locator")
        if not isinstance(locator, str):
            return None
        match = re.match(r"^(.+?\.md)(?=$|[\s,;#])", locator.strip(), re.I)
        if match is None or os.path.isabs(match.group(1)):
            return None
        root = os.path.realpath(course_dir)
        path = os.path.realpath(os.path.join(root, match.group(1)))
        try:
            if os.path.commonpath([root, path]) != root:
                return None
        except ValueError:
            return None
        admitted = banks_by_path.get(path) or []
        return admitted[0] if len(admitted) == 1 else None

    def assigned_links(objective=None, source_id=None):
        links = []
        for reading in readings:
            if objective and objective not in reading["objective_ids"]:
                continue
            if source_id and reading["source_ref"]["source_object_id"] != source_id:
                continue
            links.append('<li>%s</li>' % _link(
                reading_href(state["course_id"], reading), "Open assigned reading"))
        if objective:
            seen = set()
            for binding in bindings:
                if binding.get("binding_kind") != "treatment" or \
                        binding.get("objective") != objective or \
                        (source_id and binding.get("source_object_id") != source_id):
                    continue
                bank = bound_bank(binding)
                if bank is None:
                    continue
                stem, bank_objectives, has_lesson = bank
                kind = binding.get("treatment_kind")
                if objective not in bank_objectives:
                    continue
                if kind == "guided-lesson" and has_lesson:
                    href = '/lesson/' + urllib.parse.quote(stem, safe='')
                    label = "Open linked lesson"
                elif kind in ("practice", "formal-test"):
                    mode = "practice" if kind == "practice" else "exam"
                    query = urllib.parse.urlencode({"mode": mode,
                                                    "course": state["course_id"]})
                    href = '/quiz/' + urllib.parse.quote(stem, safe='') + '?' + query
                    label = "Open linked practice" if mode == "practice" else "Open linked formal test"
                else:
                    continue
                if href not in seen:
                    links.append('<li>%s</li>' % _link(href, label))
                    seen.add(href)
        return ('<h4>Learning activities</h4><ul>%s</ul>' % ''.join(links)
                if links else '<p>No assigned reading or linked activity is available here.</p>')
    sections = []
    if area == "map":
        sections.append(readiness_panel(readiness(course_dir, banks)))
        for index, row in enumerate(doc.get("objectives") or []):
            oid = row.get("id")
            linked = [b for b in bindings if b.get("objective") == oid]
            items = []
            for b in linked:
                sid = b.get("source_object_id")
                if sid not in source_indexes:
                    continue
                href = '/course/%s/sources?source=%d#source-%d' % (
                    cid, source_indexes[sid], source_indexes[sid])
                treatment = b.get("treatment_kind") or "source support"
                items.append('<li>%s: %s. %s. %s</li>' % (
                    presentation.esc(treatment), _link(href, source_titles[sid]),
                    presentation.esc(b.get("locator") or "Locator unavailable"),
                    presentation.esc(b.get("state") or "State unknown")))
            links = ('<ul>%s</ul>' % ''.join(items) if items else
                     '<p>No current source or treatment binding is recorded for this objective.</p>')
            sections.append('<section id="objective-%d" aria-labelledby="objective-title-%d">'
                            '<h3 id="objective-title-%d">%s</h3>%s%s</section>' % (
                                index, index, index,
                                presentation.esc(objective_titles[oid]),
                                links + assigned_links(objective=oid), back))
    elif area == "sources":
        for index, row in enumerate(doc.get("sources") or []):
            sid = row.get("source_object_id")
            linked = [b for b in bindings if b.get("source_object_id") == sid]
            items = []
            for b in linked:
                oid = b.get("objective")
                if oid not in objective_indexes:
                    continue
                href = '/course/%s/map#objective-%d' % (cid, objective_indexes[oid])
                items.append('<li>%s: %s. %s</li>' % (
                    presentation.esc(b.get("treatment_kind") or "source support"),
                    _link(href, objective_titles[oid]),
                    presentation.esc(b.get("locator") or "Locator unavailable")))
            text, unavailable = (_source_text(course_dir, sid, bank_paths)
                                  if selected_source == str(index) else
                                  (None, "Open this source to read its current text."))
            activities = assigned_links(source_id=sid)
            for oid in dict.fromkeys(b.get("objective") for b in linked):
                if oid in objective_indexes:
                    activities += assigned_links(objective=oid, source_id=sid)
            preview = ('<h4>Source text</h4><pre>%s</pre>' % presentation.esc(text)
                       if text is not None else '<p role="status">%s</p>' % presentation.esc(unavailable))
            sections.append('<section id="source-%d" aria-labelledby="source-title-%d">'
                            '<h3 id="source-title-%d">%s</h3><p>%s</p>'
                            '<h4>Objective alignment and treatments</h4>%s%s%s</section>' % (
                                index, index, index,
                                presentation.esc(source_titles[sid]),
                                presentation.esc(row.get("note") or "Registered course source."),
                                '<ul>%s</ul>' % ''.join(items) if items else
                                '<p>No current objective binding is recorded for this source.</p>',
                                activities + preview, back))
    else:
        from surfaces import retention_view
        sections.append(retention_view.course_review_history(
            review_history(handler.root, course_dir, doc, banks)))
        counts = {"responses": 0, "marks": 0, "sessions": set()}
        evidence_unavailable = False
        try:
            for event in evidence.live_events(evidence.log_path(course_dir)):
                kind = event.get("event_type")
                if kind == "response":
                    counts["responses"] += 1
                elif kind == "mark":
                    counts["marks"] += 1
                if event.get("session_id"):
                    counts["sessions"].add(event["session_id"])
        except (OSError, ValueError):
            evidence_unavailable = True
        for key, title, note in (
                ("responses", "Responses", "Recorded attempts include pending and incorrect responses. A count does not imply mastery."),
                ("marks", "Marks", "Settled marks are recorded by the assessment runtime."),
                ("sessions", "Sittings", "Open a saved sitting or its report below.")):
            amount = len(counts[key]) if key == "sessions" else counts[key]
            extra = ""
            if key == "sessions":
                resume = ia._course_resume_state(handler.root, course_dir)
                links = []
                admitted_banks = {}
                for stem, path in banks:
                    admitted_banks.setdefault(os.path.realpath(path), []).append(stem)
                for sitting in resume["sessions"]:
                    sid = sitting["session_id"]
                    matches = admitted_banks.get(os.path.realpath(sitting["bank"])) or []
                    if len(matches) != 1:
                        links.append('<li>Saved sitting is unavailable from this course view.</li>')
                        continue
                    if sitting["status"] == "complete":
                        href = '/report?session=' + urllib.parse.quote(sid, safe='')
                        links.append('<li>%s</li>' % _link(href, 'Report for saved sitting'))
                    elif sitting["status"] == "active":
                        stem = matches[0]
                        query = urllib.parse.urlencode({"mode": sitting["mode"],
                                                        "session": sid,
                                                        "course": state["course_id"]})
                        href = '/quiz/' + urllib.parse.quote(stem, safe='') + '?' + query
                        links.append('<li>%s</li>' % _link(href, 'Resume saved sitting'))
                extra = ('<ul>%s</ul>' % ''.join(links) if links else
                         '<p>No completed sitting report is available here.</p>')
            status = ('<p role="status">Evidence counts are unavailable until the local '
                      'record can be read. Repair the evidence record, then reload.</p>'
                      if evidence_unavailable else
                      '<p>%d recorded. %s</p>' % (amount, presentation.esc(note)))
            sections.append('<section id="evidence-%s"><h3>%s</h3>%s%s%s</section>' % (
                key, title, status, extra, back))
    return '<div class="course-detail">%s</div>' % ''.join(sections)
