"""Scoring, sessions, and the payloads a surface is allowed to see.

The only scorer lives here. Every surface reaches a verdict by calling into this
module rather than by reimplementing the rules, browser page included. That is
what stops the CLI, the JSON session interface and the quiz page from quietly
disagreeing about the same response.

It also draws the line the whole tool rests on: `public_item` is what a learner
may see before answering and `explain_payload` is what they may see after. A
surface that wants more than the first one has to ask.
"""
import collections, json, os, sys


# ---- agent assessment runtime ----------------------------------------------
# The browser is a presentation adapter. These helpers are the shared runtime
# contract for the CLI and future adapters, so an agent never has to scrape HTML
# or infer whether its response was accepted.

# Each published contract carries its own version because they evolve
# independently; the matching documents live under `schemas/`.
#
# Version 2 (Phase 6) adds the versioned `teaching_state`: per-item attempt
# count, highest tier unlocked/shown, the last genuine canonical response and
# its response event id, and the ordered shown-tier snapshots (D-03). The
# v1-to-v2 upgrade in SESSION_UPGRADES initializes an empty teaching_state so
# a session written before the hint ladder resumes under the new contract.
SESSION_VERSION = 2
ITEM_VERSION = 1
REPORT_VERSION = 1
# The public interaction-contract version for a check item (plan 05-01):
# the submit route and the normalized result carry it, and the evidence event
# records it, so the three can never disagree about which contract served.
INTERACTION_VERSION = 1


def public_item(q, shuffle_seed=0):
    """Return an item safe to show before the learner answers."""
    out = {"schema_version": ITEM_VERSION, "id": q["id"], "number": q["number"],
           "type": q["type"], "stem": q["stem"],
           "difficulty": q.get("difficulty", ""), "lesson_slug": q.get("lesson_slug", "")}
    if q["type"] in ("mc", "multi"):
        out["options"] = [{"key": k, "text": q["opts"][k]} for k in sorted(q["opts"])]
        out["response_schema"] = {"type": "array" if q["type"] == "multi" else "string",
                                   "select": q["select"], "allowed": sorted(q["opts"])}
    elif q["type"] in ("table", "dnd"):
        out["rows"] = [{"text": r["text"], "id": i} for i, r in enumerate(q["rows"])]
        out["categories"] = q["cats"]
        out["response_schema"] = {"type": "object", "keys": "row id", "values": q["cats"]}
    elif q["type"] == "build":
        import random
        steps = q["steps"][:]
        random.Random(shuffle_seed).shuffle(steps)
        out["steps"] = steps
        out["response_schema"] = {"type": "array", "items": "step text", "ordered": True}
    elif q["type"] == "short":
        out["response_schema"] = {"type": "string", "min_length": 2}
    elif q["type"] == "check":
        # One renderer-independent interaction contract (D-12): a declarative
        # renderer_config with the language, the starter source and the hidden
        # case count, and a response_schema declaring the raw source string.
        # The config is validated at this boundary before any renderer sees
        # it, and it contains JSON data only -- never bank-authored code, a
        # callable, a case input, expected output, or a key. The top-level
        # response_schema aliases the envelope's for the additive
        # compatibility contract the five earlier types use.
        lang = q.get("lang", "python")
        config = {
            "version": INTERACTION_VERSION,
            "type": "check",
            "renderer_config": {
                "language": lang,
                "starter_source": q.get("starter", ""),
                "hidden_case_count": len(q.get("cases") or []),
            },
            "response_schema": {"type": "string", "format": "source",
                                "language": lang},
        }
        _validate_interaction_contract(config)
        out["interaction_contract"] = config
        out["response_schema"] = config["response_schema"]
        out["starter"] = q.get("starter", "")
    return out


