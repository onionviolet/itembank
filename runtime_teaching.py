"""Internal runtime component; public access goes through runtime."""
import re


HINT_TIERS = (
    {"name": "lesson", "label": "lesson pointer"},
    {"name": "objective", "label": "objective"},
    {"name": "trap", "label": "trap"},
    {"name": "rationale", "label": "picked-option rationale"},
    {"name": "discriminator", "label": "discriminator"},
    {"name": "reveal", "label": "authored reveal"},
)


def new_teaching_record():
    """One item's persisted teaching state (D-03)."""
    import runtime
    return {"attempt_count": 0, "highest_tier_unlocked": -1,
            "highest_tier_shown": -1, "last_genuine_canonical": None,
            "last_response_event_id": None,
            "shown_tiers": []}


def teaching_key(q):
    """The stable key teaching_state is indexed by: the opaque item id when
    one has been assigned, else the positional reference -- identical to
    `evidence.evidence_key()` (which cannot be imported here without a cycle).
    """
    import runtime
    return q.get("item_id") or ("ref:" + q["id"])


def _reveal_display(q):
    """The reveal tier's learner-facing text: the runtime's own compact
    answer shaper plus the item's WHY text when one is authored. Tier 5's
    `content` is the structured `explain_payload` dict, which a surface
    rendering strings could only print as nothing -- so the runtime shapes
    the words here, where disclosure has already been authorized, rather
    than leaving a surface to invent them.
    """
    import runtime
    parts = [runtime.answer_text(q) or ""]
    why = (q.get("why") or "").strip()
    if why:
        parts.append(why)
    return " — ".join(p for p in parts if p)


def _objective_hint_display(objective):
    """Turn an internal objective id into learner-facing hint text.

    Objective ids are durable machine references, not teaching copy.  Keep the
    identifier private to the item and expose only its descriptive tail.  This
    is deliberately a small, deterministic presentation rule rather than a
    guessed objective description: authors still own the wording when they
    want more than the id can honestly say.
    """
    import runtime
    tail = str(objective or "").split(":", 1)[-1]
    words = [part for part in re.split(r"[._-]+", tail)
             if part and not part.isdigit()]
    if not words:
        # Numbered objectives such as ``math:1.2`` still carry a useful
        # learner-facing reference.  Keep that authored identifier rather
        # than claiming the tier is unavailable merely because it has no
        # alphabetic words.
        return ("Focus: %s." % tail) if tail else ""
    phrase = " ".join(words)
    return "Focus: %s." % (phrase[:1].upper() + phrase[1:])


def authored_hint(q, tier, canonical):
    """The sole private-tier resolver for the six fixed authored tiers
    (D-07/D-08/D-09). Missing content returns `available: false` at the same
    index. Tier 3 is response-specific: it resolves the distractor analysis
    for the learner's latest genuine picked option.

    Every payload carries `display`: the learner-facing text for that tier,
    empty when the tier is unavailable. `content` is unchanged on every tier,
    so no existing consumer changes behaviour. The split exists because the
    runtime already owns what a tier discloses; a surface that re-derived
    display text from an id would be a second place deciding what the learner
    reads. `display` carries text only -- never a tier index, name or label.
    """
    import runtime
    t = runtime.HINT_TIERS[tier]
    name = t["name"]
    if tier == 0:
        # The slug is a DERIVED identifier for anchors and lookups. It was
        # never learner-facing text, and printing it is the whole of this
        # defect: an offline hint read "Authored hint / the-airway-step-by-
        # step". Availability keys on the author-written reference because
        # that names the real source; the two are equivalent in practice.
        ref = q.get("lesson_ref") or ""
        slug = q.get("lesson_slug") or ""
        return {"index": 0, "name": name, "available": bool(ref),
                "content": slug,
                "display": ('Review “%s”. Use the Read the lesson link '
                            'above to open it.' % ref) if ref else "",
                "slug": slug, "label": t["label"]}
    if tier == 1:
        obj = q.get("objective") or ""
        return {"index": 1, "name": name, "available": bool(obj),
                "content": obj, "display": runtime._objective_hint_display(obj),
                "label": t["label"]}
    if tier == 2:
        trap = q.get("trap") or ""
        return {"index": 2, "name": name, "available": bool(trap),
                "content": trap,
                "display": ("Common wrong turn: %s" % trap) if trap else "",
                "label": t["label"]}
    if tier == 3:
        content = ""
        if canonical and q["type"] in ("mc", "multi"):
            option = str(canonical).split(",")[0].strip()
            content = (q.get("da") or {}).get(option, "")
        return {"index": 3, "name": name, "available": bool(content),
                "content": content,
                "display": ("Why your last choice is tempting: %s" % content)
                           if content else "",
                "label": t["label"],
                "for_response": canonical}
    if tier == 4:
        disc = q.get("disc") or ""
        return {"index": 4, "name": name, "available": bool(disc),
                "content": disc,
                "display": ("Deciding test: %s" % disc) if disc else "",
                "label": t["label"]}
    # tier == 5: the authored reveal -- the full post-response explanation.
    return {"index": 5, "name": name, "available": True,
            "content": runtime.explain_payload(q, reveal=True),
            "display": runtime._reveal_display(q), "label": t["label"]}


