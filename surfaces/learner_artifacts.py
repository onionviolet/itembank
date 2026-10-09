"""Native text workbench over NOTE-01 and an existing short-response sitting.

No attachment schema, scorer, provider, runner or new sitting. The daemon
supplies admitted paths. The response event is the immutable submitted text;
its content digest is a derived revision, not a new durable object format.
"""
import hashlib
import json
import os
from urllib.parse import parse_qs, quote, urlencode, urlsplit, urlunsplit

import evidence
import journal
import model
import notes
import runtime
from surfaces import presentation, session

KINDS = ("explanation", "proof", "program", "project")
FIELDS = {"action", "item_ref", "note_id", "session_id", "kind",
          "notes_fingerprint", "note_revision", "bank_revision",
          "content_revision", "wording", "confirmed"}


def form_body(values):
    """Parse singleton form fields. Route/context admission stays in daemon."""
    if set(values) - FIELDS:
        raise journal.JournalError("artifact.fields", "Unexpected artifact form field.")
    result = {}
    for key, value in values.items():
        if isinstance(value, list):
            if len(value) != 1:
                raise journal.JournalError("artifact.fields", "Repeated artifact form field.")
            value = value[0]
        if not isinstance(value, str):
            raise journal.JournalError("artifact.fields", "Artifact form fields must be text.")
        result[key] = value
    return result


def _target(bank_path, item_ref):
    with open(bank_path, "rb") as stream:
        bank_revision = hashlib.sha256(stream.read()).hexdigest()
    qs = model.load(bank_path)
    with open(bank_path, "rb") as stream:
        current_revision = hashlib.sha256(stream.read()).hexdigest()
    if current_revision != bank_revision:
        raise journal.JournalError("artifact.target_changed", "The activity changed while opening it. Keep your wording and reopen the activity.")
    matches = [(index, q) for index, q in enumerate(qs) if q["id"] == item_ref]
    if len(matches) != 1 or matches[0][1]["type"] != "short":
        raise journal.JournalError("artifact.target", "Choose an existing short-response activity.")
    index, q = matches[0]
    target = notes.target_record("item_public", q.get("item_id") or q["id"],
        model.content_fingerprint(q), q["id"], notes.hash_quoted_context(q["stem"]))
    return bank_revision, qs, index, q, target


def _sitting(session_file, bank_path, index):
    if session_file is None:
        return None
    data = runtime.read_session(session_file)
    if (os.path.realpath(data["bank"]) != os.path.realpath(bank_path)
            or data["items"] != [index] or data["mode"] != "practice"
            or data.get("staged_cases")):
        raise journal.JournalError("artifact.sitting", "Use this activity's single-item practice sitting. Formal or multi-item sittings stay on their assessment surface.")
    return data


def _drafts(document, target):
    return [n for n in (document or {}).get("sidecar", {}).get("notes", [])
            if n["authorship"] == "learner" and n["privacy_scope"] == "private"
            and n["status"] == "draft" and any(
                t["target_kind"] == "item_public" and t["stable_id"] == target["stable_id"]
                for t in n["targets"])]


