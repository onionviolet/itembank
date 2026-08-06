"""The evidence query surface: reading a learner's recorded history back out.

`itembank evidence --objective X` is the first reader over `_evidence/evidence.jsonl`.
It answers "how am I doing on this objective" from the log alone, the same way
`surfaces/session.py` is the first writer into it. An objective with no recorded
events is an empty history, not an error — the command still exits 0.

`itembank retract` is the undo command (D-10): it appends a reasoned
compensating event and never deletes anything. `itembank evidence`'s `count`
is always post-retraction; its new `retracted` field says how much of the
raw log for this query was undone, so a shrinking count is never mistaken
for missing data.

`itembank id-assign` is the identity writer: the only command that rewrites a
bank file. `lint` stays read-only by design (D-03) — every identity change a
learner's bank ever gets lands in `git diff` through this command alone.
"""
import json
import os
import sys

import model
import evidence


def cmd_evidence(a):
    log = evidence.log_path(a.base)
    rows = evidence.objective_history(log, a.objective)
    retracted = evidence.retracted_ids(log)
    retracted_count = sum(
        1 for ev in evidence.events(log)
        if ev.get("event_type") == evidence.RESPONSE_EVENT_TYPE
        and ev.get("objective") == a.objective
        and ev.get("event_id") in retracted)
    result = {"schema_version": evidence.EVENT_SCHEMA_VERSION,
              "objective": a.objective, "count": len(rows),
              "retracted": retracted_count, "events": rows}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_retract(a):
    """Undo a recorded event by appending a reasoned retraction (D-10).
    Nothing is ever deleted: retracting suppresses `a.event_id` in every
    view from here on, but its original line stays on disk and readable.
    """
    log = evidence.log_path(a.base)
    target = evidence.event_by_id(log, a.event_id)
    if target is None:
        sys.exit("no event %s in %s" % (a.event_id, log))

    already = evidence.retracted_ids(log)
    if a.event_id in already:
        existing = next(
            (ev for ev in evidence.events(log)
             if ev.get("event_type") == evidence.RETRACTION_EVENT_TYPE
             and ev.get("retracts") == a.event_id),
            None)
        result = {"status": "already_retracted", "event_id": a.event_id,
                  "retracted_by": existing.get("event_id") if existing else None}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    try:
        event = evidence.retraction_event(a.event_id, a.reason)
    except ValueError as exc:
        sys.exit(str(exc))
    write_result = evidence.append_event(log, event)
    result = {"status": "retracted", "event_id": write_result["event_id"],
              "retracts": a.event_id, "reason": a.reason}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_id_assign(a):
    paths = a.banks
    texts = {}
    taken = set()
    owner = {}
    for path in paths:
        text = open(path, encoding="utf-8", newline="").read()
        texts[path] = text
        for q in model.parse_bank(text):
            item_id = q.get("item_id", "")
            if not item_id:
                continue
            if item_id in owner and owner[item_id] != path:
                sys.exit("id-assign: item id %s appears in both %s and %s; "
                          "D-05 requires ids to be globally unique across banks" %
                          (item_id, os.path.basename(owner[item_id]),
                           os.path.basename(path)))
            owner[item_id] = path
            taken.add(item_id)

    banks_out = []
    total_assigned = total_recorded = total_updated = 0
    for path in paths:
        new_text, changes = model.assign_ids(texts[path], taken)
        assigned = sum(1 for c in changes if c["action"] == "assigned")
        recorded = sum(1 for c in changes if c["hash_action"] == "recorded")
        updated = sum(1 for c in changes if c["hash_action"] == "updated")
        total_assigned += assigned
        total_recorded += recorded
        total_updated += updated
        banks_out.append({"bank": os.path.basename(path), "assigned": assigned,
                          "hashes_recorded": recorded, "hashes_updated": updated,
                          "changes": changes})
        if not a.dry_run and new_text != texts[path]:
            tmp = path + ".tmp"
            with open(tmp, "w", encoding="utf-8", newline="") as fh:
                fh.write(new_text)
            os.replace(tmp, path)

    payload = {"schema_version": 1, "banks": banks_out, "dry_run": bool(a.dry_run)}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print("%d ids assigned, %d hashes recorded, %d hashes updated" %
          (total_assigned, total_recorded, total_updated))
    return 0