def _record_from_evidence(q, events):
    """Pure fold of an item's live response/hint events into a teaching
    record -- the crash-window reconciliation input (D-15/D-16). `events` is
    the item's already-live (post-retraction) event list.
    """
    import runtime
    rec = runtime.new_teaching_record()
    key = None
    for ev in events:
        et = ev.get("event_type")
        if et == "response":
            rec["attempt_count"] += 1
            rec["last_genuine_canonical"] = ev.get("canonical")
            rec["last_response_event_id"] = ev.get("event_id")
            ht = ev.get("hint_tier")
            if isinstance(ht, int):
                rec["highest_tier_shown"] = max(rec["highest_tier_shown"], ht)
                rec["highest_tier_unlocked"] = max(rec["highest_tier_unlocked"], ht)
        elif et == "hint":
            idx = ev.get("tier_index")
            if isinstance(idx, int):
                rec["highest_tier_shown"] = max(rec["highest_tier_shown"], idx)
                rec["highest_tier_unlocked"] = max(rec["highest_tier_unlocked"], idx)
                rec["shown_tiers"].append({"index": idx,
                                           "name": ev.get("tier_name"),
                                           "unlock_path": ev.get("unlock_path")})
    return rec


def _next_reveal(q, rec, unlock_path):
    """Compute the next tier to reveal from a teaching record.

    Returns (hint_payload, new_record). When every tier is already shown,
    returns a payload with `tier: None` and `exhausted: True` -- disclosure
    never repeats, and no new hint event is authorized.
    """
    import runtime
    next_index = rec["highest_tier_shown"] + 1
    if next_index >= len(runtime.HINT_TIERS):
        shown = list(rec["shown_tiers"])
        return {"tier": None, "shown": shown, "exhausted": True}, rec
    tier = runtime.authored_hint(q, next_index, rec["last_genuine_canonical"])
    rec = dict(rec)
    rec["highest_tier_shown"] = next_index
    rec["highest_tier_unlocked"] = max(rec["highest_tier_unlocked"], next_index)
    rec["shown_tiers"] = list(rec["shown_tiers"]) + [
        {"index": next_index, "name": tier["name"], "unlock_path": unlock_path}]
    payload = {"tier": tier, "unlock_path": unlock_path,
               "shown": [s["index"] for s in rec["shown_tiers"]],
               "for_response": rec["last_genuine_canonical"]}
    return payload, rec


def reconcile_teaching_state(session, q, evidence_state=None):
    """Fold live evidence into the session's teaching state for one item.

    `evidence_state` is a dict keyed by item key whose values are that item's
    live (post-retraction) response/hint event lists. When supplied, the
    item's record is rebuilt from those events, repairing a crash window in
    which evidence was durable but the session write was not -- without
    replaying any disclosure. Returns the session dict.
    """
    import runtime
    state = session.get("teaching_state")
    if not isinstance(state, dict):
        state = {}
        session = dict(session, teaching_state=state)
    if evidence_state:
        key = runtime.teaching_key(q)
        events = evidence_state.get(key)
        if events:
            state[key] = runtime._record_from_evidence(q, events)
    return session


