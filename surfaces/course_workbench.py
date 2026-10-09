"""Read-only course context for the map, sources, and evidence areas."""

import os
import re
import urllib.parse
from types import SimpleNamespace
from datetime import datetime, timezone

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


def _admitted_sittings(root, course_dir, banks, events, course_id):
    """Use the existing read-only quiz admission gate, never start a sitting."""
    # Import locally: daemon renders this module, and its saved-session gate
    # is the existing route authority for schema, selection and stale banks.
    from surfaces.daemon import _saved_quiz_session

    saved = ia._course_resume_state(root, course_dir)
    if (saved.get("evidence_without_sitting") and not saved.get("sessions") and events
            and all(event.get("event_type") == "reading_declared" and event.get("course_id") == course_id
                    for event in events)):
        try:
            for event in events:
                evidence._validate_reading_event(event)
        except (OSError, ValueError, KeyError, TypeError):
            pass
        else:
            # A declaration's operation ID is not an assessment sitting.
            # It cannot imply a lost cursor or prevent source-first guidance.
            saved = dict(saved, state="absent", cue=ia.NOT_STARTED_CUE)
    by_path = {}
    for stem, path in banks:
        by_path.setdefault(os.path.realpath(path), []).append((stem, path))
    sessions, failures, questions = {}, [], {}
    if saved.get("state") == "unavailable" or "unavailable" in saved.get("cue", ""):
        failures.append("Some saved sittings are unavailable; their history cannot be joined safely.")
    for row in saved.get("sessions", ()):
        if sum(s.get("session_id") == row["session_id"] for s in saved.get("sessions", ())) != 1:
            failures.append("Saved sittings share an identity. Reconcile them before continuing.")
            continue
        matches = by_path.get(os.path.realpath(row["bank"])) or []
        if len(matches) != 1:
            failures.append("A saved sitting has no unique admitted course route.")
            continue
        stem, path = matches[0]
        try:
            if path not in questions:
                questions[path] = model.load(path)
            selected = _saved_quiz_session(SimpleNamespace(root=root), stem, path, questions[path], cfg={
                "mode": row["mode"], "mode_specific": True,
                "requested_session_id": row["session_id"]})
            if selected is None:
                raise ValueError("saved sitting unavailable")
            sessions[row["session_id"]] = selected[1]
        except (OSError, ValueError, KeyError, TypeError, SystemExit):
            failures.append("A saved sitting is unavailable or changed. Review it before continuing.")
    return saved, sessions, failures


def _current_safe_bindings(course_dir, doc, *, include_unknown=False):
    """Current unambiguous bindings with live source revisions and rights."""
    graph.validate_reading_graph(doc)
    registry = journal.read_registry(course_dir)
    source_ids = {row.get("source_object_id") for row in doc.get("sources") or []}
    superseded = {row.get("supersedes_binding_revision_id")
                  for row in doc.get("bindings") or []}
    rows = []
    states = ("covered", "thin", "unknown") if include_unknown else ("covered", "thin")
    for row in doc.get("bindings") or []:
        if row.get("binding_revision_id") and row["binding_revision_id"] in superseded:
            continue
        source_id = row.get("source_object_id")
        source = registry.get(source_id)
        if (source_id not in source_ids or not source or source.get("kind") != "source"
                or source.get("superseded_by") or row.get("state") not in states
                or journal.object_state(course_dir, source_id) != "clean"
                or (row.get("source_fingerprint") and row["source_fingerprint"] != source.get("fingerprint"))):
            continue
        right = (graph.treatment_right(row["treatment_kind"])
                 if row.get("binding_kind") == "treatment" else "read")
        if course.rights_for_binding(course_dir, source_id, right) == "granted":
            rows.append(row)
    return rows


