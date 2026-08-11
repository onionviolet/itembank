"""Scoring, sessions, and the payloads a surface is allowed to see.

The only scorer lives here. Every surface reaches a verdict by calling into this
module rather than by reimplementing the rules, browser page included. That is
what stops the CLI, the JSON session interface and the quiz page from quietly
disagreeing about the same response.

It also draws the line the whole tool rests on: `public_item` is what a learner
may see before answering and `explain_payload` is what they may see after. A
surface that wants more than the first one has to ask.
"""
import collections, fractions, hashlib, json, os, re, sys


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
    elif q["type"] == "visual":
        # One renderer-independent interaction contract (plan 06.1-01): the
        # declarative scene and response grammar, key-free. The private
        # scoring envelope (accepted states, tolerance, partial_credit) is
        # never projected here -- it stays on the server item and is read
        # only by the visual scoring helpers below.
        contract = _visual_interaction_contract(q)
        out["interaction_contract"] = contract
        out["response_schema"] = contract["response_schema"]
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
    if t == "visual":
        state = canonical_visual_response(q, answer)
        if state is None:
            return ""
        return json.dumps(state, sort_keys=True)
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
    if t == "visual":
        # The accepted-state set, canonicalized -- used by the static/offline
        # page_item() path (which holds a key by design) and by nothing else:
        # served visual scoring goes through score_response()'s visual branch,
        # never this string comparison.
        states = []
        for raw in (q.get("scoring") or {}).get("accepted") or []:
            state = _canonical_accepted_state(q, raw)
            if state is not None:
                states.append(json.dumps(state, sort_keys=True))
        return FIELD_SEP.join(states)
    return ""


def score_response(q, answer):
    """The only scorer. Every surface reaches a verdict through this function.

    Constructed response returns None rather than False: not-yet-marked and
    marked-wrong are different states, and collapsing them would let a pending
    item read as a failure in the evidence.

    A visual response is validated, canonicalized and compared by the visual
    scoring helpers below; the verdict stays a plain boolean -- no partial
    credit, no client authority input, and invalid responses are rejected
    (False), never approximated.
    """
    key = canonical_key(q)
    if key is None:
        return None
    if q["type"] == "visual":
        return _visual_verdict(q, answer)
    return canonical_response(q, answer) == key


# ---- visual assessment protocol (plan 06.1-01) ------------------------------
# Protocol integer 1 covers plot points, number-line points, and intervals
# (D-01). Coordinates use the exact SCALAR grammar below, canonicalized with
# `fractions.Fraction`; browser floats and pixels are never evidence or
# scoring inputs. The public projection in public_item() emits only the scene,
# initial state, allowed semantic actions, response grammar, and accessibility
# text; accepted states, tolerance, misconception mapping and reveal content
# stay on the server item (D-02/D-03).
VISUAL_PROTOCOL_VERSION = 1
VISUAL_TOLERANCE_POLICY_VERSION = 1

# Locked protocol-1 bounds (06.1-RESEARCH.md "Locked bounds").
SCALAR_MAX_NUMERATOR = 1_000_000_000
SCALAR_MAX_DENOMINATOR = 1_000_000
VISUAL_MAX_TICKS = 201

VISUAL_INTERACTIONS = ("plot", "numberline")
VISUAL_KINDS = ("point", "numberline_point", "interval")
# The only protocol-1 committed-action types (D-05); final submit is the
# ordinary response event and is never duplicated as a visual action.
VISUAL_ACTIONS = ("place_point", "move_point",
                  "select_numberline_point", "set_interval")
# The closed allowlist of authored scene members (T-06.1-03): anything else is
# rejected before a renderer sees it.
_VISUAL_SCENE_MEMBERS = frozenset({"version", "axes", "axis", "initial",
                                   "actions", "accessibility"})
_VISUAL_SCORING_MEMBERS = frozenset({"kind", "accepted", "tolerance",
                                     "partial_credit", "feedback"})