def marker_close(session, q, settled_marks):
    """Close a sitting parked on an answered item whose mark is now settled.

    This is the "after" in `exam must not move the cursor before an accepted
    mark`. A pending prose answer parks the sitting at the marker's desk, and
    before 2026-08-24 nothing ever collected it: `mark` appends an evidence
    event and never touches a session, so a bank holding one short item could
    not be completed on any surface. `lti_roundtrip` reached that state only by
    hand-writing cursor and status into the session file.

    Returns the advanced session, or None when the item is not settled, so the
    caller can tell "moved" from "still parked" without comparing cursors. The
    cursor arithmetic stays here because the runtime owns session state; the
    caller supplies only the facts, since this module reads no files.
    """
    import runtime
    if not settled_marks or runtime.teaching_key(q) not in settled_marks:
        return None
    cursor, status = runtime._advance_cursor(session)
    return dict(session, cursor=cursor, status=status)


def formal_response_close(session, q, recorded_response):
    """Recover a silent formal advance after evidence outlived a session write.

    The session adapter supplies a live response for the current item. This
    runtime function alone decides whether that response closes the cursor.
    Practice remains parked on pending prose and retains its own retry flow.
    """
    import runtime
    if session.get("mode") not in ("exam", "diagnostic") or not recorded_response:
        return None
    if (recorded_response.get("item_ref") != q.get("id") or
            recorded_response.get("session_id") != session.get("session_id") or
            recorded_response.get("event_type") != "response"):
        return None
    cursor, status = runtime._advance_cursor(session)
    return dict(session, cursor=cursor, status=status)


def _advance_cursor(session):
    """Cursor advance shared by every advancing action; returns the next
    cursor and status."""
    import runtime
    cursor = session["cursor"] + 1
    status = session["status"]
    if cursor >= len(session["items"]):
        status = "complete"
    return cursor, status


TIER_HEADER_WORDS = ("LESSON", "OBJECTIVE", "TRAP", "RATIONALE",
                     "DISCRIMINATOR", "REVEAL")


LADDER_UNAVAILABLE_REASONS = {
    "drill": "Drill mode shows the answer straight away. The hint ladder does "
             "not run here.",
    "diagnostic": "Diagnostic mode records your answers and shows nothing "
                  "until the sitting ends.",
    "exam": "Exam mode holds all feedback until this attempt has been marked.",
}


LADDER_UNAVAILABLE_DEFAULT = ("This sitting's feedback mode does not run the "
                              "hint ladder.")


NEXT_TIER_UNLOCK_COPY = ("Tier %d unlocks after another attempt.",
                         "Or unlock it now with \"I'm stumped\".")


FURTHER_TIER_UNLOCK_COPY = "Tier %d unlocks after tier %d."


NEXT_TIER_ENTITLED_COPY = "Tier %d is unlocked."


MORE_TIERS_COPY = "%d more tiers after this one."


NO_AUTHORED_TIER_COPY = "This item has no authored %s."


def _tier_header(q, index, canonical):
    """One tier's Ledger header: `TIER {n} - {WORD}`, with tier 3 naming the
    option the learner actually picked. Resolved here and never by a client:
    a surface that rebuilt this string from a tier id would be a second place
    deciding how a tier introduces itself.
    """
    import runtime
    word = runtime.TIER_HEADER_WORDS[index]
    if index == 3 and canonical and q["type"] in ("mc", "multi"):
        option = str(canonical).split(",")[0].strip()
        if option:
            word = "%s FOR %s" % (word, option)
    return "TIER %d · %s" % (index, word)