def view(bank_path, note_root, course_id, item_ref, session_file=None,
         note_id=None, kind="explanation"):
    """Read only: expose saved wording and exact response bytes, no keys."""
    if kind not in KINDS:
        raise journal.JournalError("artifact.kind", "Choose text, proof, program or project text.")
    bank_revision, qs, index, q, target = _target(bank_path, item_ref)
    data = _sitting(session_file, bank_path, index)
    document = notes.read_note_document(note_root, course_id)
    drafts = _drafts(document, target)
    draft = next((n for n in drafts if n["note_id"] == note_id), None)
    if note_id and draft is None:
        raise journal.JournalError("artifact.missing", "This draft is unavailable in this activity. Keep your wording.")
    log = evidence.log_path(os.path.dirname(bank_path))
    submitted = []
    all_events = list(evidence.events(log)) if data else []
    retracted = evidence.retracted_ids(log) if data else set()
    for event in all_events:
        if (event.get("session_id") != (data or {}).get("session_id")
                or event.get("item_ref") != item_ref
                or event.get("event_type") != evidence.RESPONSE_EVENT_TYPE
                or event.get("item_type") != "short"):
            continue
        wording = event.get("answer")
        if not isinstance(wording, str):
            raise journal.JournalError("artifact.response", "This older response is not text. Preserve its evidence for review.")
        descriptor = notes.artifact_record(kind, course_id, [event.get("objective", "")], [])
        descriptor.update(artifact_id=event["event_id"], submitted_at=event["ts"])
        state = notes.artifact_evidence_view(descriptor, event["event_id"], log)
        if event["event_id"] in retracted:
            state = {"state": "retracted", "badge": "Submission retracted",
                     "lines": ["Original submitted bytes remain in the local evidence log."]}
        submitted.append({"event_id": event["event_id"], "wording": wording,
            "content_revision": notes.artifact_content_revision(wording),
            "objective": event.get("objective", ""), "submitted_at": event["ts"],
            "review": state, "descriptor": descriptor, 'response_event': event})
    changed = bool(draft and draft["targets"] != [target])
    # Reviewer disclosure uses the runtime's practice feedback policy and
    # requires a real response. This branch never returns the model answer.
    reviewer_allowed = bool(submitted and not changed and data and
                            runtime.assessment_feedback_released(data["mode"], data))
    rubric = runtime.explain_payload(q, reveal=reviewer_allowed).get("rubric", [])
    for row in submitted:
        row["descriptor"]["rubric"] = list(rubric)
        # Export the owner's actual records. A current rubric or matching
        # draft is never relabeled as historical submission provenance.
        related = {row['event_id']}
        history = []
        for event in all_events:
            if (event.get('event_type') == 'mark' and event.get('marks_event') == row['event_id'] or
                    event.get('event_type') == 'retraction' and event.get('retracts') in related):
                history.append(event)
                related.add(event['event_id'])
        row['review_events'] = history
    marks = evidence.marks_by_event(log) if submitted else {}
    mark = marks.get(submitted[0]["event_id"]) if len(submitted) == 1 else None
    return {"course_id": course_id, "item_ref": item_ref, "kind": kind,
        "item": runtime.public_item(q), "objective": q.get("objective", ""),
        "bank_revision": bank_revision,
        "notes_fingerprint": document["fingerprint"] if document else None,
        "draft": draft, "drafts": drafts,
        "content_revision": notes.artifact_content_revision(draft["learner_wording"]) if draft else None,
        "target_changed": changed, "session_id": (data or {}).get("session_id"),
        "session_status": (data or {}).get("status"), "submitted": submitted,
        "rubric": rubric, "rubric_state": "withheld" if not reviewer_allowed else "available" if rubric else "missing",
        "mark_event_id": (mark or {}).get("event_id"),
        "can_submit": bool(draft and data and data["status"] == "active" and
                           data["cursor"] == 0 and not submitted and not changed),
        "export_losses": ["Historical authored rubric and originating draft ID are not recorded in existing response events.",
                          "Text download contains the response bytes only; review lineage remains in local evidence."]}