def _linked_explanation(course_dir, doc, banks, objective, resume):
    """Resolve a current authored treatment through its exact admitted bank."""
    paths = {}
    for stem, path in banks:
        paths.setdefault(os.path.realpath(path), []).append(stem)
    registry = journal.read_registry(course_dir)
    for binding in _current_safe_bindings(course_dir, doc):
        if (binding.get("binding_kind") != "treatment" or binding.get("objective") != objective
                or binding.get("treatment_kind") != "guided-lesson"):
            continue
        locator = binding.get("locator") or ""
        match = re.match(r"^(.+?\.md)(?=$|[\s,;#])", locator.strip(), re.I)
        if match is None:
            continue
        try:
            path = _artifact_path(course_dir, match.group(1))
            stems = paths.get(path) or []
            if len(stems) != 1 or objective not in {q.get("objective") for q in model.load(path)}:
                continue
            lesson = model.parse_lesson(path)
            if not lesson or lesson.get("error") or not lesson.get("headings"):
                continue
            errors, _warnings = model.lint([], lesson=lesson)
            if errors:
                continue
            # Registered teaching artifacts must still be their accepted
            # bytes. An external lesson without a registry cannot prove that.
            lesson_path = os.path.realpath(lesson["source"])
            registered = [oid for oid, row in registry.items()
                          if os.path.realpath(os.path.join(course_dir, row.get("path") or ""))
                          in (path, lesson_path)]
            if (any(journal.object_state(course_dir, oid) != "clean" for oid in registered)
                    or (lesson_path != path and not any(
                        os.path.realpath(os.path.join(course_dir, registry[oid].get("path") or "")) == lesson_path
                        for oid in registered))):
                continue
            query = {"course": doc["header"]["course_object_id"]}
            if binding.get("binding_id"):
                query["occurrence"] = binding["binding_id"]
            if resume:
                query["return"] = resume
            return '/lesson/' + urllib.parse.quote(stems[0], safe='') + '?' + urllib.parse.urlencode(query)
        except (OSError, ValueError, KeyError, TypeError):
            continue
    return None


def _source_first_activity(course_dir, doc, banks):
    """Prefer an accepted reading, then a bound lesson, then bound practice."""
    cid = doc["header"]["course_object_id"]
    # An accepted direct reading can be available while source coverage is
    # still unknown. Availability is not a claim that its objective is covered.
    bindings = _current_safe_bindings(course_dir, doc, include_unknown=True)
    validated = graph.validate_reading_graph(doc)
    superseded = {row["supersedes_revision_id"] for row in validated["occurrences"]}
    binding_ids = {(row.get("binding_id"), row.get("binding_revision_id")) for row in bindings}
    for row in validated["occurrences"]:
        if row["revision_id"] in superseded:
            continue
        ref = row["binding_ref"]
        if (ref["binding_id"], ref["binding_revision_id"]) not in binding_ids:
            continue
        try:
            course.validate_reading_source(course_dir, row["source_ref"])
        except (OSError, ValueError, KeyError, TypeError):
            continue
        return reading_href(cid, row), (row["objective_ids"][0] if row["objective_ids"] else None)
    for objective in doc.get("objectives") or []:
        explanation = _linked_explanation(course_dir, doc, banks, objective["id"], None)
        if explanation:
            return explanation, objective["id"]
    by_path = {}
    for stem, path in banks:
        by_path.setdefault(os.path.realpath(path), []).append(stem)
    for binding in bindings:
        if (binding.get("binding_kind") != "treatment" or binding.get("treatment_kind") != "practice"
                or binding.get("state") not in ("covered", "thin")):
            continue
        match = re.match(r"^(.+?\.md)(?=$|[\s,;#])", (binding.get("locator") or "").strip(), re.I)
        if match is None:
            continue
        try:
            path = _artifact_path(course_dir, match.group(1))
            stems = by_path.get(path) or []
            if len(stems) != 1:
                continue
            qs = model.load(path)
            if binding["objective"] not in {q.get("objective") for q in qs}:
                continue
            errors, _warnings = model.lint(qs, lesson=model.parse_lesson(path))
            if errors:
                continue
            return '/quiz/' + urllib.parse.quote(stems[0], safe='') + '?' + urllib.parse.urlencode(
                {"mode": "practice", "course": cid}), binding["objective"]
        except (OSError, ValueError, KeyError, TypeError):
            continue
    return '/course/' + urllib.parse.quote(cid, safe='') + '/learn', None