# Script-bearing tokens scanned recursively over scene/scoring JSON; a match
# rejects the member before rendering (T-06.1-03). Event-handler keys are
# matched as bare words (`onload`), and common executable call patterns are
# matched in values (`alert(`, `eval(`, ...).
_VISUAL_EXEC_RE = re.compile(
    r"<\s*script|javascript:|eval\s*\(|new\s+Function|setTimeout|setInterval|"
    r"document\.|window\.|innerHTML\s*=|alert\s*\(|prompt\s*\(|confirm\s*\(|"
    r"location\.|localStorage|sessionStorage|fetch\s*\(|XMLHttpRequest|"
    r"(?:^|[^A-Za-z0-9])on(?:click|load|mouse|pointer|touch|key|input|change|"
    r"focus|blur|submit|error|dblclick|wheel|unload|resize|scroll|over|out)"
    r"\b", re.I)

# One SCALAR: a signed base-10 integer/decimal with at most six fractional
# digits, or a rational `INTEGER/POSITIVE_INTEGER`. Exponents, NaN,
# infinities, mixed numbers, units and symbolic expressions are invalid.
_SCALAR_RE = re.compile(r"^[+-]?(\d+(\.\d{1,6})?|\d+/\d+)$")


def canonical_scalar(s):
    """Reduce one SCALAR string to its exact canonical form, or None.

    Canonicalization uses `fractions.Fraction`: rationals reduce, decimal
    trailing zeroes are stripped (`"2.50"` -> `"5/2"`), negative zero maps to
    `"0"`, and numerator/denominator magnitude is bounded. The result is what
    a renderer must serialize and what the runtime compares -- never a
    browser float.
    """
    if not isinstance(s, str):
        return None
    s = s.strip()
    if not _SCALAR_RE.match(s):
        return None
    try:
        f = fractions.Fraction(s)
    except (ValueError, ZeroDivisionError):
        return None
    if abs(f.numerator) > SCALAR_MAX_NUMERATOR:
        return None
    if f.denominator > SCALAR_MAX_DENOMINATOR:
        return None
    if f.denominator == 1:
        return str(f.numerator)          # -0 -> "0", "2.0" -> "2"
    return "%d/%d" % (f.numerator, f.denominator)


def canonical_axis(axis):
    """Validate one axis dict `{min, max, step}`; return the canonical axis
    with its tick count, or None when the geometry is invalid.

    `min`/`max`/`step` must be SCALARs, `step` strictly positive, `max > min`,
    and the span must divide into at most 200 whole steps (201 ticks, D-01).
    """
    if not isinstance(axis, dict):
        return None
    lo = canonical_scalar(axis.get("min", ""))
    hi = canonical_scalar(axis.get("max", ""))
    st = canonical_scalar(axis.get("step", ""))
    if None in (lo, hi, st):
        return None
    lo_f, hi_f, st_f = (fractions.Fraction(lo), fractions.Fraction(hi),
                        fractions.Fraction(st))
    if st_f <= 0 or hi_f <= lo_f:
        return None
    span = (hi_f - lo_f) / st_f
    if span.denominator != 1 or span.numerator > VISUAL_MAX_TICKS - 1:
        return None
    return {"min": lo, "max": hi, "step": st, "ticks": span.numerator + 1}


def visual_axes(q):
    """The validated scene axes for a visual item, keyed by the interaction
    shape: `{"x": ..., "y": ...}` for plot, `{"axis": ...}` for numberline.
    Returns None when the scene is absent or geometrically invalid."""
    scene = q.get("visual")
    if not isinstance(scene, dict):
        return None
    interaction = q.get("interaction")
    if interaction == "plot":
        axes = scene.get("axes")
        if not isinstance(axes, dict):
            return None
        x, y = canonical_axis(axes.get("x")), canonical_axis(axes.get("y"))
        if x is None or y is None:
            return None
        return {"x": x, "y": y}
    if interaction == "numberline":
        axis = canonical_axis(scene.get("axis"))
        if axis is None:
            return None
        return {"axis": axis}
    return None