def apply(action, body, *, bank_path, note_root, course_id, item_ref,
          session_file=None):
    """Apply save/preview/submit/cancel over existing owners, then return view."""
    body = form_body(body)
    if body.get("item_ref", item_ref) != item_ref:
        raise journal.JournalError("artifact.target", "The activity changed. Keep your wording.")
    kind = body.get("kind", "explanation")
    note_id = body.get("note_id") or None
    current = view(bank_path, note_root, course_id, item_ref, session_file, note_id, kind)
    if body.get("session_id", "") != (current["session_id"] or ""):
        raise journal.JournalError("artifact.sitting", "The sitting changed. Reopen this activity.")
    if action in ("cancel", "view"):
        return {"view": current, "preview": False, "message": "Submission cancelled. Saved work is unchanged." if action == "cancel" else ""}
    if action not in ("save", "preview", "submit"):
        raise journal.JournalError("artifact.action", "Unsupported artifact action.")
    if body.get("bank_revision") != current["bank_revision"] or current["target_changed"]:
        raise journal.JournalError("artifact.target_changed", "The authored activity changed. Keep your draft and reconcile its target.")
    fingerprint = body.get("notes_fingerprint") or None
    if fingerprint != current["notes_fingerprint"]:
        raise journal.JournalError("notes.stale", "Notes changed. Keep your wording and reload.")
    draft = current["draft"]
    if draft and body.get("note_revision") != draft["revision_id"]:
        raise journal.JournalError("notes.stale", "This draft changed. Keep your wording and reload.")
    if action == "save":
        bank_revision, qs, index, q, target = _target(bank_path, item_ref)
        if bank_revision != current["bank_revision"]:
            raise journal.JournalError("artifact.target_changed", "The activity changed before saving. Keep your wording and reopen the activity.")
        def validate_target():
            if _target(bank_path, item_ref)[0] != bank_revision:
                raise journal.JournalError("artifact.target_changed", "The activity changed while saving. Keep your wording.")
        saved = notes.save_artifact_draft(note_root, course_id, [q.get("objective", "")],
            target, body.get("wording", ""), expected_fingerprint=fingerprint,
            note_id=note_id, expected_revision=body.get("note_revision"),
            _validate_inputs=validate_target)
        note_id = saved["note"]["note_id"]
        message = "Saved privately. This save did not submit a response."
    else:
        if not draft or body.get("content_revision") != current["content_revision"]:
            raise journal.JournalError("artifact.revision", "Choose and preview an exact saved revision.")
        if current["submitted"]:
            raise journal.JournalError("artifact.already_submitted", "This sitting already has a submission. Later draft edits stay separate.")
        if not current["can_submit"]:
            raise journal.JournalError("artifact.sitting", "Open this activity's active short-response sitting before submitting.")
        if action == "preview":
            return {"view": current, "preview": True, "message": "Review the saved bytes below. No response has been submitted."}
        if body.get("confirmed") != "yes":
            raise journal.JournalError("artifact.confirm", "Confirm this exact saved revision before submitting.")
        # Hold the same private journal lock used by note writers while
        # handing off a captured revision. A competing save cannot swap it.
        with journal._journal_lock(note_root):
            coherent = notes._read_pair(note_root, course_id)
            if coherent is None or coherent["fingerprint"] != fingerprint:
                raise journal.JournalError("notes.stale", "The saved draft changed before submission. Keep your wording.")
            latest = next(n for n in coherent["sidecar"]["notes"] if n["note_id"] == note_id)
            if latest["revision_id"] != draft["revision_id"] or _target(bank_path, item_ref)[0] != current["bank_revision"]:
                raise journal.JournalError("artifact.revision", "The draft or authored target changed before submission.")
            # JSON quoting passes exact text through the existing normalizer,
            # including whitespace and strings which themselves resemble JSON.
            try:
                session.do_action(session_file, {"kind": "submit", "answer": json.dumps(latest["learner_wording"], ensure_ascii=False)})
            except SystemExit as exc:
                raise journal.JournalError("artifact.runtime_refusal", str(exc.code)) from None
        message = "Submitted this exact saved text. Review is pending."
    return {"view": view(bank_path, note_root, course_id, item_ref, session_file, note_id, kind),
            "preview": False, "message": message}