def _validate_interaction_contract(config):
    """The public_item boundary gate for a check item's interaction contract:
    the envelope and the renderer_config must carry exactly the declared keys
    with the declared value kinds, and the whole config must serialize as JSON
    data -- no callables, no case material, no key. A config built from a
    parsed question can never fail this; it exists so a future caller cannot
    slip something through the boundary unnoticed."""
    if not isinstance(config, dict):
        raise ValueError("interaction contract must be an object")
    for key in ("version", "type", "renderer_config", "response_schema"):
        if key not in config:
            raise ValueError("interaction contract missing %r" % key)
    if config["type"] != "check":
        raise ValueError("interaction contract type must be 'check'")
    rc = config["renderer_config"]
    if not isinstance(rc, dict):
        raise ValueError("renderer_config must be an object")
    for key in ("language", "starter_source", "hidden_case_count"):
        if key not in rc:
            raise ValueError("renderer_config missing %r" % key)
    if not isinstance(rc["hidden_case_count"], int)             or isinstance(rc["hidden_case_count"], bool):
        raise ValueError("hidden_case_count must be an integer")
    if not isinstance(config["response_schema"], dict):
        raise ValueError("response_schema must be an object")
    json.dumps(config)      # JSON data only: a callable or a non-JSON value dies here


def _check_observation(q, index, case_result):
    """One ordered, 1-based observation for a check item's normalized result:
    the stable reason code, the already-bounded actual output, the post-submit
    authored expected value and input. This is data for feedback, never a
    second scoring path -- `passed` is copied from the run, not recomputed."""
    case = (q.get("cases") or [])[index]
    timed_out = bool(case_result.get("timed_out"))
    truncated = bool(case_result.get("truncated"))
    if timed_out:
        reason = "timeout"
    elif truncated:
        reason = "output_cap"
    elif case_result.get("passed"):
        reason = "passed"
    else:
        reason = "wrong_output"
    return {
        "case_index": index + 1,
        "passed": bool(case_result.get("passed")),
        "reason": reason,
        "actual": case_result.get("actual", ""),
        "expected": case["expected"],
        "expected_kind": "pattern" if q.get("match") == "regex" else "output",
        "input": case.get("call") if q.get("harness") else case.get("stdin", ""),
    }


def interaction_result(q, source, verdict, run_result):
    """The normalized post-submit result for a check item, used by every
    submitting surface.

    It does not grade: `verdict` must be the exact value already returned by
     `score_response()` -- True, False, or None for a run the deadline killed
    (criterion 12). The ordered observations stay present even for a None
    verdict so the learner sees which case timed out, but no surface may
    render a pending response as pass or fail.
    """
    return {
        "version": INTERACTION_VERSION,
        "type": "check",
        "response": source,
        "verdict": verdict,
        "observations": [_check_observation(q, i, r)
                         for i, r in enumerate(run_result or [])],
    }


def normalize_answer(answer):
    if isinstance(answer, str):
        try:
            return json.loads(answer)
        except (TypeError, ValueError):
            return answer.strip()
    return answer


# Field and record separators for the canonical form. Control characters rather
# than punctuation because option text and build steps contain commas, pipes and
# ">" often enough that any printable separator eventually collides with content
# and scores a correct response wrong.
FIELD_SEP = "\x1f"


PAIR_SEP = "\x1e"


def _canonical_mc(q, answer):
    if isinstance(answer, list):
        answer = answer[0] if len(answer) == 1 else ""
    return str(answer).strip().upper() if isinstance(answer, str) else ""


def _canonical_multi(q, answer):
    given = answer if isinstance(answer, list) else [answer]
    return ",".join(sorted(str(x).strip().upper() for x in given))


def _canonical_table_dnd(q, answer):
    if isinstance(answer, list):
        answer = {str(i): v for i, v in enumerate(answer)}
    if not isinstance(answer, dict) or len(answer) != len(q["rows"]):
        return ""          # a partial or padded assignment is not a response
    return FIELD_SEP.join("%d%s%s" % (i, PAIR_SEP, answer.get(str(i), ""))
                          for i in range(len(q["rows"])))


def _canonical_build(q, answer):
    return FIELD_SEP.join(str(x) for x in answer) if isinstance(answer, list) else ""


