"""Read-only course context for the map, sources, and evidence areas."""

import os
import re
import urllib.parse

import course
import evidence
import graph
import identity
import journal
import model
from surfaces import ia, presentation
from surfaces.reading_desk import href as reading_href


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
        counts = {"responses": 0, "marks": 0, "sessions": set()}
        try:
            for event in evidence.events(evidence.log_path(course_dir)):
                kind = event.get("event_type")
                if kind == "response":
                    counts["responses"] += 1
                elif kind == "mark":
                    counts["marks"] += 1
                if event.get("session_id"):
                    counts["sessions"].add(event["session_id"])
        except (OSError, ValueError):
            pass
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
            sections.append('<section id="evidence-%s"><h3>%s</h3><p>%d recorded. %s</p>%s%s</section>' % (
                key, title, amount, presentation.esc(note), extra, back))
    return '<div class="course-detail">%s</div>' % ''.join(sections)
