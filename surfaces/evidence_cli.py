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

import evidence
import model
import retention


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
    bank = a.bank or None

    if not (objective or subject or session_id or bank):
        sys.exit("evidence: give at least one of --objective, --subject, "
                  "--session or --bank to query")

    # objective_history() is the ONE call site that runs ensure_index() --
    # deliberately not duplicated here, so a query that skipped it (a
    # regression this surface cannot see directly) is not papered over by
    # a second, independent index refresh happening beside it. The "used"
    # vs "fallback" status reported below is inferred AFTER the query, by
    # asking whether the index it should have refreshed is in fact fresh.
    rows = evidence.objective_history(
        log, objective, prefix=a.prefix, subject=subject, mode=mode,
        session_id=session_id, since=since, bank=bank)
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
                                   session_id, since, bank)
        and ev.get("event_id") in retracted_ids)

    result = {"schema_version": evidence.REPORT_VERSION,
              "objective": objective or "", "bank": a.bank or "",
              "count": len(rows),
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


def _resolve_marks_event(log, session_id, item_ref):
    """The most recent LIVE response event for `session_id` and `item_ref`
    -- what a mark's `marks_event` field must name. Returns the response
    event dict, or `None` when nothing was ever answered for that item in
    this session, which `cmd_mark` treats as a named error rather than a
    mark with a dangling target.
    """
    candidate = None
    for ev in evidence.live_events(log):
        if ev.get("event_type") != evidence.RESPONSE_EVENT_TYPE:
            continue
        if ev.get("session_id") != session_id:
            continue
        if ev.get("item_ref") != item_ref:
            continue
        candidate = ev
    return candidate


def _resolve_proposal(log, session_id, proposal_id):
    """The LIVE mark_proposal event with this event_id for `session_id`, or
    None -- what a proposal-accept mark must reference (plan 08-04, D-14)."""
    for ev in evidence.proposals_for(log, session_id):
        if ev.get("event_id") == proposal_id:
            return ev
    return None


def _normalize_verdict(raw):
    if isinstance(raw, bool):
        return raw
    if isinstance(raw, str):
        low = raw.strip().lower()
        if low in ("pass", "true"):
            return True
        if low in ("fail", "false"):
            return False
    sys.exit("mark: verdict must be pass/fail (or true/false), got %r" % (raw,))


def _normalize_rubric(raw):
    if not raw:
        return []
    out = []
    for r in raw:
        if not isinstance(r, dict) or "point" not in r or "pass" not in r:
            sys.exit("mark: each rubric entry needs 'point' and 'pass', got %r" % (r,))
        out.append({"point": r["point"], "pass": bool(r["pass"])})
    return out


def _load_marks_batch(a):
    """Exactly one of `--file`, `--marks`, `--item` or `--proposal` selects
    the batch (D-12 requires the command to accept a batch; `--item` is the
    single-mark convenience form for one answer and `--proposal` the
    single-proposal accept form). Returns a list of raw mark dicts, in input
    order, none of which have been resolved or validated against the log
    yet. A single-form entry may carry `--rubric` JSON of N {point, pass}
    booleans supplied by the human marker (D-24).
    """
    given = [x for x in (a.file, a.marks, a.item, a.proposal) if x]
    if len(given) != 1:
        sys.exit("mark: give exactly one of --file, --marks, --item or "
                 "--proposal")
    if a.file:
        text = sys.stdin.read() if a.file == "-" else open(a.file, encoding="utf-8").read()
        entries = []
        for lineno, line in enumerate(text.splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except ValueError as exc:
                sys.exit("mark: %s:%d is not valid JSON (%s)" % (a.file, lineno, exc))
        return entries
    if a.marks:
        try:
            entries = json.loads(a.marks)
        except ValueError as exc:
            sys.exit("mark: --marks is not valid JSON (%s)" % exc)
        if not isinstance(entries, list):
            sys.exit("mark: --marks must be a JSON array")
        return entries
    if not a.verdict:
        sys.exit("mark: --item/--proposal requires --verdict")
    entry = {"verdict": a.verdict}
    if a.item:
        entry["item_ref"] = a.item
    if a.proposal:
        entry["proposal"] = a.proposal
    if a.notes is not None:
        entry["notes"] = a.notes
    if a.rubric:
        try:
            rubric = json.loads(a.rubric)
        except ValueError as exc:
            sys.exit("mark: --rubric is not valid JSON (%s)" % exc)
        if not isinstance(rubric, list):
            sys.exit("mark: --rubric must be a JSON array of {point, pass}")
        entry["rubric"] = rubric
    return [entry]


def cmd_mark(a):
    """Record a batch of marks as timestamped events (D-12) -- twenty short
    answers marked in one invocation, not twenty separate ones. Entries may
    identify their target by `item_ref` (resolved to the most recent live
    response) or by `proposal` (resolved to the proposal's response event,
    plan 08-04 D-14); a single proposal may be accepted with `--proposal`.

    Every entry is resolved before anything is appended: a batch that names
    one item never answered in this session, or one proposal that does not
    exist, exits non-zero naming the reference, with nothing appended for
    any entry in that batch, rather than partially recording the marks that
    happened to resolve first.
    """
    log = evidence.log_path(a.base)
    entries = _load_marks_batch(a)
    if not entries:
        sys.exit("mark: no marks given")

    resolved = []
    for entry in entries:
        proposal_id = entry.get("proposal")
        if proposal_id:
            proposal = _resolve_proposal(log, a.session, proposal_id)
            if proposal is None:
                sys.exit("mark: no mark_proposal event %r in session %s" %
                         (proposal_id, a.session))
            target = evidence.event_by_id(log,
                                          proposal.get("response_event_id"))
            if target is None:
                sys.exit("mark: proposal %r names a missing response event %r" %
                         (proposal_id, proposal.get("response_event_id")))
            item_ref = proposal.get("item_ref")
            if not item_ref:
                sys.exit("mark: proposal %r has no item_ref" % proposal_id)
            verdict = _normalize_verdict(entry.get("verdict"))
            rubric = _normalize_rubric(entry.get("rubric"))
            notes = entry.get("notes") or ""
            resolved.append((item_ref, target, verdict, rubric, notes,
                             proposal_id))
            continue
        item_ref = entry.get("item_ref")
        if not item_ref:
            sys.exit("mark: an entry is missing item_ref: %r" % (entry,))
        target = _resolve_marks_event(log, a.session, item_ref)
        if target is None:
            sys.exit("mark: no response recorded for item_ref %r in session %s; "
                      "marking something that was never answered is not allowed" %
                      (item_ref, a.session))
        verdict = _normalize_verdict(entry.get("verdict"))
        rubric = _normalize_rubric(entry.get("rubric"))
        notes = entry.get("notes") or ""
        resolved.append((item_ref, target, verdict, rubric, notes, None))

    results = []
    recorded = already_recorded = 0
    for item_ref, target, verdict, rubric, notes, proposal_id in resolved:
        event = evidence.mark_event(
            a.session, target.get("item_id", ""), item_ref, target["event_id"],
            verdict, rubric=rubric, notes=notes, proposal_ref=proposal_id)
        write_result = evidence.append_event(log, event)
        results.append({"item_ref": item_ref, "marks_event": target["event_id"],
                        "status": write_result["status"],
                        "event_id": write_result["event_id"],
                        "proposal_ref": proposal_id})
        if write_result["status"] == "recorded":
            recorded += 1
        else:
            already_recorded += 1

    payload = {"schema_version": evidence.EVENT_SCHEMA_VERSION, "session_id": a.session,
              "marks": results, "recorded": recorded, "already_recorded": already_recorded}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print("%d recorded, %d already recorded" % (recorded, already_recorded))
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


def cmd_trends(a):
    """`itembank trends` -- the longitudinal retention report, JSON or
    plain text, both renderings of the SAME `retention.retention_report`
    payload (D-15): no arithmetic in the renderer, no second derivation.

    Reads the append-only log once via `evidence.capture_events` and hands
    the captured sequence to the pure derivation layer; the report's claim
    names cutoff, zone, window, filters, event count and settings version.
    The default `--weeks 4` selects the report window; `--subject` and
    `--objective` narrow the filters recorded in the claim. With no
    evidence the report renders honestly (unknown states, null rates),
    never a fabricated trend (D-03).
    """
    base = a.base or "."
    log = evidence.log_path(base)
    events = evidence.capture_events(log) if os.path.exists(log) else ()
    cfg = {}
    try:
        from surfaces import settings as _settings
        cfg = _settings.load_settings(base)
    except Exception:
        cfg = {}
    filters = {}
    if getattr(a, "subject", None):
        filters["subject"] = a.subject
    if getattr(a, "objective", None):
        filters["objective"] = a.objective
    payload = retention.retention_report(
        events, cutoff=a.cutoff or None, zone=a.zone or "UTC",
        weeks=a.weeks, filters=filters, cfg=cfg)
    if a.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(retention.report_text(payload))
    return 0
