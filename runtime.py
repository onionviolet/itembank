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
SESSION_VERSION = 1
ITEM_VERSION = 1
REPORT_VERSION = 1


def public_item(q, shuffle_seed=0):
    """Return an item safe to show before the learner answers."""
    out = {"schema_version": ITEM_VERSION, "id": q["id"], "number": q["number"],
           "type": q["type"], "stem": q["stem"], "objective": q.get("objective", ""),
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
    return out


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
    t = q["type"]
    if t == "short":
        return None
    if t == "mc":
        if isinstance(answer, list):
            answer = answer[0] if len(answer) == 1 else ""
        return str(answer).strip().upper() if isinstance(answer, str) else ""
    if t == "multi":
        given = answer if isinstance(answer, list) else [answer]
        return ",".join(sorted(str(x).strip().upper() for x in given))
    if t in ("table", "dnd"):
        if isinstance(answer, list):
            answer = {str(i): v for i, v in enumerate(answer)}
        if not isinstance(answer, dict) or len(answer) != len(q["rows"]):
            return ""          # a partial or padded assignment is not a response
        return FIELD_SEP.join("%d%s%s" % (i, PAIR_SEP, answer.get(str(i), ""))
                              for i in range(len(q["rows"])))
    if t == "build":
        return FIELD_SEP.join(str(x) for x in answer) if isinstance(answer, list) else ""
    return ""


def canonical_key(q):
    """The canonical response that is correct, in the same shape as the above."""
    t = q["type"]
    if t == "short":
        return None
    if t == "mc":
        return q["correct"][0]
    if t == "multi":
        return ",".join(sorted(q["correct"]))
    if t in ("table", "dnd"):
        return FIELD_SEP.join("%d%s%s" % (i, PAIR_SEP, r["cat"])
                              for i, r in enumerate(q["rows"]))
    if t == "build":
        return FIELD_SEP.join(q["steps"])
    return ""


def score_response(q, answer):
    """The only scorer. Every surface reaches a verdict through this function.

    Constructed response returns None rather than False: not-yet-marked and
    marked-wrong are different states, and collapsing them would let a pending
    item read as a failure in the evidence.
    """
    key = canonical_key(q)
    if key is None:
        return None
    return canonical_response(q, answer) == key


def session_path(path):
    return os.path.abspath(path)


# Registered forward-upgrade functions, keyed by the source version each one
# upgrades from. Empty today because version 1 is the only version that has
# ever existed; the registry exists so the first bump is a one-function
# change to SESSION_UPGRADES rather than a rewrite of read_session.
SESSION_UPGRADES = {}


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


def explain_payload(q, reveal=True):
    """Everything the learner may see AFTER responding, and nothing before it.

    Under `serve` this is what the process hands back with the verdict, which is
    what lets the page render a full explanation while never having been sent a
    key it could leak or grade against.
    """
    out = {"answer_text": answer_text(q), "why": q.get("why", ""),
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
