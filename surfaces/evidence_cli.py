"""The evidence query surface: reading a learner's recorded history back out.

`itembank evidence` is the reader over `_evidence/evidence.jsonl`. It answers
"how am I doing on this objective" across every session and every subject, from
the log alone, the same way `surfaces/session.py` is the first writer into it.
An objective (or subject, or session) with no recorded events is an empty
history, not an error — the command still exits 0.

`--objective` matches exactly unless `--prefix` is also given, in which case it
also matches an objective beginning with the argument followed by a `.` or `:`
separator (D-06) — `emt:airway` never matches `emt:airwaymanagement`.
`--subject` filters on subject alone, ignoring `--objective` entirely. At least
one of `--objective`, `--subject` or `--session` is required. `--rebuild-index`
deletes and rebuilds the disposable sqlite3 projection (01-08, D-08) before
querying — it is a cache, so this loses nothing but time.

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
    """The one command that answers "how am I doing on objective X over
    time" across every session and every subject, reading from the log
    alone (D-08's disposable sqlite3 projection is a cache in front of
    that read, never a second source of truth). Presents counts and the
    trail itself and nothing else -- no score, level, badge or streak, per
    PROJECT.md's Out of Scope table.
    """
    log = evidence.log_path(a.base)
    index = evidence.index_for_log(log)

    if a.rebuild_index:
        # The index is a cache: deleting it and rebuilding costs time and
        # loses nothing (D-08). Say so plainly rather than silently.
        if os.path.exists(index):
            os.remove(index)
        evidence.rebuild_index(log, index)

    objective = a.objective or None
    subject = a.subject or None
    session_id = a.session or None
    mode = a.mode or None
    since = a.since or None

    if not (objective or subject or session_id):
        sys.exit("evidence: give at least one of --objective, --subject or "
                  "--session to query")

    # objective_history() is the ONE call site that runs ensure_index() --
    # deliberately not duplicated here, so a query that skipped it (a
    # regression this surface cannot see directly) is not papered over by
    # a second, independent index refresh happening beside it. The "used"
    # vs "fallback" status reported below is inferred AFTER the query, by
    # asking whether the index it should have refreshed is in fact fresh.
    rows = evidence.objective_history(
        log, objective, prefix=a.prefix, subject=subject, mode=mode,
        session_id=session_id, since=since)
    by_mode = evidence.objective_rollup(rows)
    try:
        post_stale, _ = evidence.index_stale(log, index)
        status = "fallback" if post_stale else "used"
    except Exception:
        status = "fallback"

    retracted_ids = evidence.retracted_ids(log)
    retracted_count = sum(
        1 for ev in evidence.events(log)
        if ev.get("event_type") == evidence.RESPONSE_EVENT_TYPE
        and evidence.event_matches(ev, objective, a.prefix, subject, mode,
                                   session_id, since)
        and ev.get("event_id") in retracted_ids)

    result = {"schema_version": evidence.EVENT_SCHEMA_VERSION,
              "objective": objective or "", "count": len(rows),
              "retracted": retracted_count, "by_mode": by_mode,
              "index": status, "index_rebuilt": bool(a.rebuild_index),
              "events": rows}
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


def cmd_render(a):
    """Regenerate the attempt markdown or the session JSON for one session
    from the evidence log alone (D-11) -- a view, never an input. Editing
    the output changes nothing, because the next render replaces it from
    the log alone. `daily` is reserved for plan 01-10; naming it here now
    exits with a stated "not yet implemented" error rather than silently
    producing nothing, so the gap is visible instead of guessed at.
    """
    if a.kind not in ("attempt", "session", "daily"):
        sys.exit("render: unknown kind %r" % (a.kind,))
    if a.kind == "daily":
        sys.exit("render: 'daily' is not yet implemented in this build "
                 "(arrives in plan 01-10)")
    if not a.bank:
        sys.exit("render: --bank is required for 'attempt' and 'session'")

    log = evidence.log_path(a.base)
    qs = model.load(a.bank)

    if a.kind == "attempt":
        text = evidence.render_attempt_md(log, a.session, qs, a.bank)
        count = len(evidence.session_events(log, a.session))
    else:
        data = evidence.render_session_json(log, a.session, qs, a.bank)
        text = json.dumps(data, ensure_ascii=False, indent=2)
        count = len(data["responses"])

    if a.out:
        # The runtime.write_session() pattern (T-1-22): tmp file, then
        # os.replace() -- so a half-written render can never replace a
        # good one, the one atomic-write precedent every render in this
        # phase copies rather than reinventing.
        out_dir = os.path.dirname(os.path.abspath(a.out))
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        tmp = a.out + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write(text)
            fh.write("\n")
        os.replace(tmp, a.out)
        print("%d response(s) rendered for session %s -> %s" %
              (count, a.session, a.out))
    else:
        print(text)
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