def _scalar_in_axis(axis, value):
    lo, hi = fractions.Fraction(axis["min"]), fractions.Fraction(axis["max"])
    v = fractions.Fraction(value)
    return lo <= v <= hi


def _scalar_on_grid(axis, value):
    """Whether `value` lands exactly on a declared tick of `axis`."""
    lo = fractions.Fraction(axis["min"])
    st = fractions.Fraction(axis["step"])
    offset = (fractions.Fraction(value) - lo) / st
    return offset.denominator == 1 and 0 <= offset.numerator < axis["ticks"]


def canonical_visual_response(q, answer):
    """Reduce a submitted visual response to the canonical semantic state, or
    None when it is invalid.

    The wire shapes are exactly `{"kind":"point","x":S,"y":S}`,
    `{"kind":"numberline_point","value":S}` and
    `{"kind":"interval","start":S,"end":S,"start_closed":B,"end_closed":B}`
    (D-01). Interval endpoints canonicalize into ascending order with their
    closure flags swapped when needed. A response carrying undeclared keys,
    non-bool closures, malformed scalars, or the wrong kind is invalid --
    including forged verdict/tier/tolerance fields, which are never read.
    """
    if isinstance(answer, str):
        try:
            answer = json.loads(answer)
        except (TypeError, ValueError):
            return None
    if not isinstance(answer, dict):
        return None
    kind = answer.get("kind")
    declared = (q.get("scoring") or {}).get("kind")
    if kind != declared or kind not in VISUAL_KINDS:
        return None
    if kind == "point":
        if set(answer) != {"kind", "x", "y"}:
            return None
        x, y = canonical_scalar(answer.get("x", "")), canonical_scalar(answer.get("y", ""))
        if x is None or y is None:
            return None
        return {"kind": "point", "x": x, "y": y}
    if kind == "numberline_point":
        if set(answer) != {"kind", "value"}:
            return None
        value = canonical_scalar(answer.get("value", ""))
        if value is None:
            return None
        return {"kind": "numberline_point", "value": value}
    # interval
    if set(answer) != {"kind", "start", "end", "start_closed", "end_closed"}:
        return None
    start = canonical_scalar(answer.get("start", ""))
    end = canonical_scalar(answer.get("end", ""))
    start_closed = answer.get("start_closed")
    end_closed = answer.get("end_closed")
    if None in (start, end) or not isinstance(start_closed, bool) \
            or not isinstance(end_closed, bool):
        return None
    if fractions.Fraction(start) > fractions.Fraction(end):
        start, end = end, start
        start_closed, end_closed = end_closed, start_closed
    return {"kind": "interval", "start": start, "end": end,
            "start_closed": start_closed, "end_closed": end_closed}


def _canonical_accepted_state(q, raw):
    """Canonicalize one authored SCORING.accepted entry.

    The accepted list omits `kind` -- it is inherited from the envelope's
    `SCORING.kind` (06.1-RESEARCH.md grammar), while a learner's wire
    response carries it. Injecting the declared kind before canonicalizing
    keeps one canonicalizer for both sides; a raw entry that names a
    different kind is invalid.
    """
    if isinstance(raw, dict) and "kind" not in raw:
        raw = dict(raw, kind=(q.get("scoring") or {}).get("kind"))
    return canonical_visual_response(q, raw)


def _visual_verdict(q, answer):
    """The one boolean visual verdict (D-02): canonicalize, validate against
    the authored domain/grid, then compare within the private tolerance.
    Invalid responses are rejected (False), never scored by approximation.

    Named `_visual_verdict` rather than `*_score` on purpose: the repository's
    structural one-scorer invariant (`tests/scoring_roundtrip.py`) scans for
    `def *score*(` and requires exactly `score_response` -- this helper is
    reachable only through it and must not read as a second scorer."""
    state = canonical_visual_response(q, answer)
    if state is None:
        return False
    axes = visual_axes(q)
    if axes is None:
        return False
    if not visual_state_in_domain(q, state, axes):
        return False
    scoring = q.get("scoring") or {}
    tolerance = scoring.get("tolerance") or {}
    tol = {}
    for key, raw in tolerance.items():
        t = canonical_scalar(raw)
        if t is None:
            return False
        tol[key] = fractions.Fraction(t)
    discrete = not any(f > 0 for f in tol.values())
    if discrete and not visual_state_on_grid(q, state, axes):
        return False
    for accepted in (scoring.get("accepted") or []):
        acc = _canonical_accepted_state(q, accepted)
        if acc is None:
            continue
        if visual_within_tolerance(state, acc, tol):
            return True
    return False


