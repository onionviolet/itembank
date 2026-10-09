#!/usr/bin/env python3
"""The Agent area's run-propose-accept machine (plan 17A-07).

One bounded state machine joins the two halves that already shipped:

- a skill run reaches a model only through ``model_adapter.invoke``, the
  single typed boundary. This module opens no socket of its own and adds
  no transport;
- an accepted draft becomes real only through ``journal.commit_operation``,
  the single compare-and-swap writer. This module writes nothing else, and
  the undo path is the prior revision that writer already records.

Four states, no others: ``idle``, ``running``, ``proposed``, ``settled``.
Every public function takes and returns plain state dicts so the page can
render each one without JavaScript.

This module never scores, never marks, never touches keyed assessment
content, and never decides how much of anything to disclose. It proposes
file drafts against a fingerprint, and the learner accepts or rejects.

A run names its write target from the settings document (``agent_runs``
keyed by skill id), never from the model: the model supplies text for a
file the configuration already named, so a stray answer cannot choose
what gets overwritten.
"""
import difflib
import hashlib
import json
import os
import re
import tempfile
import threading
import uuid
from datetime import datetime, timezone

import identity
import director
import journal
import model_adapter


# The whole machine. Anything else a caller sees is a bug.
STATES = ("idle", "running", "proposed", "settled")
RECORD_VERSION = 1
STORE_DIR = ".itembank/agent-proposals"
DISPOSITIONS = ("proposed", "accepted", "rejected", "conflicted", "undone")

# A proposal shows at most this many unified-diff lines. The rest are
# counted in ``diff.withheld`` so the cap is visible, never silent.
DIFF_MAX_LINES = 60

# Autonomy levels that may turn an accepted draft into a journal write.
# Every other value, including a missing setting, reads as report_only:
# restrictive by default, because the shipped default IS report_only.
AUTONOMY_MAY_WRITE = ("draft_and_approve", "audit_draft_lint_fix_commit")

# One named next action per typed unavailable code in
# model_adapter.ADAPTER_CODES. A missing entry is a test failure by
# design, so a new adapter code cannot ship with no copy on the page;
# the import-time check below makes it loud even before the suite runs.
NEXT_ACTIONS = {
    "adapter.cancelled":
        "No draft from this attempt can be accepted. Local transport has ended; "
        "provider work may have occurred. Inspect the request, then retry explicitly if needed.",
    "adapter.profile_disabled":
        "No backend is active. Choose one in Settings, Model, then start "
        "the skill again. Studying, scoring and authored hints are "
        "unaffected and keep working right now.",
    "adapter.profile_invalid":
        "The backend profile has a field this transport does not take "
        "(for example base_url instead of endpoint). Fix the profile in "
        "Settings, Model, then start again.",
    "adapter.profile_unknown":
        "The active backend name no longer matches a configured profile. "
        "Pick the backend again in Settings, Model.",
    "adapter.unreachable":
        "Nothing answered at the endpoint. Start the model server shown "
        "in Settings, Model, then start the skill again. Nothing was "
        "written.",
    "adapter.timeout":
        "The server did not answer in time. Start the skill again, or "
        "raise timeout_seconds on the profile. Nothing was written.",
    "adapter.malformed_response":
        "The endpoint answered with something that is not JSON. Check "
        "that the endpoint URL points at the chat completions address.",
    "adapter.http_error":
        "The endpoint returned an HTTP error. Check the endpoint URL and "
        "any access key the server requires.",
    "adapter.executable_missing":
        "The command this backend runs was not found on this machine. "
        "Install it, or fix the command in Settings, Model.",
    "adapter.subprocess_error":
        "The backend command failed while running. Run it once in a "
        "terminal to see why, then start the skill again.",
    "adapter.provider_refused":
        "The backend refused the request. Check its logs; nothing was "
        "written here.",
    "adapter.request_invalid":
        "itembank built a request the model boundary rejected. This is a "
        "bug in itembank, not something you did. Nothing was written.",
    "adapter.output_cap_exceeded":
        "The answer was longer than the profile allows. Raise "
        "max_output_bytes in Settings, Model, or ask for a smaller "
        "draft.",
    "adapter.transport_unknown":
        "The profile names a transport this build does not ship. Choose "
        "a listed transport in Settings, Model.",
    "adapter.internal_error":
        "Something failed unexpectedly inside the model boundary. "
        "Nothing was written. Start the skill again.",
}

for _code in model_adapter.ADAPTER_CODES:
    if _code not in NEXT_ACTIONS:
        raise RuntimeError(
            "adapter code %r shipped with no next-action copy; add it to "
            "surfaces.agent_operation.NEXT_ACTIONS" % (_code,))

# What each state means, in the page's words. Rendered verbatim by the
# Agent tab so the screen explains the machine instead of hiding it.
STATE_COPY = {
    "idle":
        "Nothing is running. Pick a skill below to start one.",
    "running":
        "The skill is at the model boundary. It comes back as a proposal "
        "or as a typed unavailable, never as a half-written file.",
    "proposed":
        "The draft is shown as a bounded diff against the file as it "
        "stands, with its citations. Accept writes once through the "
        "journal; Reject writes nothing.",
    "settled":
        "The run is over: either one journalled change you can undo, or "
        "a typed reason and the next action to take.",
}


def idle():
    """The resting state, rendered before any skill runs."""
    return {"state": "idle", "skill": None, "note": STATE_COPY["idle"]}


def _now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _store(base):
    return os.path.join(os.path.abspath(base), STORE_DIR)