def check_normalizer(q, answer):
    """Reduce a check item's per-case results to the outcome vector string.

     `answer` is one of: the list of per-case dicts the runner returns
    (the live path), a list of 0/1 ints (test callers), or the
    already-canonical vector string (when idempotency re-enters). A case that
    timed out is not a verdict: the run was killed, so this returns None and
    the response lands pending rather than wrong (criterion 12).
    """
    if isinstance(answer, str):
        return answer                 # already-canonical (idempotency re-entry)
    if isinstance(answer, list):
        if any(isinstance(c, dict) and c.get("timed_out") for c in answer):
            return None
        if answer and all(isinstance(c, dict) for c in answer):
            return ",".join("1" if c.get("passed") else "0" for c in answer)
        return ",".join("1" if c else "0" for c in answer)
    return None


# The two registries (criterion 11): a normalizer reduces (q, answer) to one
# comparable string or None; a key answers "what is the correct canonical
# form" for an item. The five legacy types' branches moved in unchanged;
# `short` is deliberately absent -- its responses are pending by design, and
# a registry miss is exactly that state (D-21).
NORMALIZERS = {
    "mc": _canonical_mc, "multi": _canonical_multi,
    "table": _canonical_table_dnd, "dnd": _canonical_table_dnd,
    "build": _canonical_build, "check": check_normalizer,
}


def _key_mc(q):
    return q["correct"][0]


def _key_multi(q):
    return ",".join(sorted(q["correct"]))


def _key_table_dnd(q):
    return FIELD_SEP.join("%d%s%s" % (i, PAIR_SEP, r["cat"])
                          for i, r in enumerate(q["rows"]))


def _key_build(q):
    return FIELD_SEP.join(q["steps"])


def check_key(q):
    """As many ones as the item has cases."""
    return ",".join("1" for _ in q.get("cases") or [])


KEYS = {
    "mc": _key_mc, "multi": _key_multi,
    "table": _key_table_dnd, "dnd": _key_table_dnd,
    "build": _key_build, "check": check_key,
}


def canonical_response(q, answer):
    """Reduce a selected response to one comparable string.

    Three consumers need to agree on what a response *is*: the scorer compares
    two of these, the static `build` page compares the learner's against a key
    computed here, and the attempt record stores what was given. Putting the
    shape in one function is what lets the browser stop deciding correctness
    while still being able to self-check offline, where there is no process to
    ask. Returns None for constructed response, which has no canonical form.
    """
    answer = normalize_answer(answer)
    normalizer = NORMALIZERS.get(q["type"])
    if normalizer is None:
        return None     # no registered normalizer: no canonical form
    return normalizer(q, answer)


def canonical_key(q):
    """The canonical response that is correct, in the same shape as the above."""
    key = KEYS.get(q["type"])
    if key is None:
        return None
    return key(q)


def score_response(q, answer):
    """The only scorer. Every surface reaches a verdict through this function.

    Constructed response returns None rather than False: not-yet-marked and
    marked-wrong are different states, and collapsing them would let a pending
    item read as a failure in the evidence.
    """
    key = canonical_key(q)
    if key is None:
        return None
    canon = canonical_response(q, answer)
    if canon is None:
        return None          # a None canonical is not a False verdict (check timeout)
    return canon == key


def session_path(path):
    return os.path.abspath(path)


# Registered forward-upgrade functions, keyed by the source version each one
# upgrades from. Version 1 is the only older version that has ever existed;
# the registry exists so every bump is a one-function change to
# SESSION_UPGRADES rather than a rewrite of read_session.
SESSION_UPGRADES = {
    1: lambda data: dict(data, teaching_state={}),
}