def visual_state_in_domain(q, state, axes=None):
    axes = axes or visual_axes(q)
    if axes is None:
        return False
    kind = state["kind"]
    if kind == "point":
        return (_scalar_in_axis(axes["x"], state["x"])
                and _scalar_in_axis(axes["y"], state["y"]))
    if kind == "numberline_point":
        return _scalar_in_axis(axes["axis"], state["value"])
    return (_scalar_in_axis(axes["axis"], state["start"])
            and _scalar_in_axis(axes["axis"], state["end"]))


def visual_state_on_grid(q, state, axes=None):
    """Whether every coordinate lands exactly on a declared tick. Only
    meaningful for discrete (zero-tolerance) items."""
    axes = axes or visual_axes(q)
    if axes is None:
        return False
    kind = state["kind"]
    if kind == "point":
        return (_scalar_on_grid(axes["x"], state["x"])
                and _scalar_on_grid(axes["y"], state["y"]))
    if kind == "numberline_point":
        return _scalar_on_grid(axes["axis"], state["value"])
    return (_scalar_on_grid(axes["axis"], state["start"])
            and _scalar_on_grid(axes["axis"], state["end"]))


def visual_within_tolerance(state, accepted, tol):
    """Per-coordinate `|submitted - accepted| <= tolerance`, with closure
    equality for intervals. A tolerance of 0 is exact equality after
    canonicalization. `tol` maps coordinate names to Fractions."""
    kind = state["kind"]
    if state["kind"] != accepted["kind"]:
        return False

    def within(a, b, key):
        return abs(fractions.Fraction(a) - fractions.Fraction(b)) \
            <= tol.get(key, fractions.Fraction(0))

    if kind == "point":
        return within(state["x"], accepted["x"], "x") \
            and within(state["y"], accepted["y"], "y")
    if kind == "numberline_point":
        return within(state["value"], accepted["value"], "value")
    return (within(state["start"], accepted["start"], "start")
            and within(state["end"], accepted["end"], "end")
            and state["start_closed"] == accepted["start_closed"]
            and state["end_closed"] == accepted["end_closed"])


def _reject_visual_exec(member, where):
    """Recursively scan one authored JSON member and reject any string or key
    carrying a script-bearing token, so no bank content can become browser
    code (T-06.1-03). Raises ValueError with the offending path."""
    if isinstance(member, str):
        if _VISUAL_EXEC_RE.search(member):
            raise ValueError("visual %s carries a script-bearing value" % where)
    elif isinstance(member, dict):
        for key, value in member.items():
            if _VISUAL_EXEC_RE.search(str(key)):
                raise ValueError("visual %s carries a script-bearing key %r"
                                 % (where, key))
            _reject_visual_exec(value, where)
    elif isinstance(member, list):
        for item in member:
            _reject_visual_exec(item, where)


def _visual_response_schema(kind):
    if kind == "point":
        return {"type": "object", "kind": "point",
                "fields": {"x": "scalar", "y": "scalar"}}
    if kind == "numberline_point":
        return {"type": "object", "kind": "numberline_point",
                "fields": {"value": "scalar"}}
    return {"type": "object", "kind": "interval",
            "fields": {"start": "scalar", "end": "scalar",
                       "start_closed": "boolean", "end_closed": "boolean"}}