def _record_path(base, proposal_id):
    if not isinstance(proposal_id, str) or not proposal_id.startswith("p_") \
            or not proposal_id[2:].isalnum():
        raise ValueError("agent.invalid_proposal_id")
    return os.path.join(_store(base), proposal_id + ".json")


def _write_record(base, record):
    directory = _store(base)
    os.makedirs(directory, exist_ok=True)
    path = _record_path(base, record["proposal_id"])
    raw = (json.dumps(record, ensure_ascii=False, indent=2,
                      sort_keys=True) + "\n").encode("utf-8")
    fd, temporary = tempfile.mkstemp(prefix=".proposal-", dir=directory)
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(raw)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return record


def _unavailable(proposal_id, code, reason):
    return {"schema_version": RECORD_VERSION, "state": "unavailable",
            "disposition": "unavailable", "proposal_id": proposal_id,
            "code": code, "reason": reason,
            "next_action": "Start a new proposal. The unreadable record was preserved."}


def status(base, proposal_id):
    """Read one durable proposal without allowing a malformed record to
    break the course surface."""
    try:
        path = _record_path(base, proposal_id)
        with open(path, encoding="utf-8") as fh:
            record = json.load(fh)
    except FileNotFoundError:
        return _unavailable(proposal_id, "agent.proposal_not_found",
                            "No stored proposal has that identity.")
    except (OSError, ValueError, json.JSONDecodeError):
        return _unavailable(proposal_id, "agent.proposal_malformed",
                            "The stored proposal could not be read.")
    if not isinstance(record, dict) or record.get("schema_version") != RECORD_VERSION:
        return _unavailable(proposal_id, "agent.proposal_version_unavailable",
                            "This build cannot read the stored proposal version.")
    if record.get("proposal_id") != proposal_id \
            or record.get("disposition") not in DISPOSITIONS:
        return _unavailable(proposal_id, "agent.proposal_malformed",
                            "The stored proposal is missing required lifecycle fields.")
    return record


def proposals(base):
    """Return every readable record plus typed unavailable rows, newest first."""
    directory = _store(base)
    try:
        names = [n[:-5] for n in os.listdir(directory)
                 if n.startswith("p_") and n.endswith(".json")]
    except OSError:
        return []
    rows = [status(base, name) for name in names]
    return sorted(rows, key=lambda row: row.get("updated_at") or "", reverse=True)


def pending(base):
    return [row for row in proposals(base)
            if row.get("disposition") == "proposed"]


def request_history(base):
    """Project author requests from the existing director checkpoints.

    A receipt without a proposal or completion has unknown transport outcome,
    including after restart. It never proves a provider did no work.
    """
    requests = {}
    for entry in journal.entries(base):
        agent = entry.get("agent") or {}
        checkpoint = agent.get("checkpoint") or {}
        if not isinstance(checkpoint, dict) or checkpoint.get("client") != "agent-operation":
            continue
        operation_id = agent.get("operation_id")
        if not operation_id:
            continue
        row = dict(checkpoint, operation_id=operation_id,
                   updated_at=entry.get("timestamp"))
        requests[operation_id] = row
    rows = []
    for row in requests.values():
        proposal = status(base, row.get("proposal_id"))
        if proposal.get("disposition") in DISPOSITIONS:
            row.update(request_state=proposal["disposition"],
                       next_action="Review the saved proposal. Do not repeat the provider request.")
        elif row.get("request_state") == "started":
            with _JOB_LOCK:
                job = _RUNNING.get((os.path.realpath(base), row.get('proposal_id')))
                if job is not None:
                    row.update(request_state='cancel-requested' if job['cancel'].is_set() else 'running',
                        next_action='Cancellation requested; wait for transport completion.' if job['cancel'].is_set()
                        else 'Refresh for progress or cancel this request. Accepted files are unchanged.')
                else:
                    row.update(request_state="unresolved", code="agent.request_unresolved",
                               next_action="Refresh and check the provider before starting again. The request may still be running or have been interrupted; retry may repeat provider work and cost. No accepted file changed.")
        rows.append(row)
    return sorted(rows, key=lambda row: row.get("updated_at") or "", reverse=True)


def propose_staged_cases(base, target, cases, expected_bank_fingerprint):
    """Propose one local bank-header edit through the existing revision route."""
    import model
    if (not isinstance(target, str) or not target or os.path.isabs(target)
            or ".." in target.replace("\\", "/").split("/")):
        raise ValueError("agent.staged_target_invalid")
    path = os.path.realpath(os.path.join(base, target))
    if os.path.commonpath([os.path.realpath(base), path]) != os.path.realpath(base):
        raise ValueError("agent.staged_target_invalid")
    with open(path, "rb") as stream:
        raw = stream.read()
    fingerprint = identity.object_fingerprint(raw, "bank")
    if not expected_bank_fingerprint or fingerprint != expected_bank_fingerprint:
        raise ValueError("agent.target_stale")
    text = raw.decode("utf-8")
    questions = model.parse_bank(text)
    if model.staged_case_spec_errors(questions):
        raise ValueError("agent.staged_existing_invalid")
    header, rest = re.split(r"(?m)(?=^Q\d+\.)", text, maxsplit=1)
    declaration = "STAGED-CASES: " + json.dumps(cases, ensure_ascii=False, separators=(",", ":"))
    if re.search(r"(?m)^STAGED-CASES:.*$", header):
        header = re.sub(r"(?m)^STAGED-CASES:.*$", lambda _: declaration, header)
    else:
        header += ("" if not header or header.endswith("\n") else "\n") + declaration + "\n"
    draft = header + rest
    errors, _ = model.lint(model.parse_bank(draft))
    if errors:
        raise ValueError("agent.staged_draft_invalid: " + errors[0].message)
    created = _now()
    record = {"schema_version": RECORD_VERSION, "state": "proposed", "disposition": "proposed",
              "proposal_id": "p_" + uuid.uuid4().hex, "operation_id": "op_" + uuid.uuid4().hex,
              "skill": "staged-cases", "interaction_id": None, "target": target, "kind": "bank",
              "draft": draft, "citations": [], "source_paths": [], "source_fingerprints": {},
              "expected_fingerprint": fingerprint, "diff": _bounded_diff(target, raw, draft),
              "provider": {"kind": "local-edit", "egress": "none"},
              "validation": {"state": "valid", "findings": []},
              "egress": {"destination": "local", "spans": []}, "created_at": created,
              "updated_at": created, "next_action": "Review staged declaration and unchanged question blocks"}
    return _write_record(base, record)