def teaching_payload(q, rec, mode, locked_preview="full"):
    """The whole of what a surface may know about the authored hint ladder
    for one item (14-UI-SPEC section 9.1, LOCKED). Pure: it reads no file,
    writes nothing, touches no session, and reads no settings -- the caller
    resolves `locked_preview` server-side and passes it in, so a client can
    never widen its own preview (T-14-11).

    `rec` is a `new_teaching_record()`-shaped dict, `mode` the sitting's
    feedback mode, `locked_preview` the resolved `teaching.hint_locked_preview`
    value (`full` or `next`).

    Returned keys:

      available          -- false in any mode whose FEEDBACK_POLICIES `wrong`
                            entry is not `hold`. Derived from that table, not
                            from a mode list restated here.
      unavailable_reason -- null when available, else the mode's own sentence.
      shown              -- one entry per already-disclosed tier, in index
                            order: {index, name, label, header, display,
                            available}. `display` is the text the runtime
                            already resolved (`authored_hint`'s own `display`),
                            or the inherited no-authored-content sentence.
                            `available` is disclosed information ON A SHOWN
                            TIER only (06-UI-SPEC section 5.2 discloses
                            availability at the moment a tier is shown).
      next_locked        -- {index, name, header, unlock_copy} for the single
                            next undisclosed tier, or null when none remains.
      further_locked     -- the locked tiers after that one, each {name,
                            header, unlock_copy} and deliberately NO index:
                            their number already appears inside their own
                            locked copy, and nothing else needs it. Empty
                            under `locked_preview: next`, which instead
                            appends the inherited count line to next_locked.
      entitled           -- a tier is unlocked and not yet shown.
      exhausted          -- the last tier has been shown.
      unlock_path        -- "attempt" when entitled, else "stumped"; null when
                            the ladder does not run, because a refused ladder
                            has no path rather than a stumped one.

    What it never contains, and what the fixtures assert: an undisclosed
    tier's body or `content`, an undisclosed tier's availability,
    `highest_tier_unlocked` or `attempt_count`, or anything else a client
    could turn into a request naming a tier. There is no request shape that
    names a tier because there is nothing in this payload to name one with.
    """
    import runtime
    if rec is None:
        rec = runtime.new_teaching_record()
    policy = runtime.FEEDBACK_POLICIES.get(mode, runtime.FEEDBACK_POLICIES["practice"])
    if policy["wrong"] != "hold":
        # 06-UI-SPEC section 6.5: absent with a stated reason, never a rail of
        # greyed cards. Nothing about the item's tiers crosses this branch.
        return {"available": False,
                "unavailable_reason": runtime.LADDER_UNAVAILABLE_REASONS.get(
                    mode, runtime.LADDER_UNAVAILABLE_DEFAULT),
                "shown": [], "next_locked": None, "further_locked": [],
                "entitled": False, "exhausted": False, "unlock_path": None}

    canonical = rec.get("last_genuine_canonical")
    highest_shown = rec.get("highest_tier_shown", -1)
    highest_unlocked = rec.get("highest_tier_unlocked", -1)

    # The ladder is monotone: `highest_tier_shown` IS the disclosed set, and
    # it is the same number `_next_reveal` reveals against, so the payload and
    # the transition can never disagree about where the boundary sits.
    shown = []
    for index in range(highest_shown + 1):
        tier = runtime.authored_hint(q, index, canonical)
        shown.append({
            "index": index,
            "name": tier["name"],
            "label": tier["label"],
            "header": runtime._tier_header(q, index, canonical),
            "display": tier["display"] if tier["available"]
                       else runtime.NO_AUTHORED_TIER_COPY % tier["label"],
            "available": tier["available"],
        })

    next_index = highest_shown + 1
    exhausted = next_index >= len(runtime.HINT_TIERS)
    entitled = highest_unlocked > highest_shown

    next_locked = None
    further_locked = []
    if not exhausted:
        unlock_copy = ([runtime.NEXT_TIER_ENTITLED_COPY % next_index] if entitled else
                       [runtime.NEXT_TIER_UNLOCK_COPY[0] % next_index,
                        runtime.NEXT_TIER_UNLOCK_COPY[1]])
        remaining = list(range(next_index + 1, len(runtime.HINT_TIERS)))
        if locked_preview == "next":
            if remaining:
                unlock_copy.append(runtime.MORE_TIERS_COPY % len(remaining))
        else:
            further_locked = [
                {"name": runtime.HINT_TIERS[i]["name"],
                 "header": runtime._tier_header(q, i, canonical),
                 "unlock_copy": [runtime.FURTHER_TIER_UNLOCK_COPY % (i, i - 1)]}
                for i in remaining]
        next_locked = {"index": next_index,
                       "name": runtime.HINT_TIERS[next_index]["name"],
                       "header": runtime._tier_header(q, next_index, canonical),
                       "unlock_copy": unlock_copy}

    return {"available": True, "unavailable_reason": None,
            "shown": shown, "next_locked": next_locked,
            "further_locked": further_locked,
            "entitled": entitled, "exhausted": exhausted,
            "unlock_path": "attempt" if entitled else "stumped"}