def _visual_interaction_contract(q):
    """Build the key-free public interaction contract for a visual item,
    validating the declarative scene and scoring envelope first.

    The contract carries exactly `version`, `type`, `interaction`,
    `renderer_config` (scene, initial state, actions, accessibility) and
    `response_schema` -- never accepted states, tolerance, partial_credit,
    reveal content, or any scoring authority (D-02/D-03). Raises ValueError
    on unknown members, executable/script-bearing content, an invalid scene,
    or a malformed scoring envelope, so a bad bank fails before a renderer
    sees it.
    """
    interaction = q.get("interaction")
    if interaction not in VISUAL_INTERACTIONS:
        raise ValueError(
            "visual item %s: unknown INTERACTION %r (protocol %d supports %s)"
            % (q["id"], interaction, VISUAL_PROTOCOL_VERSION,
               ", ".join(VISUAL_INTERACTIONS)))
    scene = q.get("visual")
    scoring = q.get("scoring")
    if not isinstance(scene, dict) or not isinstance(scoring, dict):
        raise ValueError("visual item %s: VISUAL and SCORING must be JSON "
                         "objects" % q["id"])
    unknown = set(scene) - _VISUAL_SCENE_MEMBERS
    if unknown:
        raise ValueError("visual item %s: unknown VISUAL member(s) %s"
                         % (q["id"], ", ".join(sorted(unknown))))
    unknown = set(scoring) - _VISUAL_SCORING_MEMBERS
    if unknown:
        raise ValueError("visual item %s: unknown SCORING member(s) %s"
                         % (q["id"], ", ".join(sorted(unknown))))
    _reject_visual_exec(scene, "VISUAL")
    _reject_visual_exec(scoring, "SCORING")

    kind = scoring.get("kind")
    if kind not in VISUAL_KINDS:
        raise ValueError("visual item %s: unknown SCORING kind %r"
                         % (q["id"], kind))
    if scoring.get("partial_credit") is not False:
        raise ValueError("visual item %s: protocol %d is dichotomous; "
                         "partial_credit must be false"
                         % (q["id"], VISUAL_PROTOCOL_VERSION))
    axes = visual_axes(q)
    if axes is None:
        raise ValueError("visual item %s: scene axes are invalid (SCALAR "
                         "min/max, positive step, at most %d ticks)"
                         % (q["id"], VISUAL_MAX_TICKS))

    actions = scene.get("actions")
    if not isinstance(actions, list) or not actions \
            or any(a not in VISUAL_ACTIONS for a in actions):
        raise ValueError("visual item %s: actions must be a non-empty subset "
                         "of %s" % (q["id"], ", ".join(VISUAL_ACTIONS)))
    accessibility = scene.get("accessibility")
    if not isinstance(accessibility, dict) \
            or not str(accessibility.get("description") or "").strip():
        raise ValueError("visual item %s: accessibility.description is "
                         "required (D-07)" % q["id"])

    # The accepted states and tolerance are validated here (server-side) so a
    # malformed scoring envelope fails before any learner sees the item; they
    # are never emitted into the public contract.
    accepted = scoring.get("accepted")
    if not isinstance(accepted, list) or not accepted:
        raise ValueError("visual item %s: SCORING.accepted must be a "
                         "non-empty list" % q["id"])
    for raw in accepted:
        state = _canonical_accepted_state(q, raw)
        if state is None or not visual_state_in_domain(q, state, axes):
            raise ValueError("visual item %s: an accepted state is invalid "
                             "or out of domain" % q["id"])
    tolerance = scoring.get("tolerance") or {}
    if not isinstance(tolerance, dict):
        raise ValueError("visual item %s: SCORING.tolerance must be an "
                         "object" % q["id"])
    for key, raw in tolerance.items():
        if canonical_scalar(raw) is None or fractions.Fraction(raw) < 0:
            raise ValueError("visual item %s: tolerance %r is not a "
                             "non-negative SCALAR" % (q["id"], key))

    renderer_config = {"actions": list(actions),
                       "accessibility": {"description":
                                         str(accessibility["description"])}}
    if interaction == "plot":
        renderer_config["axes"] = {"x": axes["x"], "y": axes["y"]}
        renderer_config["initial"] = scene.get("initial") or {"points": []}
    else:
        renderer_config["axis"] = axes["axis"]
        renderer_config["initial"] = scene.get("initial") or {
            "points": [], "interval": None}
    return {"version": VISUAL_PROTOCOL_VERSION, "type": "visual",
            "interaction": interaction, "renderer_config": renderer_config,
            "response_schema": _visual_response_schema(kind)}