def propose_course_outline(base, treatments, order=None, proposal_id=None,
                           expected_draft_fingerprint=None,
                           expected_course_fingerprint=None):
    """Local editable proposal, preserving accepted bindings and objective IDs.

    Treatments are additive. In particular an adequate direct reading is never
    replaced by a generated lesson. No source text leaves the machine.
    """
    import course
    import graph

    read = course.read_course(base)
    if read["state"] != "clean":
        raise ValueError("agent.course_not_clean")
    if expected_course_fingerprint is not None and expected_course_fingerprint != read["fingerprint"]:
        raise ValueError("agent.course_stale")
    prior = status(base, proposal_id) if proposal_id else None
    if prior:
        if prior.get("skill") != "course-outline" or prior.get("disposition") != "proposed":
            raise ValueError("agent.course_proposal_settled")
        if expected_draft_fingerprint != draft_fingerprint(prior["draft"]):
            raise ValueError("agent.draft_stale")
        if prior["expected_fingerprint"] != read["fingerprint"]:
            raise ValueError("agent.course_stale")
        if _source_fingerprints(base, prior["source_paths"]) != prior["source_fingerprints"]:
            raise ValueError("agent.source_stale")
    doc = read["doc"]
    ids = [row["id"] for row in doc["objectives"]]
    if order is not None:
        if len(order) != len(ids) or set(order) != set(ids):
            raise ValueError("agent.outline_identity_change")
        for row in doc["objectives"]:
            if row.get("origin") == "imported":
                if order.index(row["id"]) != ids.index(row["id"]):
                    raise ValueError("agent.imported_outline_immutable")
                continue
            row["order"] = str(order.index(row["id"]) + 1)
        doc["objectives"].sort(key=lambda row: order.index(row["id"]))
    sources = {row["source_object_id"] for row in doc["sources"]}
    registry = journal.read_registry(base)
    source_paths = set()
    for binding in doc["bindings"]:
        if binding.get("treatment_kind") != "direct-reading":
            continue
        sid = binding["source_object_id"]
        source = registry.get(sid) or {}
        if source.get("kind") != "source" or journal.object_state(base, sid) != "clean":
            raise ValueError("agent.source_not_clean")
        if course.rights_for_binding(base, sid, "read") != "granted":
            raise ValueError("agent.treatment_right_not_granted")
        source_paths.add(source["path"])
    choices = []
    for choice in treatments:
        if set(choice) != {"objective", "source", "treatment", "locator"}:
            raise ValueError("agent.invalid_treatment_choice")
        if not all(isinstance(value, str) for value in choice.values()) or not choice["locator"].strip():
            raise ValueError("agent.invalid_treatment_choice")
        if choice["objective"] not in ids or choice["source"] not in sources:
            raise ValueError("agent.unknown_treatment_endpoint")
        right = graph.treatment_right(choice["treatment"])
        if course.rights_for_binding(base, choice["source"], right) != "granted":
            raise ValueError("agent.treatment_right_not_granted")
        source = registry.get(choice["source"]) or {}
        if source.get("kind") != "source" or journal.object_state(base, choice["source"]) != "clean":
            raise ValueError("agent.source_not_clean")
        source_paths.add(source["path"])
        existing = any(row.get("binding_kind") == "treatment" and
                       row.get("objective") == choice["objective"] and
                       row.get("source_object_id") == choice["source"] and
                       row.get("treatment_kind") == choice["treatment"] and
                       row.get("locator") == choice["locator"] for row in doc["bindings"])
        if not existing:
            graph.add_binding(doc, "treatment", choice["objective"], choice["source"],
                              treatment_kind=choice["treatment"], locator=choice["locator"],
                              state="unknown", confidence="unknown", rights_snapshot="granted")
        choices.append(dict(choice))
    draft = graph.serialize_course(doc)
    graph.parse_course(draft)
    record = {"schema_version": RECORD_VERSION, "proposal_id": proposal_id or "p_" + uuid.uuid4().hex,
              "state": "proposed", "disposition": "proposed", "skill": "course-outline",
              "kind": "course", "target": course.COURSE_SIDECAR_FILENAME,
              "interaction_id": None, "expected_fingerprint": read["fingerprint"],
              "source_paths": sorted(source_paths),
              "source_fingerprints": _source_fingerprints(base, sorted(source_paths)),
              "draft": draft, "treatment_choices": choices,
              "diff": _bounded_diff(course.COURSE_SIDECAR_FILENAME, read["text"].encode("utf-8"), draft),
              "validation": {"state": "passed", "findings": graph.validate_order(doc)},
              "citations": [choice["source"] + ": " + choice["locator"] for choice in choices],
              "provider": {"kind": "local-edit", "egress": "none"}, "updated_at": _now(),
              "next_action": "Review the outline and additive treatments, then accept or cancel"}
    return _write_record(base, record)