CSS = """
.artifact-workbench{max-width:900px;margin:auto;overflow-wrap:anywhere}
.artifact-workbench textarea{box-sizing:border-box;width:100%;min-height:240px;font:inherit;line-height:1.5;padding:12px;background:var(--card);color:inherit;border:1px solid var(--line)}
.artifact-workbench pre{white-space:pre-wrap;overflow-wrap:anywhere;padding:16px;background:var(--card);border:1px solid var(--line)}
.artifact-workbench label{display:block;margin:12px 0}.artifact-workbench section{margin-block:28px}.artifact-workbench code{overflow-wrap:anywhere;white-space:normal}
.artifact-workbench button,.artifact-workbench .go{margin:8px 8px 8px 0;min-height:44px}
.artifact-workbench :focus-visible{outline:3px solid var(--accent,#477);outline-offset:3px}
@media(max-width:420px){.artifact-workbench pre{padding:10px}.artifact-workbench textarea{min-height:280px}}
"""


def render(view, *, action_url, return_href, panel_href, message="", preview=False,
           preserved_wording=None, reviewer_href=None, objective_label=None, theme_css=None):
    """Render native forms with useful script-free save/preview/cancel paths."""
    esc = presentation.esc
    draft = view["draft"]
    hidden = {"item_ref": view["item_ref"], "kind": view["kind"],
        "session_id": view["session_id"] or "", "note_id": (draft or {}).get("note_id", ""),
        "note_revision": (draft or {}).get("revision_id", ""),
        "notes_fingerprint": view["notes_fingerprint"] or "",
        "bank_revision": view["bank_revision"], "content_revision": view["content_revision"] or ""}
    def form(action, inner):
        fields = dict(hidden, action=action)
        inputs = ''.join('<input type="hidden" name="%s" value="%s">' % (esc(k), esc(v)) for k, v in fields.items())
        return '<form method="post" action="%s">%s%s</form>' % (esc(action_url), inputs, inner)
    text = preserved_wording if preserved_wording is not None else (draft or {}).get("learner_wording", "")
    body = '<div class="artifact-workbench"><p id="artifact-status" role="status" aria-live="polite">%s</p>' % esc(message)
    body += '<p>Objective: %s</p><p>%s</p><p>Original text, proof or program. Programs are stored as text here. Saving is private; submission creates a pending runtime response.</p>' % (esc(objective_label or view["objective"]), esc(view["item"]["stem"]))
    if view["target_changed"]:
        body += '<p role="alert">The authored activity changed. Saved wording remains available; reconcile the target before saving or submitting. Historical rubric disclosure is withheld.</p>'
    if not view["session_id"] and not view["target_changed"]:
        body += form("start", '<label><input type="checkbox" name="confirmed" value="yes" required> Start a single-item practice sitting for this original work.</label><button class="go" type="submit">Start this original-work activity</button><p>This deliberate start records selection, not a response. Your saved draft stays private until you submit it.</p>')
    if view["drafts"]:
        body += '<nav aria-label="Saved drafts">'
        for draft_number, row in enumerate(view["drafts"], start=1):
            parts = urlsplit(panel_href)
            query = parse_qs(parts.query)
            query.update(item_ref=[view["item_ref"]], note_id=[row["note_id"]],
                         session_id=[view["session_id"] or ""], kind=[view["kind"]])
            href = urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query, doseq=True), parts.fragment))
            body += '<a class="go" href="%s"%s>Draft %s</a>' % (esc(href), ' aria-current="page"' if draft and row["note_id"] == draft["note_id"] else '', draft_number)
        body += '</nav>'
    body += '<section aria-labelledby="artifact-draft-heading"><h2 id="artifact-draft-heading">My draft</h2>'
    body += form("save", '<label for="artifact-wording">Your own wording</label><textarea id="artifact-wording" name="wording" required>%s</textarea><button class="go primary" type="submit"%s>Save private draft</button>' % (esc(text), ' disabled' if view["target_changed"] else ''))
    if preserved_wording is not None and draft and preserved_wording != draft["learner_wording"]:
        body += '<details open><summary>Current saved wording after the conflict</summary><p>Your unsaved wording is preserved above. Compare it with this saved revision before saving again.</p><pre>%s</pre></details>' % esc(draft["learner_wording"])
    if draft:
        body += '<p>Saved text revision <code>%s</code></p><details><summary>Saved revision details</summary><p>Note revision <code>%s</code><br>Exact text <code>%s</code></p></details>' % (esc(view["content_revision"][-64:][:8]), esc(draft["revision_id"]), esc(view["content_revision"]))
        if view["can_submit"] and not preview:
            body += form("preview", '<button class="go" type="submit">Preview saved revision for submission</button>')
        elif not view["session_id"]:
            body += '<p>Open this activity’s single-item practice sitting to submit. Saving and reopening do not start a sitting.</p>'
    body += '</section>'
    if preview and draft:
        body += '<section aria-labelledby="artifact-preview-heading"><h2 id="artifact-preview-heading">Submit this saved revision</h2><p>The text below is the exact response. Unsaved editor changes are separate.</p><pre>%s</pre>' % esc(draft["learner_wording"])
        body += form("submit", '<label><input type="checkbox" name="confirmed" value="yes" required> I choose this exact saved revision for pending review.</label><button class="go primary" type="submit">Submit saved revision</button>')
        body += form("cancel", '<button class="go" type="submit">Cancel submission</button>') + '</section>'
    for row_number, row in enumerate(view["submitted"]):
        download = 'data:text/plain;charset=utf-8,' + quote(row["wording"], safe='')
        body += '<section aria-labelledby="artifact-submitted-heading-%s"><h2 id="artifact-submitted-heading-%s">Submitted original</h2><p>%s</p><p>Submitted text revision <code>%s</code></p><details><summary>Submission details</summary><p>Response <code>%s</code><br>Exact text <code>%s</code></p></details><pre>%s</pre>' % (row_number, row_number, esc(row["review"]["badge"]), esc(row["content_revision"][-64:][:8]), esc(row["event_id"]), esc(row["content_revision"]), esc(row["wording"]))
        body += ''.join('<p>%s</p>' % esc(line) for line in row["review"]["lines"])
        if view["content_revision"] != row["content_revision"]:
            body += '<p>The current saved draft differs from this submitted original. Review applies to the original bytes.</p>'
        if view["rubric_state"] == "available":
            body += '<h3>Current authored review criteria</h3><ul>' + ''.join('<li>%s</li>' % esc(point) for point in view["rubric"]) + '</ul>'
        elif view["rubric_state"] == "missing":
            body += '<p>Rubric missing. Submitted bytes are preserved; any recorded reviewer mark remains a separate fact.</p>'
        else:
            body += '<p>Authored rubric withheld for this target revision.</p>'
        body += '<a class="go" download="submitted-original.txt" href="%s">Download exact submitted text</a>' % esc(download)
        details = {'response_event': row['response_event'], 'review_events': row['review_events'],
                   'current_authored_criteria': {'state': view['rubric_state'], 'points': view['rubric']},
                   'limitations': view['export_losses']}
        review_download = 'data:application/json;charset=utf-8,' + quote(json.dumps(details, ensure_ascii=False, indent=2) + '\n', safe='')
        body += '<a class="go" download="original-work-review.json" href="%s">Download current review details</a>' % esc(review_download)
        body += '<p>The review download includes the original response and recorded marks/retractions. Current criteria are labeled separately; missing submission history stays missing.</p>'
        if reviewer_href:
            body += '<a class="go" href="%s">Open sitting reviewer</a>' % esc(reviewer_href)
        body += '<p>Use the existing sitting reviewer to settle this response. Retracting a mark returns its review state to pending.</p></section>'
    if view["submitted"]:
        body += '<details><summary>Download and recovery limits</summary>' + ''.join('<p>%s</p>' % esc(line) for line in view["export_losses"]) + '</details>'
    body += '<a class="go" id="artifact-return" href="%s">Return to course activity</a></div>' % esc(return_href)
    return presentation.surface_shell("My original work", body, theme_css=theme_css or "",
        extra_css=CSS, wide=True, back={"href": return_href, "label": "Return to course activity"},
        noscript="Saving, previewing and cancelling work without JavaScript. Review remains in the existing sitting reviewer.")
