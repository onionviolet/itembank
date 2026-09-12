"""Explicit scoreless reading declarations over journal and evidence authority.

Lock order is journal then evidence. Confirmation checkpoints contain resolved
facts, never source bytes or learner notes. No completion flag is stored here.
"""
import os

import course
import director
import discovery
import evidence
import graph
import journal


def _current(base, body):
    read = course.accepted_reading_graph(base, body["expected_fingerprint"])
    rows = [r for r in graph.validate_reading_graph(read["doc"])["occurrences"]
            if r["occurrence_id"] == body["occurrence_id"]]
    parents = {r["supersedes_revision_id"] for r in rows}
    heads = [r for r in rows if r["revision_id"] not in parents]
    if len(heads) != 1 or heads[0]["revision_id"] != body["revision_id"]:
        raise course.CourseError("course.reading_revision_stale", "Select the current reading revision.")
    course.validate_reading_source(base, heads[0]["source_ref"])
    return read, heads[0]


def _log(base):
    log = evidence.log_path(base)
    if not discovery.inside_any_root(log, [base]):
        raise course.CourseError("course.reading_outside_root", "Evidence leaves the approved root.")
    return log


def confirm(base, body, actor_kind="human", actor_name=""):
    """Persist a fresh explicit confirmation against the current correction epoch."""
    if actor_kind != "human" or body.get("confirmation") != "read":
        raise course.CourseError("course.reading_confirmation_required", "A learner must explicitly confirm read.")
    with journal._journal_lock(base):
        read, occurrence = _current(base, body)
        log = _log(base)
        if not os.path.exists(log) and any(
                ((e.get("agent") or {}).get("checkpoint") or {}).get("reading_confirmation_version")
                for e in journal.entries(base)):
            raise course.CourseError("course.reading_history_unavailable", "Restore the missing reading history before confirming again.")
        os.makedirs(os.path.dirname(log), exist_ok=True)
        fd = os.open(log, os.O_RDWR | os.O_CREAT, 0o644)
        try:
            with evidence.locked(fd):
                evidence._repair_evidence_tail(fd, log)
                rows = evidence._reading_history(log)
                key = evidence.reading_dedupe_key(read["object_id"], occurrence["occurrence_id"], occurrence["revision_id"])
                intent = director.new_operation_id()
                event = evidence.reading_declared_event(read["object_id"], occurrence, intent,
                                                        evidence.reading_retraction_epoch(rows, key))
                checkpoint = {"reading_confirmation_version": 1, "event": event,
                              "expected_fingerprint": read["fingerprint"]}
                director.begin_operation(base, base, "Explicit reading confirmation", "human", actor_name,
                                         "learner", "draft-and-review", scopes=["local reading declaration"],
                                         operation_id=intent, checkpoint=checkpoint, lock_held=True)
                # Empty history is now durably known, distinct from lost history.
                os.fsync(fd)
                evidence._sync_evidence_directory(log)
                evidence._sync_evidence_directory(os.path.dirname(log))
        finally:
            os.close(fd)
    return {"intent_id": intent, "base_retraction_id": event["base_retraction_id"],
            "occurrence_id": occurrence["occurrence_id"], "revision_id": occurrence["revision_id"],
            "expected_fingerprint": read["fingerprint"], "status": "confirmed"}


def _confirmation(base, body):
    entries = director.operation_entries(base, body["intent_id"])
    entries = [e for e in entries if e.get("operation") == director.AGENT_RECORD_TYPE
               and e.get("state") == "applied" and (e.get("origin") or {}).get("actor_kind") == "human"
               and (e.get("agent") or {}).get("phase") == "declare-intent"]
    if len(entries) != 1:
        raise course.CourseError("course.reading_confirmation_missing", "Make a fresh explicit confirmation.")
    checkpoint = entries[0]["agent"].get("checkpoint") or {}
    event = checkpoint.get("event") or {}
    if (checkpoint.get("reading_confirmation_version") != 1 or
            event.get("intent_id") != body["intent_id"] or
            event.get("occurrence_id") != body["occurrence_id"] or
            event.get("occurrence_revision_id") != body["revision_id"] or
            checkpoint.get("expected_fingerprint") != body["expected_fingerprint"]):
        raise course.CourseError("course.reading_confirmation_conflict", "Use the original confirmation context.")
    evidence._validate_reading_event(event)
    return event


def declare(base, body, actor_kind="human", actor_name=""):
    """Replay without source access. Validate all live authority on first write."""
    if actor_kind != "human":
        raise course.CourseError("course.reading_confirmation_required", "Only the learner declares read.")
    with journal._journal_lock(base):
        event = _confirmation(base, body)
        log = _log(base)
        if not os.path.exists(log):
            raise course.CourseError("course.reading_history_unavailable", "Restore the missing evidence log before retrying.")

        def validate():
            read, occurrence = _current(base, body)
            if (event["course_id"] != read["object_id"] or
                    any(evidence.reading_canonical(event[k]) != evidence.reading_canonical(occurrence[k])
                        for k in ("objective_ids", "binding_ref", "source_ref"))):
                raise course.CourseError("course.reading_confirmation_conflict", "The accepted reading differs from the confirmation.")

        result = evidence.append_event(log, event, precommit=validate)
        result["availability"] = availability(base, event["source_ref"])
        return result


def availability(base, source_ref):
    """Report registry and filesystem availability without opening source bytes."""
    source_id = source_ref["source_object_id"]
    try:
        rights = course.rights_for_binding(base, source_id, "read")
    except course.CourseError:
        return {"state": "rights-unknown", "source_bytes_rechecked": False}
    except (OSError, ValueError):
        return {"state": "error", "source_bytes_rechecked": False}
    state = "available"
    row = journal._compute_registry(base).get(source_id) or {}
    if rights != "granted":
        state = "rights-denied" if rights == "denied" else "rights-unknown"
    elif row.get("fingerprint") != source_ref["source_fingerprint"]:
        state = "revision-conflict"
    else:
        path = os.path.join(base, row.get("path") or "")
        if not discovery.inside_any_root(path, [base]) or not os.path.isfile(path):
            state = "source-unavailable"
        elif source_ref["range"]["locator_id"] is not None:
            import source_adapters
            if not os.path.isfile(source_adapters.sidecar_path_for(path)):
                state = "locator-missing"
    return {"state": state, "source_bytes_rechecked": False}


def operation(base, operation, body, actor_kind, actor_name):
    try:
        return (confirm if operation == "confirm_reading" else declare)(base, body, actor_kind, actor_name)
    except (ValueError, OSError) as err:
        raise course.CourseError("course.reading_evidence_refused", str(err)) from err