def _validate_course_proposal(base, state):
    """Re-read binding rights at acceptance, never trust the proposal snapshot."""
    import course
    import graph

    doc = graph.parse_course(state["draft"])
    if _source_fingerprints(base, state.get("source_paths") or []) != state.get("source_fingerprints"):
        raise journal.JournalError("agent.source_stale", "The source changed during review.")
    for choice in state.get("treatment_choices") or []:
        right = graph.treatment_right(choice["treatment"])
        if course.rights_for_binding(base, choice["source"], right) != "granted":
            raise journal.JournalError("agent.treatment_right_not_granted",
                                       "The treatment right changed. Review the source rights again.")
    for binding in doc["bindings"]:
        if binding.get("treatment_kind") == "direct-reading" and course.rights_for_binding(base, binding["source_object_id"], "read") != "granted":
            raise journal.JournalError("agent.treatment_right_not_granted",
                                       "The direct reading's read right changed. Review the source rights again.")


def _settled(iid, skill, code, reason, **extra):
    state = {"state": "settled", "ok": False, "skill": skill,
             "interaction_id": iid, "code": code, "reason": reason,
             "entry_id": None, "conflict": False}
    state.update(extra)
    return state


def _run_spec(skill, settings):
    """The write target for this skill, taken from the settings document
    and never from the model. Returns None when the skill has none."""
    runs = (settings or {}).get("agent_runs") or {}
    spec = runs.get(skill)
    if not isinstance(spec, dict) or not spec.get("target"):
        return None
    kind = spec.get("kind") or "bank"
    if kind not in identity.OBJECT_KINDS:
        return None
    target = str(spec["target"])
    if os.path.isabs(target) or ".." in target.replace("\\", "/").split("/"):
        return None
    request = spec.get("request") or "Draft the configured target."
    citations = [str(value) for value in (spec.get("citations") or [])]
    source_paths = spec.get("source_paths") or []
    if not isinstance(source_paths, list) or any(
            not isinstance(path, str) or not path or os.path.isabs(path) or
            ".." in path.replace("\\", "/").split("/")
            for path in source_paths):
        return None
    return {"target": target, "kind": kind,
            "request": str(request), "citations": citations,
            "source_paths": source_paths}


def _source_fingerprints(base, paths):
    """Hash only explicitly configured course-local source files."""
    result = {}
    root = os.path.realpath(base)
    for rel in paths:
        path = os.path.realpath(os.path.join(root, rel))
        if os.path.commonpath((root, path)) != root:
            raise ValueError("agent.source_outside_course")
        with open(path, "rb") as fh:
            result[rel] = hashlib.sha256(fh.read()).hexdigest()
    return result


def _bounded_diff(rel, before_raw, draft):
    """A capped unified diff of the draft against the current bytes. The
    withheld count travels with the shown lines, so a truncation is a
    stated fact rather than a silent one."""
    before = before_raw.decode("utf-8", errors="replace").splitlines()
    after = draft.splitlines()
    full = list(difflib.unified_diff(
        before, after,
        fromfile="current/%s" % rel, tofile="draft/%s" % rel,
        lineterm=""))
    shown = full[:DIFF_MAX_LINES]
    return {"lines": shown, "shown": len(shown), "total": len(full),
            "withheld": max(0, len(full) - len(shown))}


def draft_fingerprint(draft):
    """Version token for a pending draft, independent of accepted content."""
    return hashlib.sha256(draft.encode("utf-8")).hexdigest()


def _lesson_preview_body(draft):
    """Return only teaching prose from a standalone lesson draft.

    Assessment markers are refused before rendering so a proposed lesson
    cannot turn the review surface into an early answer-key disclosure.
    """
    if not re.search(r"(?m)^## LESSON\s*$", draft):
        raise ValueError("agent.lesson_section_missing")
    marker = re.search(r"(?m)^## LESSON\s*$", draft)
    body = draft[marker.end():]
    if not re.search(r"(?m)^###\s+\S", body):
        raise ValueError("agent.lesson_heading_missing")
    # The plain preview also shows the preamble, so guard both sides of the
    # one allowed section marker before returning any preview content.
    preview_text = draft[:marker.start()] + body
    if re.search(r"(?im)^\s*(?:##\s+\S|Q\d+\.|CORRECT:|ANSWER:|KEY:|\[!KEY\])", preview_text):
        raise ValueError("agent.lesson_keyed_content")
    return body.strip()


def lesson_preview(base, proposal_id):
    """Render a pending lesson through the learner's Markdown renderer.

    This reads the durable proposal, not the accepted target. The returned
    Markdown is the exact draft and the HTML is teaching prose only.
    """
    record = status(base, proposal_id)
    if record.get("disposition") != "proposed" or record.get("kind") != "lesson":
        raise ValueError("agent.lesson_preview_unavailable")
    body = _lesson_preview_body(record["draft"])
    from surfaces import lesson
    return {"proposal_id": proposal_id,
            "draft_fingerprint": draft_fingerprint(record["draft"]),
            "markdown": record["draft"],
            "html": lesson.render_markdown(body),
            "citations": list(record.get("citations") or []),
            "diff": record.get("diff")}