def visual_observation(q, state, verdict, hint_tier=None):
    """The structured, runtime-bounded observation for one visual response
    (D-06): submitted canonical semantic state, a deterministic
    error/invariant category, the ordered authored invariants that held,
    an opaque authored feedback anchor, and only the hint tier the
    Phase-6 policy already permitted for the session.

    `state` is the canonical state dict from `canonical_visual_response`
    (None for an invalid response); `hint_tier` is the entitlement supplied
    by the caller (the Phase-6 policy transition), never read from any client
    or agent field -- a forged tier cannot raise it (T-06.1-02).
    """
    if isinstance(state, str):
        try:
            state = json.loads(state)
        except (TypeError, ValueError):
            state = None
    if state is not None and not isinstance(state, dict):
        state = None
    error_category = None
    invariants = []
    if state is None:
        error_category = "invalid_response"
    else:
        axes = visual_axes(q)
        if axes is None:
            error_category = "invalid_response"
        else:
            if visual_state_in_domain(q, state, axes):
                invariants.append("in_bounds")
            else:
                error_category = "out_of_domain"
            tolerance = (q.get("scoring") or {}).get("tolerance") or {}
            discrete = not any(fractions.Fraction(
                canonical_scalar(v) or "0") > 0 for v in tolerance.values())
            if state["kind"] == "interval":
                invariants.append("ordered")
            if discrete and error_category is None \
                    and not visual_state_on_grid(q, state, axes):
                error_category = "off_grid"
            elif not discrete and error_category is None:
                invariants.append("continuous")
    anchors = (q.get("scoring") or {}).get("feedback") or {}
    if not isinstance(anchors, dict):
        anchors = {}
    feedback_anchor = anchors.get(error_category or "default")
    return {
        "submitted": state,
        "error_category": error_category,
        "invariants": invariants,
        "feedback_anchor": feedback_anchor,
        "hint_tier": hint_tier,
        "tolerance_policy_version": VISUAL_TOLERANCE_POLICY_VERSION,
    }


def interaction_result(q, response, verdict, observations):
    """The normalized post-submit result envelope for a visual item, consumed
    by the served submit path and any agent adapter. It does not grade:
    `verdict` is exactly what `score_response()` returned, and `observations`
    is the ordered list of runtime-bounded observations built by
    `visual_observation`. No accepted state, tolerance, or reveal content is
    carried here.
    """
    return {
        "version": VISUAL_PROTOCOL_VERSION,
        "type": "visual",
        "response": response,
        "verdict": verdict,
        "observations": observations,
    }


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


def explain_payload(q, reveal=True):
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


# ---- phase 8: model-orchestrated hint and rubric review (08-04) ------------
# D-08..D-14: the runtime, not the surface, sequences adapter -> gate ->
# evidence -> authored fallback. These helpers never accept a caller-supplied
# tier, profile, key, or marker, and the learner-facing payloads they return
# never carry a reason code (D-08) -- the gate reason is evidence-only
# (T-08-32).

def _interaction_fingerprint(value):
    """One stable descriptor fingerprint for a request/response structure
    (D-15): a SHA-256 over the canonical JSON. Raw text never enters an
    event, only this digest."""
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _new_interaction_id():
    """One fresh interaction id: uuid4 hex (plan 08-04, D-12)."""
    import uuid
    return uuid.uuid4().hex


def _last_response_was_wrong(live_responses_for_item):
    """True when the most recent live response event for the current item was
    deterministically scored False. A pending (short) response, a correct
    response, or no response at all is never a genuine wrong response
    (D-10)."""
    if not live_responses_for_item:
        return False
    return live_responses_for_item[-1].get("score") is False