def review_history(root, course_dir, doc, banks, cutoff=None):
    """A disposable joined view of saved responses, marks, readings and due work.

    Never emit bank keys or learner answers. The current bank is parsed only
    for the existing saved-sitting admission gate. Detailed feedback remains
    behind that sitting's runtime route and release policy.
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
        issues = []
        try:
            current = list(evidence.live_events(log, diagnostics=issues.append))
            if issues:
                failures.append("Evidence includes unreadable or unsupported records.")
            events.extend(current)
        except (OSError, ValueError, TypeError):
            failures.append("Evidence check failed. Repair the local record, then reload.")
    unique_events = {}
    for event in events:
        eid = event.get("event_id")
        if not isinstance(eid, str) or not eid:
            failures.append("Evidence identity is unavailable; due work cannot be derived safely.")
            continue
        if event.get("session_id") is not None and not isinstance(event["session_id"], str):
            failures.append("Evidence sitting identity is unsupported.")
            continue
        if event.get("event_type") == "mark" and (
                not isinstance(event.get("marks_event"), str) or type(event.get("verdict")) is not bool):
            failures.append("A review mark is unavailable or unsupported.")
            continue
        if eid in unique_events and unique_events[eid] != event:
            failures.append("Divergent records share an evidence identity. Reconcile them before reviewing due work.")
        unique_events[eid] = event
    events = list(unique_events.values())
    # Each admitted bank has its own evidence root. Session identity scopes
    # responses, including older events whose bank field is only a basename.
    saved, sessions, sitting_failures = _admitted_sittings(root, course_dir, banks, events, cid)
    failures.extend(sitting_failures)
    responses = [e for e in events if e.get("event_type") == "response" and
                 e.get("session_id") in sessions and
                 e.get("bank") == os.path.basename(sessions[e["session_id"]]["bank"])]
    for event in responses:
        if (event.get("mode") != sessions[event["session_id"]].get("mode")
                or (event.get("score") is not None and type(event.get("score")) is not bool)
                or not isinstance(event.get("item_ref"), str) or not event.get("item_ref")
                or not isinstance(event.get("objective"), str)):
            failures.append("Response context is unavailable or conflicts with its saved sitting.")
    ids = {e["event_id"] for e in responses}
    relevant = [e for e in events if e.get("event_id") in ids or
                (e.get("session_id") in sessions and e.get("event_type") in ("mark", "hint", "selection"))]
    released = runtime.learner_evidence(relevant, sessions)
    released_ids = {e.get("event_id") for e in released}
    marks = {e.get("marks_event"): e for e in released if e.get("event_type") == "mark"}
    if any(type(mark.get("verdict")) is not bool for mark in marks.values()):
        failures.append("A review mark is unavailable or unsupported.")
    rows, explanation_cache = [], {}
    counts = {"settled": 0, "missed": 0, "pending": 0, "withheld": 0, "reading_reported": 0}
    for event in responses:
        sitting = sessions[event["session_id"]]
        permitted = event["event_id"] in released_ids
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
        if permitted:
            try:
                cache_key = (event.get("objective"), resume)
                if cache_key not in explanation_cache:
                    explanation_cache[cache_key] = _linked_explanation(
                        course_dir, doc, banks, event.get("objective"), resume)
                explanation = explanation_cache[cache_key]
            except (OSError, ValueError, KeyError, TypeError):
                explanation = None
            if explanation:
                links.append({"origin": "Lesson", "label": "Linked explanation", "href": explanation})
        rows.append({"event_id": event["event_id"], "session_id": event["session_id"],
                     "item_ref": event.get("item_ref"), "item_id": event.get("item_id"),
                     "artifact": stem, "mode": event.get("mode"), "objective": event.get("objective"),
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
            "sessions": tuple(s for s in saved.get("sessions", ()) if s["session_id"] in sessions),
            "read_only": True}


def prerequisite_context(root, course_dir, doc, banks, *, course_id=None):
    """Authored relations and released history, without a readiness verdict."""
    objectives = {row['id']: row for row in doc.get('objectives') or []}
    result = {'objectives': {}, 'failures': [], 'read_only': True}
    if not any(edge.get('edge_type') == 'prerequisite-of' for edge in doc.get('edges') or []):
        return result
    try:
        warnings = graph.validate_order(doc)
        result['failures'].extend(warnings)
        history = review_history(root, course_dir, doc, banks)
    except (OSError, ValueError, KeyError, TypeError, graph.GraphError):
        history = {'state': 'error', 'rows': []}
        result['failures'].append('Prerequisite history is unavailable. Review the course and evidence records.')
    cid = urllib.parse.quote(course_id or doc['header']['course_object_id'], safe='')
    for raw in doc.get('edges') or []:
        # Unknown relations remain available in the graph, but cannot be
        # promoted into a prerequisite just because their endpoints match.
        edge = graph.validate_edge(raw)
        if edge['original_type'] != 'prerequisite-of':
            continue
        source, target = edge['source'], edge['target']
        if source not in objectives or target not in objectives or source == target:
            result['failures'].append('A prerequisite has an unresolved objective identity. Repair the course map.')
            continue
        rows = [row for row in history['rows'] if row['objective'] == source]
        counts = {state: sum(row['status'] == state for row in rows)
                  for state in ('pending', 'feedback-withheld', 'missed', 'settled-correct')}
        if history['state'] == 'error':
            description = 'Evidence history is unavailable or incomplete. Review the evidence record.'
        elif not rows:
            description = 'No attributable assessment evidence is recorded for this objective.'
        else:
            description = ('%d settled attempts; %d pending review; %d with feedback withheld. '
                           'These records do not establish readiness or mastery.' % (
                               counts['missed'] + counts['settled-correct'], counts['pending'],
                               counts['feedback-withheld']))
        index = list(objectives).index(source)
        result['objectives'].setdefault(target, []).append(dict(
            edge, title=objectives[source].get('statement') or source,
            href='/course/%s/map#objective-%d' % (cid, index), evidence=description))
    return result


def _due_practice_activity(course_dir, doc, banks, report):
    """Join the existing due order to a current admitted practice treatment."""
    if not report:
        return None
    objectives = {row['id'] for row in doc.get('objectives') or []}
    paths = {}
    for stem, path in banks:
        paths.setdefault(os.path.realpath(path), []).append(stem)
    bindings = _current_safe_bindings(course_dir, doc)
    for due in report.get('due_order') or []:
        objective = due.get('objective')
        summary = (report.get('objectives') or {}).get(objective) or {}
        if objective not in objectives or summary.get('due') is not True:
            continue
        for binding in bindings:
            if (binding.get('objective') != objective or binding.get('binding_kind') != 'treatment'
                    or binding.get('treatment_kind') != 'practice'):
                continue
            match = re.match(r'^(.+?\.md)(?=$|[\s,;#])', (binding.get('locator') or '').strip(), re.I)
            if match is None:
                continue
            try:
                path = _artifact_path(course_dir, match.group(1))
                stems = paths.get(path) or []
                questions = model.load(path)
                errors, _ = model.lint(questions, lesson=model.parse_lesson(path))
                if len(stems) != 1 or errors or objective not in {q.get('objective') for q in questions}:
                    continue
            except (OSError, ValueError, KeyError, TypeError):
                continue
            href = '/course/' + urllib.parse.quote(doc['header']['course_object_id'], safe='') + '/practice?'
            href += urllib.parse.urlencode({'bank': stems[0], 'objective': objective}) + '#course-guidance'
            explanation = summary.get('risk_reason') or 'The configured review interval has elapsed'
            explanation = explanation[:1].upper() + explanation[1:].rstrip('.')
            reason = '%s. Based on %d settled response(s).' % (explanation, summary.get('settled', 0))
            return {'href': href, 'objective': objective, 'reason': reason}
    return None


def course_guidance(root, course_dir, doc, banks):
    """A public next-action projection over admitted, runtime-released history."""
    cid = doc["header"]["course_object_id"]
    review_href = '/course/' + urllib.parse.quote(cid, safe='') + '/evidence#course-review-history'
    start_href = '/course/' + urllib.parse.quote(cid, safe='') + '/learn'

    def result(kind, title, reason, href, objective=None, resume=None):
        out = {"kind": kind, "title": title, "reason": reason, "href": href,
               "objective": objective}
        if resume:
            out["resume_href"] = resume
        return out

    try:
        current = course.read_course(course_dir)
        if current["state"] != "clean" or current["doc"] != doc:
            raise ValueError("course changed or unavailable")
        history = review_history(root, course_dir, doc, banks)
    except (OSError, ValueError, KeyError, TypeError, SystemExit):
        return result("unavailable", "Review the local course record",
                      "The course or its evidence cannot be checked safely. Inspect the local record, then reload.",
                      review_href)
    if history["state"] == "error":
        return result("unavailable", "Check the saved history",
                      "Evidence or saved sittings are incomplete, unavailable or changed. Review them before choosing the next activity.",
                      review_href)
    active = [row for row in history["sessions"] if row["status"] == "active"]
    if len(active) > 1 or history["session_state"] == "ambiguous":
        return result("unavailable", "Choose a saved sitting",
                      "More than one sitting is active. Choose the work you want to continue from the evidence area.",
                      review_href)
    admitted_paths = {os.path.realpath(path): stem for stem, path in banks}
    resume = None
    if active:
        row = active[0]
        stem = admitted_paths[os.path.realpath(row["bank"])]
        resume = '/quiz/' + urllib.parse.quote(stem, safe='') + '?' + urllib.parse.urlencode(
            {"mode": row["mode"], "session": row["session_id"], "course": cid})
    # Log order breaks timestamp ties. Only the newest evidence for the same
    # admitted item can describe its current unresolved work. A correction,
    # pending response or withheld attempt displaces an older miss.
    latest = {}
    try:
        for index, row in enumerate(history["rows"]):
            stamp = datetime.fromisoformat(row["timestamp"])
            if stamp.tzinfo is None:
                raise ValueError("evidence timestamp unavailable")
            rank = (stamp.astimezone(timezone.utc), index)
            key = (row["artifact"], row.get("item_id") or row.get("item_ref"))
            if key not in latest or rank > latest[key][0]:
                latest[key] = (rank, row)
    except (ValueError, TypeError, KeyError):
        return result("unavailable", "Check the saved history",
                      "Evidence timing or item identity is unavailable. Review the local record before choosing an activity.",
                      review_href)
    rows = [row for _rank, row in sorted(latest.values(), key=lambda pair: pair[0], reverse=True)]
    if active:
        # Finish the learner's selected sitting before suggesting older work.
        rows = [row for row in rows if row["session_id"] == active[0]["session_id"]]
    pending = next((row for row in rows if row["status"] == "pending"), None)
    if pending:
        return result("pending", "Review a pending response",
                      "A response is awaiting review. It has no settled mark yet.",
                      review_href, pending.get("objective"), resume)
    missed = next((row for row in rows if row["status"] == "missed"
                   and row["mode"] in ("practice", "drill", "remediation")), None)
    if missed:
        explanation = next((link["href"] for link in missed["context_links"]
                            if link["origin"] == "Lesson"), None)
        return result("review", "Review the linked explanation" if explanation else "Review the released attempt",
                      "The latest released practice attempt for this item was missed. Review its explanation, then return to the saved sitting."
                      if explanation and resume else
                      "The latest released practice attempt for this item was missed. Review the available context before continuing.",
                      explanation or review_href, missed.get("objective"), resume)
    if resume:
        return result("resume", "Resume your saved sitting",
                      "Continue at the saved position. Held assessment feedback stays private until the runtime releases it.",
                      resume, resume=resume)
    due = _due_practice_activity(course_dir, doc, banks, history.get('due'))
    if due:
        return result('due', 'Practice a due objective', due['reason'], due['href'], due['objective'])
    try:
        start_href, objective = _source_first_activity(course_dir, doc, banks)
    except (OSError, ValueError, KeyError, TypeError):
        objective = None
    return result("start", "Start with the source",
                  "Choose an assigned reading or linked lesson. There is not enough unresolved released practice evidence to suggest remediation.",
                  start_href, objective)


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


def source_inventory(course_dir, doc, *, course_id=None):
    """Explicit, bounded course-folder discovery; never register found files."""
    import discovery
    registry = journal.read_registry(course_dir)
    sources = {row['source_object_id']: index for index, row in enumerate(doc.get('sources') or [])}
    registered = {}
    for oid in sources:
        row = registry.get(oid) or {}
        if row.get('kind') == 'source':
            registered.setdefault(row.get('path'), []).append(oid)
    seen = [0]
    def limited():
        seen[0] += 1
        return seen[0] > 128
    report = discovery.run_report([course_dir], approved_roots=[course_dir], cancel=limited,
        max_file_bytes=2 * 1024 * 1024,
        skip_dirs=('.itembank', '_journal', '_attempts', '_evidence', '_notes', '_research', '.git'))
    cid = urllib.parse.quote(course_id or doc['header']['course_object_id'], safe='')
    rows = []
    for entry in report['entries']:
        ids = registered.get(entry['path']) or []
        item = {'path': entry['path'], 'state': entry['state'], 'kind': 'unregistered file', 'href': None}
        if len(ids) == 1:
            index = sources[ids[0]]
            item.update(kind='registered source', href='/course/%s/sources?source=%d#source-%d' % (cid, index, index))
        elif ids:
            item.update(kind='ambiguous source identity')
        rows.append(item)
    return {'rows': rows, 'complete': report['complete'], 'read_only': True}


def source_impact(course_dir, doc, source_id):
    """Read-only exact current assignments, preserving recorded revision identity."""
    registry = journal.read_registry(course_dir)
    row = registry.get(source_id) or {}
    result = {'state': 'unavailable', 'accepted': row.get('fingerprint'), 'current': None,
              'objectives': [], 'readings': [], 'treatments': [], 'issues': [],
              'historical_readings': 0, 'historical_bindings': 0, 'read_only': True}
    if row.get('kind') != 'source':
        result['issues'].append('Source registration unavailable for exact ID: %s' % source_id)
    try:
        if row.get('kind') != 'source':
            raise KeyError(source_id)
        result['state'] = journal.object_state(course_dir, source_id)
        if not identity.rights_granted(row.get('rights'), 'read'):
            result['issues'].append('Current source fingerprint unavailable: read right is not granted.')
            raise PermissionError('Source read right is not granted')
        path = _artifact_path(course_dir, row['path'])
        with open(path, 'rb') as stream:
            raw = stream.read(2 * 1024 * 1024 + 1)
        if len(raw) <= 2 * 1024 * 1024:
            result['current'] = identity.object_fingerprint(raw, 'source')
    except PermissionError:
        pass
    except (OSError, ValueError, KeyError, journal.JournalError):
        result['state'] = 'unavailable'
    superseded = {b.get('supersedes_binding_revision_id') for b in doc.get('bindings') or []}
    current = []
    for binding in doc.get('bindings') or []:
        if binding.get('source_object_id') != source_id:
            continue
        if binding.get('binding_revision_id') in superseded and binding.get('binding_revision_id'):
            result['historical_bindings'] += 1
            continue
        current.append(binding)
    result['objectives'] = list(dict.fromkeys(b.get('objective') for b in current))
    result['treatments'] = [b for b in current if b.get('binding_kind') == 'treatment']
    known_objectives = {o.get('id') for o in doc.get('objectives') or []}
    for oid in result['objectives']:
        if oid not in known_objectives:
            result['issues'].append('Objective link unavailable for exact ID: %s' % oid)
    try:
        manifest = graph.validate_reading_graph(doc)
        old = {r['supersedes_revision_id'] for r in manifest['occurrences']}
        for reading in manifest['occurrences']:
            if reading['source_ref']['source_object_id'] != source_id:
                continue
            if reading['revision_id'] in old:
                result['historical_readings'] += 1
                continue
            if reading['binding_ref']['binding_revision_id'] in superseded:
                result['issues'].append('Reading %s revision %s retains a superseded binding; excluded from current impact.' %
                                        (reading['occurrence_id'], reading['revision_id']))
                continue
            result['readings'].append(reading)
            for oid in reading['objective_ids']:
                if oid not in result['objectives']:
                    result['objectives'].append(oid)
    except (graph.GraphError, ValueError, KeyError):
        result['issues'].append('Reading assignment links unavailable: the accepted reading manifest could not be validated.')
    return result


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
                    if r["revision_id"] not in superseded and
                    r["binding_ref"]["binding_revision_id"] not in superseded_bindings]
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

    def assigned_links(objective=None, source_id=None, exact_binding=None, return_source=None):
        links = []
        for reading in readings:
            if exact_binding is not None:
                ref = reading['binding_ref']
                if (not exact_binding.get('binding_id') or
                        ref['binding_id'] != exact_binding['binding_id'] or
                        ref['binding_revision_id'] != exact_binding.get('binding_revision_id')):
                    continue
            if objective and objective not in reading["objective_ids"]:
                continue
            if source_id and reading["source_ref"]["source_object_id"] != source_id:
                continue
            href = reading_href(state["course_id"], reading)
            if return_source:
                href += '?' + urllib.parse.urlencode({'return_source': return_source})
            links.append('<li>%s</li>' % _link(href, "Open assigned reading"))
        if objective or source_id:
            seen = set()
            for binding in bindings:
                if exact_binding is not None and binding is not exact_binding:
                    continue
                if binding.get("binding_kind") != "treatment" or \
                        (objective and binding.get("objective") != objective) or \
                        (source_id and binding.get("source_object_id") != source_id):
                    continue
                bank = bound_bank(binding)
                if bank is None:
                    continue
                stem, bank_objectives, has_lesson = bank
                kind = binding.get("treatment_kind")
                if binding.get("objective") not in bank_objectives:
                    continue
                if kind == "guided-lesson" and has_lesson:
                    href = '/lesson/' + urllib.parse.quote(stem, safe='')
                    query = {"course": state["course_id"]}
                    if binding.get("binding_id"):
                        query["occurrence"] = binding["binding_id"]
                    if return_source:
                        query['return_source'] = return_source
                    href += '?' + urllib.parse.urlencode(query)
                    label = "Open linked lesson"
                elif kind in ("practice", "formal-test"):
                    mode = "practice" if kind == "practice" else "exam"
                    query = {"mode": mode, "course": state["course_id"]}
                    if return_source:
                        query['return_source'] = return_source
                    href = '/quiz/' + urllib.parse.quote(stem, safe='') + '?' + urllib.parse.urlencode(query)
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
        from surfaces import course_context_view
        course_checks = readiness(course_dir, banks)
        prerequisites = prerequisite_context(handler.root, course_dir, doc, banks, course_id=state['course_id'])
        return_context = course_context_view.prerequisite_return(
            getattr(handler, 'path', ''), doc.get('objectives') or [],
            prerequisites['objectives'], state['course_id'])
        if prerequisites['failures']:
            sections.append('<p role="status">%s</p>' % presentation.esc(
                ' '.join(dict.fromkeys(prerequisites['failures']))))
        for index, row in enumerate(doc.get("objectives") or []):
            oid = row.get("id")
            linked = [b for b in bindings if b.get("objective") == oid]
            items = []
            for b in linked:
                sid = b.get("source_object_id")
                if sid not in source_indexes:
                    continue
                return_id = (return_context['origin'] if return_context and
                             return_context['target'] == oid else oid)
                href = '/course/%s/sources?%s#source-%d' % (
                    cid, urllib.parse.urlencode({'source': source_indexes[sid],
                                                  'return_objective': return_id}),
                    source_indexes[sid])
                treatment = b.get("treatment_kind") or "source support"
                items.append('<li>%s: %s. %s. %s</li>' % (
                    presentation.esc(treatment), _link(href, source_titles[sid]),
                    presentation.esc(b.get("locator") or "Locator unavailable"),
                    presentation.esc(b.get("state") or "State unknown")))
            links = ('<ul>%s</ul>' % ''.join(items) if items else
                     '<p>No current source or treatment binding is recorded for this objective.</p>')
            sections.append(course_context_view.objective_section(
                index, row, prerequisites['objectives'].get(oid, []), links,
                assigned_links(objective=oid), back, return_context))
        sections.append(course_context_view.checks_details(
            course_checks['state'], readiness_panel(course_checks)))
    elif area == "sources":
        from surfaces import course_context_view
        source_return = course_context_view.objective_return(
            getattr(handler, 'path', ''), doc.get('objectives') or [], state['course_id'])
        sections.append('<form method="get" action="/course/%s/sources">'
            '<input type="hidden" name="inventory" value="1">'
            '<button class="go" type="submit">Find files in this course folder</button>'
            '<p>Read-only inventory of up to 128 files, at most 2 MiB each. '
            'Private notes, journal and assessment history folders are excluded. '
            'Finding a file does not register or import it.</p></form>' % cid)
        query = urllib.parse.parse_qs(urllib.parse.urlsplit(getattr(handler, 'path', '')).query)
        if query.get('inventory') == ['1']:
            try:
                inventory = source_inventory(course_dir, doc, course_id=state['course_id'])
                entries = ''.join('<li>%s: %s, %s</li>' % (
                    _link(r['href'], r['path']) if r['href'] else presentation.esc(r['path']),
                    presentation.esc(r['kind']), presentation.esc(r['state'])) for r in inventory['rows'])
                sections.append('<section aria-label="Course file inventory"><h3>Existing files</h3><ul>%s</ul>'
                    '<p>%s</p></section>' % (entries or '<li>No files found.</li>',
                    'Inventory completed within this scope.' if inventory['complete'] else
                    'Inventory stopped at its file limit. Narrow the course folder before another scan.'))
            except (OSError, ValueError, journal.JournalError):
                sections.append('<p role="status">Inventory is unavailable. Repair the course registry and reload.</p>')
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
            preview = ('<h4>Source text</h4><pre class="course-source-text" tabindex="0" '
                       'role="region" aria-label="Source text">%s</pre>' % presentation.esc(text)
                       if text is not None else '<p role="status">%s</p>' % presentation.esc(unavailable))
            impact = source_impact(course_dir, doc, sid)
            if impact['state'] != 'clean':
                from surfaces import course_context_view
                origin_query = urllib.parse.urlencode({'return_source': sid})
                affected = ''.join('<li>%s</li>' % _link('/course/%s/map?%s#objective-%d' %
                    (cid, origin_query, objective_indexes[oid]), objective_titles[oid])
                    for oid in impact['objectives'] if oid in objective_indexes)
                reading_rows = []
                for reading in impact['readings']:
                    reading_rows.append('<li>%s<p>Assigned range: %s.</p>'
                        '<details><summary>Reading revision details</summary>'
                        '<p>Occurrence %s; recorded revision %s; source fingerprint %s.</p>'
                        '<p>Binding %s; recorded binding revision %s.</p></details></li>' % (
                        _link(reading_href(state['course_id'], reading) + '?' + origin_query, 'Inspect assigned reading'),
                        presentation.esc(reading['source_ref']['locator']),
                        presentation.esc(reading['occurrence_id']), presentation.esc(reading['revision_id']),
                        presentation.esc(reading['source_ref']['source_fingerprint']),
                        presentation.esc(reading['binding_ref']['binding_id']),
                        presentation.esc(reading['binding_ref']['binding_revision_id'])))
                treatment_rows = []
                for binding in impact['treatments']:
                    activity = assigned_links(source_id=sid, exact_binding=binding, return_source=sid)
                    if '<li>' not in activity:
                        activity = '<p>Task link unavailable: missing admitted artifact, objective mismatch, or unsupported treatment.</p>'
                    treatment_rows.append('<li>%s: %s%s'
                        '<details><summary>Binding revision details</summary>'
                        '<p>Binding %s; recorded revision %s; source fingerprint %s.</p></details></li>' % (
                        presentation.esc((binding.get('treatment_kind') or 'Unsupported treatment').replace('-', ' ')),
                        presentation.esc(binding.get('locator') or 'Locator unavailable'),
                        activity,
                        presentation.esc(binding.get('binding_id') or 'Legacy binding has no permanent ID'),
                        presentation.esc(binding.get('binding_revision_id') or 'No recorded revision ID'),
                        presentation.esc(binding.get('source_fingerprint') or 'No recorded fingerprint')))
                preview += course_context_view.source_impact(
                    impact, affected, ''.join(reading_rows), ''.join(treatment_rows))
            sections.append('<section id="source-%d" class="course-source-context" tabindex="-1" '
                            'aria-labelledby="source-title-%d">'
                            '<h3 id="source-title-%d">%s</h3>%s<p>%s</p>'
                            '<h4>Objective alignment and treatments</h4>%s%s%s</section>' % (
                                index, index, index,
                                presentation.esc(source_titles[sid]),
                                source_return if selected_source == str(index) else '',
                                presentation.esc(row.get("note") or "Registered course source."),
                                '<ul>%s</ul>' % ''.join(items) if items else
                                '<p>No current objective binding is recorded for this source.</p>',
                                activities + preview, back))
    else:
        from surfaces import retention_view
        sections.append(retention_view.course_review_history(
            review_history(handler.root, course_dir, doc, banks)))
        counts = evidence.course_counts(evidence.log_path(course_dir))
        for key, title, note in (
                ("responses", "Responses", "Recorded attempts include pending and incorrect responses. A count does not imply mastery."),
                ("marks", "Marks", "Settled marks are recorded by the assessment runtime."),
                ("sessions", "Sittings", "Open a saved sitting or its report below.")):
            amount = counts[key]
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
            if counts["state"] == "unavailable":
                status = ('<p role="status">Evidence counts are unavailable until the local '
                          'record can be read. Repair the evidence record, then reload.</p>')
            elif counts["state"] == "incomplete":
                status = ('<p role="status">Evidence history is incomplete. %d live records of this kind '
                          'were read; this count may omit unreadable or unsupported records. '
                          'Inspect the evidence record, then reload.</p>' % amount)
            else:
                status = '<p>%d recorded. %s</p>' % (amount, presentation.esc(note))
            sections.append('<section id="evidence-%s"><h3>%s</h3>%s%s%s</section>' % (
                key, title, status, extra, back))
    return '<div class="course-detail">%s</div>' % ''.join(sections)