def revise(base, proposal_id, before_paragraph, after_paragraph,
           expected_draft_fingerprint):
    """Correct exactly one paragraph in a pending lesson proposal.

    The caller supplies the draft token it reviewed. A stale edit or an
    ambiguous paragraph is refused, and accepted target bytes never change.
    """
    record = status(base, proposal_id)
    if record.get("disposition") != "proposed" or record.get("kind") != "lesson":
        raise ValueError("agent.lesson_revision_unavailable")
    draft = record["draft"]
    if draft_fingerprint(draft) != expected_draft_fingerprint:
        raise ValueError("agent.draft_stale")
    try:
        sources_now = _source_fingerprints(base, record.get("source_paths") or [])
    except (OSError, ValueError):
        raise ValueError("agent.source_stale") from None
    if sources_now != (record.get("source_fingerprints") or {}):
        raise ValueError("agent.source_stale")
    if not isinstance(before_paragraph, str) or not before_paragraph.strip() \
            or not isinstance(after_paragraph, str) or not after_paragraph.strip():
        raise ValueError("agent.paragraph_empty")
    if "\n\n" in before_paragraph or "\n\n" in after_paragraph:
        raise ValueError("agent.paragraph_not_single")
    paragraphs = [part.strip() for part in draft.split("\n\n")]
    if paragraphs.count(before_paragraph.strip()) != 1 or \
            draft.count(before_paragraph) != 1 or \
            re.match(r"^#{1,6}\s", before_paragraph.strip()) or \
            re.match(r"^#{1,6}\s", after_paragraph.strip()):
        raise ValueError("agent.paragraph_ambiguous")
    updated = draft.replace(before_paragraph, after_paragraph, 1)
    _lesson_preview_body(updated)
    target = os.path.join(os.path.abspath(base), record["target"])
    try:
        with open(target, "rb") as fh:
            current = fh.read()
    except FileNotFoundError:
        current = None
    current_fingerprint = (identity.object_fingerprint(current, "lesson")
                           if current is not None else None)
    if current_fingerprint != record.get("expected_fingerprint"):
        raise ValueError("agent.target_stale")
    record.update({"draft": updated,
                   "diff": _bounded_diff(record["target"], current or b"", updated),
                   "validation": {"state": "not_run", "findings": []},
                   "updated_at": _now(),
                   "next_action": "Review corrected proposal"})
    return _write_record(base, record)


def _author_payload(skill, spec):
    """The bounded author request the adapter schema requires: the public
    format contract, the bounded request (here, which configured skill
    and file to draft for), the attempt number, and empty findings. No
    repository contents ride along."""
    import model
    contract = model.SPEC
    if spec["kind"] == "lesson":
        contract = (
            "A lesson is portable UTF-8 Markdown. It must remain coherent in "
            "a plain Markdown reader, use ## LESSON and ### section headings, "
            "retain source links and attribution, label generated synthesis, "
            "and contain no answer key or scoring decision.")
    return {
        "schema_version": 1,
        "contract": contract,
        "request": {"stage": "agent_proposal", "skill": skill,
                    "target": spec["target"],
                    "instruction": spec["request"],
                    "citations": spec["citations"]},
        "attempt": 1,
        "findings": [],
    }


_JOB_LOCK = threading.RLock()
_RUNNING = {}


class AgentRequestError(ValueError):
    """A safe request refusal shared by the native form, API and CLI."""
    def __init__(self, code, message):
        self.code, self.message = code, message
        super().__init__(code + ': ' + message)


def start_background(skill, settings, base, *, retry_of=None):
    """Run the existing proposal machine with process-local transport ownership.

    Durable recovery is the director receipt, never this disposable handle.
    A vanished handle after restart leaves the provider outcome unresolved.
    """
    base = os.path.realpath(base)
    if model_adapter.resolve_profile(settings or {})[0] is None:
        return start(skill, settings, base)
    pid = 'p_' + uuid.uuid4().hex
    ready = threading.Event()
    job = {'cancel': threading.Event(), 'done': threading.Event(), 'result': None}
    with _JOB_LOCK:
        if any(key[0] == base for key in _RUNNING):
            raise AgentRequestError('agent.request_running', 'Finish or cancel the current course request first.')
        _RUNNING[(base, pid)] = job
    def run():
        try:
            job['result'] = start(skill, settings, base, cancel=job['cancel'],
                proposal_id=pid, retry_of=retry_of, on_started=lambda _row: ready.set())
        except Exception:
            job['result'] = {'state': 'settled', 'proposal_id': pid,
                'code': 'agent.request_unresolved',
                'next_action': 'Inspect request history. The provider outcome is unknown; no automatic retry will run.'}
        finally:
            with _JOB_LOCK:
                _RUNNING.pop((base, pid), None)
            job['done'].set()
            ready.set()
    threading.Thread(target=run, name='itembank-author', daemon=True).start()
    ready.wait(1)
    return job['result'] or {'state': 'running', 'proposal_id': pid,
        'next_action': 'Refresh for progress or cancel this request.'}