def _hint_item_context(q):
    """The item fields the runtime permits a provider to see for hint
    generation (never the key or the model answer): enough context to target
    the learner's error, nothing that outranks the permitted tier."""
    out = {"id": q.get("id"), "type": q.get("type"), "stem": q.get("stem", ""),
           "difficulty": q.get("difficulty", "")}
    if q.get("type") in ("mc", "multi"):
        out["options"] = dict(q.get("opts") or {})
    return out


def _serializable_manifest(manifest):
    """The tier-gate fact manifest as a JSON-safe structure (sets become
    sorted lists), suitable for an adapter request payload and a stable
    request fingerprint. Facts keep their stable ids and text; nothing is
    added or dropped."""
    if manifest is None:
        return None
    return {
        "tier": manifest.get("tier"),
        "wrong_response": manifest.get("wrong_response"),
        "span": manifest.get("span"),
        "picked_option": manifest.get("picked_option"),
        "facts": manifest.get("facts") or {},
        "allowed_ids": sorted(manifest.get("allowed_ids") or []),
        "protected_ids": sorted(manifest.get("protected_ids") or []),
        "ambiguous_ids": sorted(manifest.get("ambiguous_ids") or []),
        "protected_fragments": manifest.get("protected_fragments") or [],
    }


def _backend_descriptors(adapter_result):
    """(backend_class, profile) for the evidence event: prefer the adapter's
    own provider audit metadata (D-17); when no profile resolved (a disabled
    backend), record the design-target hosted class with an empty profile --
    D-18 names the hosted CLI as the default backend class."""
    provider = adapter_result.get("provider")
    if provider:
        return (provider.get("backend_class") or "hosted",
                provider.get("profile") or "")
    return "hosted", ""


def hint_context(session_data, q):
    """Resolve the Phase 6 teaching record for the current item into the
    context a model hint generation needs (D-03/D-10).

    Returns {"item", "tier", "wrong_response", "picked_option", "mode"} or
    None when no genuine wrong response exists -- nothing to target, so no
    generation may be attempted. `tier` is the Phase 6 permitted tier (the
    highest the learner has unlocked; a grant, never a model choice, D-09).
    A constructed (short) response is pending review, never wrong (T-06-05),
    so it is not a valid hint context.
    """
    state = session_data.get("teaching_state")
    if not isinstance(state, dict):
        return None
    rec = state.get(teaching_key(q))
    if not isinstance(rec, dict):
        return None
    wrong = rec.get("last_genuine_canonical")
    if not wrong:
        return None
    if q.get("type") == "short":
        return None
    tier = rec.get("highest_tier_unlocked", -1)
    picked = None
    if q.get("type") in ("mc", "multi"):
        picked = str(wrong).split(",")[0].strip().upper()
    return {"item": q, "tier": tier, "wrong_response": wrong,
            "picked_option": picked,
            "mode": session_data.get("mode", "")}