def upgrade_session(data):
    """Carry a session dict forward to SESSION_VERSION, one registered step
    at a time.

    A non-integer `schema_version` and a version above what this build
    understands each exit with a named error rather than guessing at a
    shape. This is the migration path `.planning/codebase/CONCERNS.md`
    flagged as missing: a version stamp with no way to move forward from it.
    """
    version = data.get("schema_version")
    if not isinstance(version, int):
        sys.exit("session has no valid schema_version (got %r)" % (version,))
    while version < SESSION_VERSION:
        upgrade = SESSION_UPGRADES.get(version)
        if upgrade is None:
            sys.exit("no upgrade path from session schema %d to %d" %
                     (version, SESSION_VERSION))
        data = upgrade(data)
        version += 1
        data["schema_version"] = version
    if version > SESSION_VERSION:
        sys.exit("session schema %d is newer than this build understands (%d); "
                 "upgrade itembank" % (version, SESSION_VERSION))
    return data


def read_session(path):
    try:
        data = json.load(open(session_path(path), encoding="utf-8"))
    except (OSError, ValueError) as exc:
        sys.exit("cannot read session %s: %s" % (path, exc))
    return upgrade_session(data)


def write_session(path, data):
    target = session_path(path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    tmp = target + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    os.replace(tmp, target)


def session_view(data, qs):
    selected = data["items"]
    cursor = data["cursor"]
    view = {"schema_version": SESSION_VERSION, "session_id": data["session_id"],
            "status": data["status"], "mode": data["mode"],
            "objective": data.get("objective", ""), "position": cursor,
            "total": len(selected), "responses": len(data["responses"])}
    if data["status"] == "active" and cursor < len(selected):
        view["item"] = public_item(qs[selected[cursor]], data.get("seed", 0) + cursor)
    else:
        view["summary"] = session_summary(data)
    return view


def session_summary(data):
    responses = data["responses"]
    auto = [r for r in responses if r["score"] is not None]
    correct = sum(1 for r in auto if r["score"] is True)
    by_objective = collections.defaultdict(lambda: {"attempts": 0, "correct": 0, "pending": 0})
    for r in responses:
        bucket = by_objective[r.get("objective") or "(unmapped)"]
        bucket["attempts"] += 1
        if r["score"] is None:
            bucket["pending"] += 1
        elif r["score"]:
            bucket["correct"] += 1
    return {"schema_version": REPORT_VERSION, "auto_attempts": len(auto),
            "auto_correct": correct, "pending_manual": len(responses) - len(auto),
            "objectives": dict(by_objective)}


def answer_text(q):
    """Compact answer text for study and export surfaces."""
    if q["type"] in ("mc", "multi"):
        return "; ".join("%s) %s" % (c, q["opts"][c]) for c in q["correct"])
    if q["type"] in ("table", "dnd"):
        return "; ".join("%s -> %s" % (r["text"], r["cat"]) for r in q["rows"])
    if q["type"] == "build":
        return " -> ".join(q["steps"])
    return q.get("model", "")


def glossable(qs, term):
    """The one gate between a term's definition and the learner: False when
    the definition text could disclose keyed answer material from any
    question in `qs`, True otherwise.

    This is the same class of decision as `public_item()` withholding a key:
    the runtime, not the author and not a model, decides what reaches the
    learner (Directive §4.1, D-20). It is deliberately conservative -- on any
    ambiguity it returns False. It is a pure function: no I/O, no side
    effects, deterministic across calls. It is NOT a secrecy mechanism
    against the file on disk: the learner owns the bank markdown, and
    UI-SPEC §8.4 states that plainly.

    The answer-bearing fragments are the plan's locked set: the correct
    option labels, the canonical key output of `canonical_key()`, and the
    collapsed key/answer text for short/build items.
    """
    def _collapse(s):
        return " ".join(str(s or "").split()).lower()

    definition = _collapse(term.get("def"))
    if not definition:
        return True
    for q in qs:
        t = q["type"]
        if t in ("mc", "multi"):
            frags = [q["opts"][c] for c in q["correct"]]
        elif t == "short":
            frags = [q.get("model", "")]
        elif t == "build":
            frags = list(q.get("steps") or [])
        else:
            frags = []
        key = canonical_key(q)
        if key is not None:
            frags.append(key)
        for frag in frags:
            frag = _collapse(frag)
            if frag and frag in definition:
                return False
    return True


def response_text(q, answer):
    """Human-readable rendering of what the learner actually gave.

    The attempt file records option text, not letters. Letters are reshuffled on
    every page load, so "B" in a saved attempt names a different option the next
    time the same bank is sat, which makes the record unreadable exactly when
    somebody comes back to mark it.
    """
    answer = normalize_answer(answer)
    t = q["type"]
    if t == "short":
        return str(answer or "")
    if t in ("mc", "multi"):
        given = answer if isinstance(answer, list) else [answer]
        keys = [str(k).strip().upper() for k in given]
        return "; ".join("%s) %s" % (k, q["opts"][k]) for k in keys if k in q["opts"])
    if t in ("table", "dnd"):
        if isinstance(answer, list):
            answer = dict((str(i), v) for i, v in enumerate(answer))
        if not isinstance(answer, dict):
            return ""
        return "; ".join("%s -> %s" % (r["text"], answer.get(str(i), "(unassigned)"))
                         for i, r in enumerate(q["rows"]))
    if t == "build":
        return " -> ".join(str(x) for x in answer) if isinstance(answer, list) else ""
    return ""


def explain_payload(q, reveal=True, run_result=None):
    """Everything the learner may see AFTER responding, and nothing before it.

    Under `serve` this is what the process hands back with the verdict, which is
    what lets the page render a full explanation while never having been sent a
    key it could leak or grade against.
    """
    out = {"answer_text": answer_text(q), "why": q.get("why", ""),
           # C7 (03.1-03): the syllabus reference and the one-sentence
           # Educational Objective line are answer-adjacent, so both live in
           # the post-verdict payload only -- never public_item().
           "objective": q.get("objective", ""),
           "educational_objective": q.get("objective_line", ""),
           "disc": q.get("disc", ""), "second": q.get("second", ""),
           "trap": q.get("trap", ""), "notes": q.get("notes") or []}
    t = q["type"]
    if t in ("mc", "multi"):
        out["correct"] = q["correct"]
        out["da"] = dict((k, v) for k, v in (q.get("da") or {}).items() if v)
    elif t in ("table", "dnd"):
        out["row_cats"] = dict((str(i), r["cat"]) for i, r in enumerate(q["rows"]))
    elif t == "build":
        out["steps"] = q["steps"]
    elif t == "short":
        # The model answer stays hidden unless asked for, because reading it
        # turns every item after this one into recognition rather than recall.
        out["model"] = q.get("model", "") if reveal else ""
        out["rubric"] = (q.get("rubric") or []) if reveal else []
        if not reveal:
            out["trap"] = ""
    elif t == "check":
        # With `run_result` the per-case actual output and the timed-out /
        # truncated flags are zipped against the authored input and expected
        # halves (the only channel through which actual output can reach the
        # explanation, D-15); without it the authored halves stand alone.
        rows = []
        for i, c in enumerate(q.get("cases") or []):
            row = {
                "case_index": i + 1,
                "input": c.get("call") if q.get("harness") else c.get("stdin", ""),
                "expected": c["expected"],
                "expected_kind": "pattern" if q.get("match") == "regex" else "output",
            }
            if run_result is not None and i < len(run_result):
                rc = run_result[i]
                row["actual"] = rc.get("actual", "")
                row["timed_out"] = bool(rc.get("timed_out"))
                row["truncated"] = bool(rc.get("truncated"))
            rows.append(row)
        out["cases"] = rows
    return out


def page_item(q, reveal=True, offline=False):
    """One item shape for the quiz page, in both of its modes.

    `serve` sends only the public half and scores in the process. A file:// page
    has no process to ask, so `build` additionally carries the canonical key and
    the explanation. That makes the static file the one surface holding a key on
    the client, which is a property of having no server rather than a second
    scoring model, and it is stated in the README rather than left implicit.
    """
    out = public_item(q)
    if offline:
        out["key"] = canonical_key(q)
        out["explain"] = explain_payload(q, reveal)
    return out


# ---- phase 6: the one feedback-policy engine -------------------------------
# D-01/D-02: one mode-keyed policy table and one teaching transition own every
# scoring, cursor-movement, tier-gating and disclosure decision for a sitting.
# A surface (CLI, daemon, browser) is a client of the returned action, never a
# second implementer of the rules. The transition is a pure function: it takes
# a session dict, an item and a Phase 6 action, and returns the next session
# dict plus an action. It never writes files, and it never accepts renderer,
# canvas, observation, or metadata parameters -- concrete interactive visual
# action/observation semantics belong exclusively to Phase 06.1.

# The six fixed authored tiers (D-07/D-08). An unavailable tier stays in its
# numbered slot: `authored_hint` returns `available: false` at the same index
# rather than shifting later content forward.
HINT_TIERS = (
    {"name": "lesson", "label": "lesson pointer"},
    {"name": "objective", "label": "objective"},
    {"name": "trap", "label": "trap"},
    {"name": "rationale", "label": "picked-option rationale"},
    {"name": "discriminator", "label": "discriminator"},
    {"name": "reveal", "label": "authored reveal"},
)

# One policy table keyed ONLY by feedback mode (D-01/D-10..D-13). `selection`
# is the Phase 7 axis and is deliberately absent: feedback policy never
# consults selection_mode.
FEEDBACK_POLICIES = {
    "drill": {"wrong": "advance", "right": "advance"},
    "practice": {"wrong": "hold", "right": "advance"},
    "diagnostic": {"wrong": "defer_feedback", "right": "defer_feedback"},
    "exam": {"wrong": "defer_feedback", "right": "defer_feedback"},
    # remediation was not one of the four planned Phase 6 modes, but it ships
    # in the session mode enum; practice's held-retry ladder is the honest
    # teaching behavior for it rather than an unhandled mode.
    "remediation": {"wrong": "hold", "right": "advance"},
    # 'legacy' appears only on events migrated from a pre-mode store; a
    # live session can never carry it, and a legacy mode must not pretend to
    # be a policy it never was.
    "legacy": {"wrong": "defer_feedback", "right": "defer_feedback"},
}


def new_teaching_record():
    """One item's persisted teaching state (D-03)."""
    return {"attempt_count": 0, "highest_tier_unlocked": -1,
            "highest_tier_shown": -1, "last_genuine_canonical": None,
            "last_response_event_id": None,
            "shown_tiers": []}


def _idempotent_canon(q, answer):
    """The canonical form the transition compares for duplicate detection.

    `canonical_response()` returns None for a constructed (short) response by
    design; idempotency still needs something comparable, so a short answer's
    whitespace-collapsed, lowercased text is used. This mirrors
    `evidence.idempotency_canon()` -- the two must agree, and the transition
    computes it locally to stay import-cycle-free.
    """
    canon = canonical_response(q, answer)
    if canon is not None:
        return canon
    text = " ".join(str(answer or "").split()).lower()
    return "short:" + text


def teaching_key(q):
    """The stable key teaching_state is indexed by: the opaque item id when
    one has been assigned, else the positional reference -- identical to
    `evidence.evidence_key()` (which cannot be imported here without a cycle).
    """
    return q.get("item_id") or ("ref:" + q["id"])


def authored_hint(q, tier, canonical):
    """The sole private-tier resolver for the six fixed authored tiers
    (D-07/D-08/D-09). Missing content returns `available: false` at the same
    index. Tier 3 is response-specific: it resolves the distractor analysis
    for the learner's latest genuine picked option.
    """
    t = HINT_TIERS[tier]
    name = t["name"]
    if tier == 0:
        slug = q.get("lesson_slug") or ""
        return {"index": 0, "name": name, "available": bool(slug),
                "content": slug, "label": t["label"]}
    if tier == 1:
        obj = q.get("objective") or ""
        return {"index": 1, "name": name, "available": bool(obj),
                "content": obj, "label": t["label"]}
    if tier == 2:
        trap = q.get("trap") or ""
        return {"index": 2, "name": name, "available": bool(trap),
                "content": trap, "label": t["label"]}
    if tier == 3:
        content = ""
        if canonical and q["type"] in ("mc", "multi"):
            option = str(canonical).split(",")[0].strip()
            content = (q.get("da") or {}).get(option, "")
        return {"index": 3, "name": name, "available": bool(content),
                "content": content, "label": t["label"],
                "for_response": canonical}
    if tier == 4:
        disc = q.get("disc") or ""
        return {"index": 4, "name": name, "available": bool(disc),
                "content": disc, "label": t["label"]}
    # tier == 5: the authored reveal -- the full post-response explanation.
    return {"index": 5, "name": name, "available": True,
            "content": explain_payload(q, reveal=True), "label": t["label"]}


def _record_from_evidence(q, events):
    """Pure fold of an item's live response/hint events into a teaching
    record -- the crash-window reconciliation input (D-15/D-16). `events` is
    the item's already-live (post-retraction) event list.
    """
    rec = new_teaching_record()
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
    next_index = rec["highest_tier_shown"] + 1
    if next_index >= len(HINT_TIERS):
        shown = list(rec["shown_tiers"])
        return {"tier": None, "shown": shown, "exhausted": True}, rec
    tier = authored_hint(q, next_index, rec["last_genuine_canonical"])
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
    state = session.get("teaching_state")
    if not isinstance(state, dict):
        state = {}
        session = dict(session, teaching_state=state)
    if evidence_state:
        key = teaching_key(q)
        events = evidence_state.get(key)
        if events:
            state[key] = _record_from_evidence(q, events)
    return session


def teaching_transition(session, q, action, evidence_state=None):
    """The one teaching transition (D-01/D-02): the sole authority for
    scoring, cursor movement, tier unlock/show state, completion, and
    disclosure. Accepts only Phase 6 action kinds -- submit, hint, stumped.

    Returns {"action": ..., "session": next_session, "hint": ...|None,
    "reveal": ...|None, "hint_tier": int|None}. The session adapter persists
    the returned session and appends response/hint events; the transition
    itself never writes files.
    """
    import evidence  # function-local: module-level would cycle (line 426)
    kind = action.get("kind")
    if kind not in ("submit", "hint", "stumped"):
        sys.exit("unknown teaching action %r (expected submit, hint, or stumped)"
                 % (kind,))
    mode = action.get("mode")
    if mode is not None and mode != session["mode"]:
        sys.exit("action mode %r does not match session mode %r; a sitting's "
                 "feedback mode is immutable (D-14)" % (mode, session["mode"]))

    session = reconcile_teaching_state(session, q, evidence_state)
    state = session["teaching_state"]
    rec = state.get(teaching_key(q))
    if rec is None:
        rec = new_teaching_record()

    if kind in ("hint", "stumped"):
        unlock_path = "stumped" if kind == "stumped" else "attempt"
        payload, next_rec = _next_reveal(q, rec, unlock_path)
        state = dict(state)
        state[teaching_key(q)] = next_rec
        return {"action": "reveal_tier", "hint": payload,
                "session": dict(session, teaching_state=state)}

    # kind == "submit"
    answer = normalize_answer(action.get("answer"))
    canon = _idempotent_canon(q, answer)
    genuine = bool(canon) and canon != rec["last_genuine_canonical"]
    score = score_response(q, answer)
    hint_tier = rec["highest_tier_shown"] if rec["highest_tier_shown"] >= 0 else None

    if (rec["highest_tier_shown"] >= len(HINT_TIERS) - 1
            and rec["highest_tier_shown"] >= 0):
        # The reveal has been shown: the next submit action advances without
        # manufacturing further attempts (D-06) -- even a repeat of the last
        # canonical response, because the disclosure already happened and
        # holding the card forever would manufacture exactly the false
        # attempts D-06 forbids.
        next_rec = dict(rec, attempt_count=rec["attempt_count"] + 1,
                        last_genuine_canonical=canon)
        state = dict(state)
        state[teaching_key(q)] = next_rec
        cursor, status = _advance_cursor(session)
        return {"action": "advance",
                "session": dict(session, teaching_state=state,
                                cursor=cursor, status=status),
                "hint_tier": hint_tier}

    if not genuine:
        # Empty, canonical-identical, or deduped replays unlock nothing and
        # move nothing (D-04/D-05).
        return {"action": "hold", "session": session,
                "hint_tier": hint_tier, "tier_unlocked": None}

    policy = FEEDBACK_POLICIES.get(session["mode"], FEEDBACK_POLICIES["practice"])

    if score is None:
        # A constructed response is pending review, never wrong (T-06-05).
        next_rec = dict(rec, attempt_count=rec["attempt_count"] + 1,
                        last_genuine_canonical=canon)
        state = dict(state)
        state[teaching_key(q)] = next_rec
        return {"action": "defer_feedback", "session": dict(session, teaching_state=state),
                "hint_tier": None}

    if score is False:
        if policy["wrong"] == "advance":
            # Drill: score once, reveal immediately, advance (D-10).
            next_rec = dict(rec, attempt_count=rec["attempt_count"] + 1,
                            last_genuine_canonical=canon)
            state = dict(state)
            state[teaching_key(q)] = next_rec
            cursor, status = _advance_cursor(session)
            return {"action": "advance",
                    "session": dict(session, teaching_state=state,
                                    cursor=cursor, status=status),
                    "hint_tier": None, "reveal": explain_payload(q, reveal=True)}
        if policy["wrong"] == "defer_feedback":
            next_rec = dict(rec, attempt_count=rec["attempt_count"] + 1,
                            last_genuine_canonical=canon)
            state = dict(state)
            state[teaching_key(q)] = next_rec
            return {"action": "defer_feedback",
                    "session": dict(session, teaching_state=state),
                    "hint_tier": None}
        # practice/remediation hold: at most one tier unlocks per genuine
        # wrong attempt (D-05); the lesson pointer is tier 0, and it becomes
        # available now.
        unlocked = max(rec["highest_tier_unlocked"] + 1, 0)
        if unlocked > len(HINT_TIERS) - 1:
            unlocked = len(HINT_TIERS) - 1
        next_rec = dict(rec, attempt_count=rec["attempt_count"] + 1,
                        highest_tier_unlocked=unlocked,
                        last_genuine_canonical=canon)
        state = dict(state)
        state[teaching_key(q)] = next_rec
        return {"action": "hold", "session": dict(session, teaching_state=state),
                "hint_tier": hint_tier, "tier_unlocked": unlocked}

    # score is True.
    if policy["right"] == "defer_feedback":
        next_rec = dict(rec, attempt_count=rec["attempt_count"] + 1,
                        last_genuine_canonical=canon)
        state = dict(state)
        state[evidence.evidence_key(q)] = next_rec
        return {"action": "defer_feedback",
                "session": dict(session, teaching_state=state),
                "hint_tier": None}
    next_rec = dict(rec, attempt_count=rec["attempt_count"] + 1,
                    last_genuine_canonical=canon)
    state = dict(state)
    state[teaching_key(q)] = next_rec
    cursor, status = _advance_cursor(session)
    action_name = "complete" if status == "complete" else "advance"
    return {"action": action_name,
            "session": dict(session, teaching_state=state,
                            cursor=cursor, status=status),
            "hint_tier": hint_tier}


def _advance_cursor(session):
    """Cursor advance shared by every advancing action; returns the next
    cursor and status."""
    cursor = session["cursor"] + 1
    status = session["status"]
    if cursor >= len(session["items"]):
        status = "complete"
    return cursor, status