def cancel_request(base, proposal_id):
    """Request cancellation of one owned live transport; never accept a late draft."""
    with _JOB_LOCK:
        if status(base, proposal_id).get('disposition') in DISPOSITIONS:
            raise AgentRequestError('agent.request_finished', 'Inspect the saved proposal; its transport has already ended.')
        job = _RUNNING.get((os.path.realpath(base), proposal_id))
        if job is None:
            raise AgentRequestError('agent.transport_unowned', 'Inspect request history; its provider outcome is unknown.')
        job['cancel'].set()
    return {'state': 'running', 'proposal_id': proposal_id, 'request_state': 'cancel-requested',
            'next_action': 'Refresh until the transport ends. Accepted files are unchanged.'}


def wait_request(base, proposal_id, timeout=None):
    """Keep a CLI owner alive until its transport ends; never replay a receipt."""
    with _JOB_LOCK:
        job = _RUNNING.get((os.path.realpath(base), proposal_id))
    if job is not None:
        if job['done'].wait(timeout):
            return job['result']
        return {'state': 'running', 'proposal_id': proposal_id,
                'next_action': 'Transport outcome remains unresolved. Inspect request history before retrying.'}
    proposal = status(base, proposal_id)
    if proposal.get('disposition') in DISPOSITIONS:
        return proposal
    receipt = next((row for row in request_history(base) if row.get('proposal_id') == proposal_id), None)
    return dict(receipt or proposal, state='settled')


def retry_request(base, proposal_id, settings):
    """Explicit new attempt linked to its receipt, with fresh source/base admission."""
    rows = [row for row in request_history(base) if row.get('proposal_id') == proposal_id]
    if len(rows) != 1 or rows[0]['request_state'] not in ('settled', 'unresolved'):
        raise AgentRequestError('agent.retry_unavailable', 'Inspect the existing request or saved proposal first.')
    return start_background(rows[0]['skill'], settings, base, retry_of=rows[0]['operation_id'])


def start(skill, settings, base, *, cancel=None, proposal_id=None, retry_of=None, on_started=None):
    """Run one skill: build the bounded request, invoke the boundary, and
    land in exactly one of two places. An ok result becomes a ``proposed``
    state carrying the draft, its citations, and a bounded diff against
    the current bytes of the target file. Any unavailable result becomes
    a ``settled`` state carrying the typed code, the adapter's message,
    and the next action named in NEXT_ACTIONS."""
    iid = "agent-%s-%s" % (skill, uuid.uuid4().hex[:12])
    base = os.path.abspath(base)

    spec = _run_spec(skill, settings)
    if spec is None:
        return _settled(
            iid, skill, "agent.no_run_target",
            "The skill '%s' has no file to draft into. Add an "
            "agent_runs.%s.target entry to itembank.json naming the file "
            "inside the course directory this skill should draft."
            % (skill, skill))

    try:
        source_fingerprints = _source_fingerprints(base, spec["source_paths"])
    except (OSError, ValueError):
        return _settled(iid, skill, "agent.source_unavailable",
                        "A configured source is missing or outside the course. "
                        "Check source_paths and start again. Nothing was written.")

    request = model_adapter.request_from_operation(
        "author", iid, "",
        author_request=_author_payload(skill, spec))
    if model_adapter.resolve_profile(settings or {})[0] is None:
        # A disabled or invalid profile cannot start provider work. Keep the
        # existing first-use refusal read-only and use the adapter's code.
        result = model_adapter.invoke(request, settings or {})
        error = result.get("error") or {}
        code = error.get("code")
        return _settled(iid, skill, code, error.get("message"),
                        next_action=NEXT_ACTIONS[code], message=error.get("message"))
    proposal_id = proposal_id or "p_" + uuid.uuid4().hex
    operation_id = "op_" + uuid.uuid4().hex
    checkpoint = {"client": "agent-operation", "proposal_id": proposal_id,
                  "interaction_id": iid, "skill": skill, "target": spec["target"],
                  "source_fingerprints": source_fingerprints,
                  "request_state": "started"}
    if retry_of:
        checkpoint['retry_of'] = retry_of
    target_path = os.path.join(base, spec['target'])
    raw = None
    if os.path.exists(target_path):
        with open(target_path, 'rb') as stream:
            raw = stream.read()
    director.begin_operation(base, base, "Draft configured target: " + spec["target"],
                             "agent", skill, "course-builder",
                             (settings or {}).get("auditor_autonomy") or "report_only",
                             scopes=spec["source_paths"], operation_id=operation_id,
                             checkpoint=checkpoint)
    if on_started is not None:
        on_started(checkpoint)

    def settle(*args, **kwargs):
        outcome = _settled(*args, **kwargs)
        receipt = dict(checkpoint, request_state="settled", code=outcome.get("code"),
                       next_action=outcome.get("next_action") or outcome.get("reason"))
        director.record_phase(base, operation_id, "report", 12, "applied",
                              "agent", skill, checkpoint=receipt)
        return dict(outcome, operation_id=operation_id, proposal_id=proposal_id)

    # On interruption the started receipt remains unresolved. Do not claim a
    # hosted call had no external effect or retry it automatically.
    result = (model_adapter.invoke(request, settings or {}, cancel=cancel) if cancel is not None
              else model_adapter.invoke(request, settings or {}))

    if result.get("status") != "ok":
        error = result.get("error") or {}
        code = error.get("code")
        # Indexing directly, not .get(): a missing entry is a failure to
        # fix in the map above, never a silent fallback.
        return settle(iid, skill, code, error.get("message"),
                        next_action=NEXT_ACTIONS[code],
                        message=error.get("message"))

    candidate = result.get("candidate")
    if not isinstance(candidate, dict) \
            or not isinstance(candidate.get("draft"), str) \
            or not isinstance(candidate.get("citations"), list):
        return settle(
            iid, skill, "agent.candidate_invalid",
            "The backend answered, but not with a draft this page can "
            "propose (it needs JSON with a draft string and a citations "
            "list). Check the endpoint serves this skill's output "
            "format.")

    draft = candidate["draft"]
    citations = [str(c) for c in candidate["citations"]]
    try:
        source_now = _source_fingerprints(base, spec["source_paths"])
    except (OSError, ValueError):
        source_now = None
    if source_now != source_fingerprints:
        return settle(iid, skill, "agent.source_stale",
                        "A configured source changed during drafting. "
                        "Review it and start again. Nothing was written.")
    if spec["kind"] == "lesson":
        try:
            _lesson_preview_body(draft)
        except ValueError as exc:
            return settle(iid, skill, str(exc),
                            "The lesson draft cannot be previewed safely. "
                            "Correct the model request and start again. "
                            "Nothing was written.")
        if not citations or any(c not in spec["citations"] for c in citations):
            return settle(iid, skill, "agent.citations_unverified",
                            "The draft citations do not match the configured "
                            "sources. Check source bindings and start again. "
                            "Nothing was written.")
    created = _now()
    record = {
        "schema_version": RECORD_VERSION,
        "state": "proposed",
        "disposition": "proposed",
        "proposal_id": proposal_id,
        "operation_id": operation_id,
        "skill": skill,
        "interaction_id": iid,
        "target": spec["target"],
        "kind": spec["kind"],
        "draft": draft,
        "citations": citations,
        "source_paths": spec["source_paths"],
        "source_fingerprints": source_fingerprints,
        "expected_fingerprint":
            identity.object_fingerprint(raw, spec["kind"])
            if raw is not None else None,
        "diff": _bounded_diff(spec["target"], raw or b"", draft),
        "provider": result.get("provider"),
        "validation": candidate.get("validation") or {"state": "not_run", "findings": []},
        "egress": result.get("egress") or {"destination": "local", "spans": []},
        "created_at": created,
        "updated_at": created,
        "next_action": "Review proposal",
    }
    with _JOB_LOCK:
        if cancel is not None and cancel.is_set():
            return settle(iid, skill, 'adapter.cancelled', 'Cancelled draft discarded.',
                          next_action=NEXT_ACTIONS['adapter.cancelled'])
        _write_record(base, record)
    # Compatibility for direct Python callers. The persisted record and every
    # transport response omit the course path.
    return dict(record, base=base)