def invoke_hint(session_file, retry=False):
    """The ONE orchestration path for an error-specific hint (plan 08-04).

    Sequences: resolve session and current item -> hint_context -> mint or
    reuse the interaction id (at most one generation per id, D-12) ->
    model_adapter.request_from_operation(operation hint) ->
    model_adapter.invoke with surfaces.settings.load_settings -> validate
    the result -> tier_gate.evaluate_candidate on any candidate ->
    learner_payload on pass, or the authored fallback via
    authored_hint(q, tier) on drop/unavailable (D-08/D-11) -> append one
    evidence.model_interaction_event (evidence-only, D-15) -> return the
    typed {"status", "generated", "authored", "interaction_id", "evidence"}
    payload that never carries a reason code (D-08).
    """
    import evidence
    import model
    import model_adapter
    import tier_gate
    from surfaces import settings as _settings

    data = read_session(session_file)
    if data["status"] != "active":
        sys.exit("session is already complete")
    qs = model.load(data["bank"])
    if data["cursor"] >= len(data["items"]):
        data["status"] = "complete"
        write_session(session_file, data)
        sys.exit("session is already complete")
    q = qs[data["items"][data["cursor"]]]

    log = evidence.log_path(os.path.dirname(data["bank"]))
    item_key = evidence.evidence_key(q)
    live_responses = [ev for ev in evidence.live_events(log)
                      if ev.get("event_type") == evidence.RESPONSE_EVENT_TYPE
                      and ev.get("session_id") == data["session_id"]
                      and evidence.evidence_key({
                          "item_id": ev.get("item_id", ""),
                          "id": ev.get("item_ref", "")}) == item_key]

    ctx = hint_context(data, q)
    if ctx is None or not _last_response_was_wrong(live_responses):
        return {"status": "unavailable", "generated": None, "authored": None,
                "interaction_id": None,
                "evidence": {"status": "no_genuine_wrong_response"}}
    tier = ctx["tier"]
    if tier < 0:
        # No tier has been permitted for this item (a diagnostic/exam defer
        # or an untouched record): nothing may be generated or shown.
        return {"status": "unavailable", "generated": None, "authored": None,
                "interaction_id": None,
                "evidence": {"status": "no_permitted_tier"}}

    # At most one generation per interaction id (D-12): a repeated command
    # without retry regenerates nothing and reports the existing id.
    prior = [ev for ev in evidence.model_interactions(log, data["session_id"])
             if ev.get("operation") == "hint"
             and ev.get("item_ref") == q.get("id")]
    if prior and not retry:
        existing = prior[-1]
        authored = None
        ah = authored_hint(q, tier, ctx["wrong_response"])
        if ah.get("available"):
            authored = ah
        return {"status": "unavailable", "generated": None, "authored": authored,
                "interaction_id": existing["interaction_id"],
                "evidence": {"accepted": False, "status": "already_recorded",
                             "event_id": existing["event_id"]}}

    interaction_id = _new_interaction_id()
    parent = prior[-1]["interaction_id"] if (retry and prior) else None

    settings_data = _settings.load_settings(os.path.dirname(data["bank"]) or ".")
    manifest = _serializable_manifest(
        tier_gate.build_fact_manifest(q, tier, ctx["wrong_response"],
                                      ctx["picked_option"]))
    request = model_adapter.request_from_operation(
        "hint", interaction_id, "",
        item_context=_hint_item_context(q),
        learner_response=ctx["wrong_response"],
        permitted_tier=tier,
        fact_manifest=manifest)
    result = model_adapter.invoke(request, settings_data)
    candidate = result.get("candidate")

    outcome = "unavailable"
    gate_reason = None
    rendered = None
    if candidate is not None:
        gate = tier_gate.evaluate_candidate(q, tier, ctx["wrong_response"],
                                            candidate)
        if gate["outcome"] == "pass":
            rendered = tier_gate.render_hint(gate["plan"], manifest)
            outcome = "pass"
        else:
            outcome = "drop"
            gate_reason = gate["reason"]

    authored = None
    ah = authored_hint(q, tier, ctx["wrong_response"])
    if ah.get("available"):
        authored = ah

    backend_class, profile = _backend_descriptors(result)
    ev = evidence.model_interaction_event(
        data["session_id"], os.path.basename(data["bank"]), q.get("id", ""),
        "hint", interaction_id, outcome, gate_reason, tier, backend_class,
        profile, request_fingerprint=_interaction_fingerprint(request),
        response_fingerprint=_interaction_fingerprint(candidate)
        if candidate is not None else None,
        elapsed_ms=result.get("elapsed_ms"),
        output_bytes=len(json.dumps(candidate, ensure_ascii=False))
        if candidate is not None else 0,
        pass_payload=rendered if outcome == "pass" else None,
        parent_interaction_id=parent)
    write_result = evidence.append_event(log, ev)

    generated = None
    if outcome == "pass":
        generated = tier_gate.learner_payload("pass", rendered).get("generated")
    return {"status": outcome, "generated": generated, "authored": authored,
            "interaction_id": interaction_id, "evidence": write_result}