def accept(state, settings, base=None, reviewer="", expected_draft_fingerprint=None):
    """Turn a proposal into exactly one journalled change, or refuse.

    - On an already-settled state (or any non-proposal) it returns the
      same state unchanged and records nothing, so a double submit
      cannot write twice: the guard is here, not in the page.
    - Under report_only autonomy it refuses visibly: a settled state
      whose reason names the setting and where to change it.
    - On a fingerprint that no longer matches it reports the conflict in
      words a learner can act on; journal.commit_operation already
      refused the overwrite, this only says so.

    Exactly one journal operation per accepted proposal: prepared and
    applied entries for one change, never two changes.
    """
    by_identity = isinstance(state, str)
    if by_identity:
        if base is None:
            raise ValueError("base is required when accepting by proposal id")
        state = status(base, state)
    else:
        base = base or (state or {}).get("base")
    if not isinstance(state, dict) or state.get("disposition") in \
            ("accepted", "rejected", "conflicted", "undone"):
        return state
    if state.get("state") != "proposed":
        return state
    if expected_draft_fingerprint is not None and expected_draft_fingerprint != draft_fingerprint(state["draft"]):
        raise ValueError("agent.draft_stale")

    skill = state.get("skill") or ""
    iid = state.get("interaction_id")
    autonomy = (settings or {}).get("auditor_autonomy")
    if autonomy not in AUTONOMY_MAY_WRITE:
        shown = autonomy if autonomy else "unset, which reads as"
        refused = _settled(
            iid, skill, "agent.report_only",
            "auditor_autonomy is %s 'report_only', so drafts are shown "
            "but never written. To let an accepted draft become a "
            "revision, set auditor_autonomy to 'draft_and_approve' in "
            "itembank.json." % shown,
            refusal="report_only")
        if by_identity and state.get("proposal_id") and base:
            state.update({"code": refused["code"], "reason": refused["reason"],
                          "refusal": "report_only", "updated_at": _now(),
                          "next_action": "Change Agent autonomy or reject this proposal"})
            return _write_record(base, state)
        return refused

    if not base:
        raise ValueError("base is required")
    try:
        sources_now = _source_fingerprints(base, state.get("source_paths") or [])
    except (OSError, ValueError):
        sources_now = None
    if sources_now != (state.get("source_fingerprints") or {}):
        reason = ("A configured source changed or became unavailable since "
                  "this draft was shown. Review it and start a new proposal. "
                  "Nothing was written.")
        if state.get("proposal_id"):
            state.update({"state": "settled", "disposition": "conflicted",
                          "code": "agent.source_stale", "reason": reason,
                          "conflict": True, "updated_at": _now(),
                          "reviewer": reviewer, "decided_at": _now(),
                          "next_action": "Start a new proposal"})
            return _write_record(base, state)
        return _settled(iid, skill, "agent.source_stale", reason,
                        conflict=True)
    rel = state["target"]
    kind = state["kind"]

    existing = None
    for row in (journal.read_registry(base) or {}).values():
        if isinstance(row, dict) and row.get("path") == rel:
            existing = row
            break
    object_id = existing["object_id"] if existing \
        else identity.new_object_id()
    operation = "edit_in_place" if existing else "mint"

    try:
        if skill == "staged-cases":
            import model
            findings, _ = model.lint(model.parse_bank(state["draft"]))
            if findings:
                raise ValueError("agent.staged_draft_invalid: " + findings[0].message)
        if skill == "course-outline":
            import course
            import graph
            _validate_course_proposal(base, state)
            record = course.write_course(
                base, graph.parse_course(state["draft"]), state["expected_fingerprint"],
                "human", reviewer,
                precommit=lambda: _validate_course_proposal(base, state))
        else:
            record = journal.commit_operation(
                base, object_id, kind, rel, operation,
                state["draft"].encode("utf-8"),
                expected_fingerprint=state.get("expected_fingerprint"),
                actor_kind="agent", actor_name="agent-area:%s" % skill,
                create_if_missing=True)
    except journal.JournalError as exc:
        conflict = exc.code in ("journal.conflict", "journal.stale_preflight")
        if conflict:
            reason = ("%s changed since this draft was shown, so nothing "
                      "was written. Open the file, keep what you need, "
                      "then start the skill again. (%s)"
                      % (rel, exc.message))
        else:
            reason = ("Nothing was written: %s Next safe action: try the "
                      "skill again; if it keeps failing, check the course "
                      "directory is reachable." % exc.message)
        if state.get("proposal_id"):
            state.update({"state": "settled", "disposition": "conflicted",
                          "code": exc.code, "reason": reason,
                          "conflict": True, "updated_at": _now(),
                          "reviewer": reviewer, "decided_at": _now(),
                          "next_action": "Start a new proposal"})
            return _write_record(base, state)
        return _settled(iid, skill, exc.code, reason, conflict=conflict)

    entry_id = None
    for entry in journal.entries(base):
        if entry.get("object_id") == object_id \
                and entry.get("state") == "applied" \
                and entry.get("revision") == record["revision"]:
            entry_id = entry.get("entry_id")

    settled = {
        "schema_version": RECORD_VERSION,
        "state": "settled",
        "disposition": "accepted",
        "proposal_id": state.get("proposal_id"),
        "operation_id": state.get("operation_id"),
        "ok": True,
        "skill": skill,
        "interaction_id": iid,
        "target": rel,
        "operation": operation,
        "entry_id": entry_id,
        "revision": record["revision"],
        "prior_revision": record.get("parent_revision"),
        "undoable": True,
        "conflict": False,
        "reason": "Draft accepted into %s as revision %s. Undo restores "
                  "the previous content from the journal."
                  % (rel, record["revision"]),
        "reviewer": reviewer,
        "decided_at": _now(),
        "updated_at": _now(),
        "expected_fingerprint": state.get("expected_fingerprint"),
        "validation": state.get("validation"),
        "citations": state.get("citations"),
        "source_paths": state.get("source_paths"),
        "source_fingerprints": state.get("source_fingerprints"),
        "provider": state.get("provider"),
        "draft": state.get("draft"),
        "kind": kind,
        "diff": state.get("diff"),
        "next_action": "Undo accepted change",
    }
    return _write_record(base, settled) if settled.get("proposal_id") else settled


def reject(base, proposal_id, reviewer="", reason=""):
    record = status(base, proposal_id)
    if record.get("disposition") != "proposed":
        return record
    record.update({"state": "settled", "disposition": "rejected",
                   "reviewer": reviewer, "review_reason": reason,
                   "decided_at": _now(), "updated_at": _now(),
                   "reason": "Proposal rejected. No accepted course content changed.",
                   "next_action": "Start a new proposal"})
    return _write_record(base, record)


def undo(base, proposal_id, reviewer=""):
    record = status(base, proposal_id)
    if record.get("disposition") == "undone":
        return record
    if record.get("disposition") != "accepted" or not record.get("entry_id"):
        return record
    target = os.path.join(os.path.abspath(base), record["target"])
    accepted = next((entry for entry in journal.entries(base)
                     if entry.get("entry_id") == record["entry_id"]), None)
    before = b""
    if accepted and accepted.get("before_image"):
        with open(os.path.join(journal.journal_dir(base),
                               accepted["before_image"]), "rb") as fh:
            before = fh.read()
    prior_absent = (accepted is not None and
                    accepted.get("operation") == "mint" and
                    accepted.get("before_fingerprint") is None and
                    not accepted.get("before_image"))
    revision = journal.undo(base, record["entry_id"], "human", reviewer)
    if prior_absent:
        restored_byte_identical = not os.path.lexists(target)
    else:
        with open(target, "rb") as fh:
            restored_byte_identical = fh.read() == before
    undo_entry = next((entry for entry in reversed(list(journal.entries(base)))
                       if entry.get("state") == "applied"
                       and entry.get("revision") == revision.get("revision")
                       and entry.get("object_id") == accepted.get("object_id")), None)
    record.update({"disposition": "undone", "state": "settled",
                   "undo_entry_id": (undo_entry or {}).get("entry_id"),
                   "restored_revision": revision.get("revision"),
                   "restored_byte_identical": restored_byte_identical,
                   "undone_at": _now(), "updated_at": _now(),
                   "undo_reviewer": reviewer,
                   "reason": "Accepted change undone. The previous accepted state was restored and the reversal was recorded.",
                   "next_action": "Start a new proposal"})
    return _write_record(base, record)
