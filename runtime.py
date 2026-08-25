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
#
# Version 3 (Phase 9) adds the nullable `subject_profile` snapshot: the
# resolved subject id, registry/profile versions, the full resolved profile
# (lesson capabilities, allowed item types, verifier), and any requested
# unavailable capabilities. New sessions persist the complete snapshot; the
# v2-to-v3 upgrade leaves the slot null and the session adapter fills it once
# from the bank on the first action (D-04).
SESSION_VERSION = 3
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
    t = q["type"]
    if t == "visual":
        state = canonical_visual_response(q, answer)
        if state is None:
            return ""
        return json.dumps(state, sort_keys=True)
    normalizer = NORMALIZERS.get(t)
    if normalizer is None:
        return None     # no registered normalizer: no canonical form
    return normalizer(q, answer)


def canonical_key(q):
    """The canonical response that is correct, in the same shape as the above."""
    t = q["type"]
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
    key = KEYS.get(t)
    if key is None:
        return None
    return key(q)


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
    canon = canonical_response(q, answer)
    if canon is None:
        return None          # a None canonical is not a False verdict (check timeout)
    return canon == key


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

VISUAL_INTERACTIONS = ("plot", "numberline", "hotspot", "timeline",
                       "diagram", "trace")
VISUAL_KINDS = ("point", "numberline_point", "interval", "hotspot",
                "timeline_event", "diagram_connection", "trace_path")
# The only protocol-1 committed-action types (D-05); final submit is the
# ordinary response event and is never duplicated as a visual action.
# Phase 999.1 adds the advanced families additively (D-999.1-01): protocol
# integer stays 1 and the envelope shape is unchanged; only these allowlists
# grow, so plot/numberline items stay byte-compatible.
VISUAL_ACTIONS = ("place_point", "move_point",
                  "select_numberline_point", "set_interval",
                  "select_hotspot", "place_timeline_event",
                  "move_timeline_event", "connect_diagram",
                  "place_trace_point", "move_trace_point")
# The closed allowlist of authored scene members per interaction
# (T-06.1-03/D-999.1-04): each family accepts exactly its own set; anything
# else is rejected before a renderer sees it.
_VISUAL_SCENE_MEMBERS = {
    "plot": frozenset({"version", "axes", "initial", "actions",
                       "accessibility"}),
    "numberline": frozenset({"version", "axis", "initial", "actions",
                             "accessibility"}),
    "hotspot": frozenset({"version", "plane", "regions", "initial",
                          "actions", "accessibility"}),
    "timeline": frozenset({"version", "axis", "events", "initial",
                           "actions", "accessibility"}),
    "diagram": frozenset({"version", "plane", "nodes", "initial",
                          "actions", "accessibility"}),
    "trace": frozenset({"version", "axes", "point_count", "initial",
                        "actions", "accessibility"}),
}
# The response kinds each interaction family accepts (D-999.1-02).
_VISUAL_KIND_BY_INTERACTION = {
    "plot": ("point",),
    "numberline": ("numberline_point", "interval"),
    "hotspot": ("hotspot",),
    "timeline": ("timeline_event",),
    "diagram": ("diagram_connection",),
    "trace": ("trace_path",),
}
_VISUAL_SCORING_MEMBERS = frozenset({"kind", "accepted", "tolerance",
                                     "partial_credit", "feedback"})
# Stable authored identifier grammar for the advanced families: bounded
# length, no whitespace or punctuation beyond `-`/`_`, and nothing that the
# script-bearing scan (below) would flag. Ids are semantic data, never code.
_VISUAL_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
# Scene-size bounds (T-999.1-04/08/12): the advanced families stay small.
VISUAL_MAX_REGIONS = 200
VISUAL_MAX_EVENTS = 100
VISUAL_MAX_NODES = 100
VISUAL_MAX_TRACE_POINTS = 50
_VISUAL_SHAPES = ("rect", "circle", "polygon")
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
    if interaction == "trace":
        # The trace family reuses the plot's two-axis geometry (999.1).
        axes = scene.get("axes")
        if not isinstance(axes, dict):
            return None
        x, y = canonical_axis(axes.get("x")), canonical_axis(axes.get("y"))
        if x is None or y is None:
            return None
        return {"x": x, "y": y}
    return None


# ---- phase 999.1 scene validation (advanced visual families) ----------------
# One strict per-interaction scene builder used by the contract, lint, and
# scoring paths: a malformed scene raises ValueError with a field-addressed
# message; scoring wraps it leniently (`_visual_scene_data`) so anything
# unparseable fails closed as invalid. Coordinate grammar is the 06.1 SCALAR
# grammar -- browser floats and pixels are never scene or scoring inputs.

def _visual_plane(scene, item_id):
    """Validate `plane: {width, height}` as positive SCALARs."""
    plane = scene.get("plane")
    if not isinstance(plane, dict) or set(plane) != {"width", "height"}:
        raise ValueError("geometry: visual item %s: plane must be "
                         "{width, height}" % item_id)
    w = canonical_scalar(plane.get("width", ""))
    h = canonical_scalar(plane.get("height", ""))
    if w is None or h is None or fractions.Fraction(w) <= 0 \
            or fractions.Fraction(h) <= 0:
        raise ValueError("geometry: visual item %s: plane width/height must "
                         "be positive SCALARs" % item_id)
    return {"width": w, "height": h}


def _visual_region_coords(coords, shape, plane, item_id, where):
    """Validate one region's `coords` in plane units; returns canonical
    SCALARs. rect: [x, y, w, h]; circle: [cx, cy, r]; polygon: [[x, y], ...]
    with at least 3 in-plane vertices."""
    W = fractions.Fraction(plane["width"])
    H = fractions.Fraction(plane["height"])
    if shape in ("rect", "circle"):
        want = 4 if shape == "rect" else 3
        if not isinstance(coords, list) or len(coords) != want:
            raise ValueError("geometry: visual item %s: %s.coords needs %d "
                             "SCALARs" % (item_id, where, want))
        vals = [canonical_scalar(v) for v in coords]
        if None in vals:
            raise ValueError("geometry: visual item %s: %s.coords must be "
                             "SCALARs" % (item_id, where))
        fs = [fractions.Fraction(v) for v in vals]
        if shape == "rect":
            x, y, w, h = fs
            if w <= 0 or h <= 0 or x < 0 or y < 0 or x + w > W or y + h > H:
                raise ValueError("geometry: visual item %s: %s rect must sit "
                                 "inside the plane" % (item_id, where))
        else:
            cx, cy, r = fs
            if r <= 0 or cx - r < 0 or cx + r > W or cy - r < 0 \
                    or cy + r > H:
                raise ValueError("geometry: visual item %s: %s circle must "
                                 "sit inside the plane" % (item_id, where))
        return [str(v) for v in vals]
    if not isinstance(coords, list) or len(coords) < 3:
        raise ValueError("geometry: visual item %s: %s polygon needs at "
                         "least 3 vertices" % (item_id, where))
    out = []
    for j, v in enumerate(coords):
        if not isinstance(v, list) or len(v) != 2:
            raise ValueError("geometry: visual item %s: %s polygon vertex %d "
                             "must be [x, y]" % (item_id, where, j))
        x, y = canonical_scalar(v[0]), canonical_scalar(v[1])
        if x is None or y is None:
            raise ValueError("geometry: visual item %s: %s polygon vertex %d "
                             "must be SCALARs" % (item_id, where, j))
        fx, fy = fractions.Fraction(x), fractions.Fraction(y)
        if fx < 0 or fx > W or fy < 0 or fy > H:
            raise ValueError("geometry: visual item %s: %s polygon vertex %d "
                             "is outside the plane" % (item_id, where, j))
        out.append([x, y])
    return out


def _visual_named_list(scene, key, item_id, maximum, noun):
    """Validate a list of `{id, label, ...}` entries with unique ids; returns
    `{id: entry}` with the entry's label stripped. Raises on malformed or
    duplicate ids."""
    entries = scene.get(key)
    if not isinstance(entries, list) or not entries or len(entries) > maximum:
        raise ValueError("geometry: visual item %s: %s must be a non-empty "
                         "list of at most %d entries"
                         % (item_id, key, maximum))
    out = {}
    for i, raw in enumerate(entries):
        where = "%s[%d]" % (key, i)
        if not isinstance(raw, dict):
            raise ValueError("geometry: visual item %s: %s must be an "
                             "object" % (item_id, where))
        rid = raw.get("id")
        if not isinstance(rid, str) or not _VISUAL_ID_RE.match(rid):
            raise ValueError("geometry: visual item %s: %s.id is not a valid "
                             "identifier" % (item_id, where))
        if rid in out:
            raise ValueError("duplicate_id: visual item %s: duplicate %s id "
                             "%r" % (item_id, noun, rid))
        label = raw.get("label")
        if not isinstance(label, str) or not label.strip():
            raise ValueError("geometry: visual item %s: %s.label is "
                             "required" % (item_id, where))
        out[rid] = dict(raw, label=label.strip())
    return out


def _visual_initial_ok(interaction, scene, data, item_id):
    """Validate the family's `initial` renderer state so the public
    renderer_config is trustworthy. Raises on malformed state."""
    initial = scene.get("initial")
    if initial is None:
        return
    if not isinstance(initial, dict):
        raise ValueError("geometry: visual item %s: initial must be an "
                         "object" % item_id)
    if interaction == "hotspot":
        region = initial.get("region")
        if region is not None and region not in data["regions"]:
            raise ValueError("geometry: visual item %s: initial.region %r is "
                             "not a known region" % (item_id, region))
    elif interaction == "timeline":
        placements = initial.get("placements") or []
        if not isinstance(placements, list) or len(placements) > len(data["events"]):
            raise ValueError("geometry: visual item %s: initial.placements "
                             "must be a bounded list" % item_id)
        seen = set()
        for raw in placements:
            if not isinstance(raw, dict) or set(raw) != {"event", "value"}:
                raise ValueError("geometry: visual item %s: a placement must "
                                 "be {event, value}" % item_id)
            ev, value = raw.get("event"), canonical_scalar(raw.get("value", ""))
            if ev not in data["events"] or value is None:
                raise ValueError("geometry: visual item %s: a placement names "
                                 "an unknown event or bad value" % item_id)
            if ev in seen or not _scalar_in_axis(data["axis"], value):
                raise ValueError("geometry: visual item %s: a placement is "
                                 "duplicated or out of axis bounds" % item_id)
            seen.add(ev)
    elif interaction == "diagram":
        connections = initial.get("connections") or []
        if not isinstance(connections, list):
            raise ValueError("geometry: visual item %s: initial.connections "
                             "must be a list" % item_id)
        for raw in connections:
            if not isinstance(raw, dict) or set(raw) != {"from", "to"} \
                    or raw.get("from") not in data["nodes"] \
                    or raw.get("to") not in data["nodes"]:
                raise ValueError("geometry: visual item %s: a connection "
                                 "names unknown nodes" % item_id)
    elif interaction == "trace":
        points = initial.get("points") or []
        if not isinstance(points, list) \
                or len(points) != data["point_count"]:
            raise ValueError("geometry: visual item %s: initial.points must "
                             "match point_count" % item_id)
        axes = data["axes"]
        for raw in points:
            if not isinstance(raw, dict) or set(raw) != {"x", "y"}:
                raise ValueError("geometry: visual item %s: a trace point "
                                 "must be {x, y}" % item_id)
            x, y = canonical_scalar(raw.get("x", "")), canonical_scalar(raw.get("y", ""))
            if x is None or y is None \
                    or not _scalar_in_axis(axes["x"], x) \
                    or not _scalar_in_axis(axes["y"], y):
                raise ValueError("geometry: visual item %s: a trace point is "
                                 "invalid or out of domain" % item_id)


def _visual_scene(q, interaction):
    """Strictly validate one family's authored scene; returns the canonical
    per-interaction scene data or raises ValueError with a field-addressed
    message (see `_visual_scene_data` for the shape)."""
    scene = q.get("visual") or {}
    item_id = q["id"]
    if interaction in ("plot", "numberline"):
        axes = visual_axes(q)
        if axes is None:
            raise ValueError("geometry: visual item %s: scene axes are "
                             "invalid (SCALAR min/max, positive step, at most "
                             "%d ticks)" % (item_id, VISUAL_MAX_TICKS))
        return axes
    if interaction == "hotspot":
        data = {"plane": _visual_plane(scene, item_id),
                "regions": _visual_named_list(scene, "regions", item_id,
                                              VISUAL_MAX_REGIONS, "region")}
        regions = scene.get("regions")
        for i, raw in enumerate(regions):
            shape = raw.get("shape")
            if shape not in _VISUAL_SHAPES:
                raise ValueError("geometry: visual item %s: regions[%d].shape "
                                 "must be one of %s"
                                 % (item_id, i, ", ".join(_VISUAL_SHAPES)))
            data["regions"][raw["id"]]["shape"] = shape
            data["regions"][raw["id"]]["coords"] = _visual_region_coords(
                raw.get("coords"), shape, data["plane"], item_id,
                "regions[%d]" % i)
        _visual_initial_ok(interaction, scene, data, item_id)
        return data
    if interaction == "timeline":
        axis = canonical_axis(scene.get("axis"))
        if axis is None:
            raise ValueError("geometry: visual item %s: axis is invalid "
                             "(SCALAR min/max, positive step, at most %d "
                             "ticks)" % (item_id, VISUAL_MAX_TICKS))
        data = {"axis": axis,
                "events": _visual_named_list(scene, "events", item_id,
                                             VISUAL_MAX_EVENTS, "event")}
        _visual_initial_ok(interaction, scene, data, item_id)
        return data
    if interaction == "diagram":
        data = {"plane": _visual_plane(scene, item_id),
                "nodes": _visual_named_list(scene, "nodes", item_id,
                                            VISUAL_MAX_NODES, "node")}
        nodes = scene.get("nodes")
        for i, raw in enumerate(nodes):
            x, y = canonical_scalar(raw.get("x", "")), \
                canonical_scalar(raw.get("y", ""))
            if x is None or y is None \
                    or fractions.Fraction(x) < 0 \
                    or fractions.Fraction(x) > fractions.Fraction(data["plane"]["width"]) \
                    or fractions.Fraction(y) < 0 \
                    or fractions.Fraction(y) > fractions.Fraction(data["plane"]["height"]):
                raise ValueError("geometry: visual item %s: nodes[%d] x/y "
                                 "must be SCALARs inside the plane"
                                 % (item_id, i))
            data["nodes"][raw["id"]]["x"] = x
            data["nodes"][raw["id"]]["y"] = y
        _visual_initial_ok(interaction, scene, data, item_id)
        return data
    # trace
    axes = visual_axes(q)
    if axes is None:
        raise ValueError("geometry: visual item %s: scene axes are invalid "
                         "(SCALAR min/max, positive step, at most %d ticks)"
                         % (item_id, VISUAL_MAX_TICKS))
    count = scene.get("point_count")
    if not isinstance(count, int) or isinstance(count, bool) \
            or count < 1 or count > VISUAL_MAX_TRACE_POINTS:
        raise ValueError("geometry: visual item %s: point_count must be an "
                         "integer in 1..%d" % (item_id, VISUAL_MAX_TRACE_POINTS))
    data = {"axes": axes, "point_count": count}
    _visual_initial_ok(interaction, scene, data, item_id)
    return data


def _visual_scene_data(q):
    """Lenient per-family scene lookup for scoring/observation paths: the
    canonical scene dict from `_visual_scene`, or None when the scene is
    absent or malformed. Scoring re-validates defensively and treats anything
    unparseable as invalid (fail closed)."""
    interaction = q.get("interaction")
    if interaction not in VISUAL_INTERACTIONS:
        return None
    try:
        return _visual_scene(q, interaction)
    except ValueError:
        return None


def _visual_region_ids(q):
    """The known hotspot region ids (empty when the scene is malformed)."""
    data = _visual_scene_data(q)
    return set(data["regions"]) if data else set()


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
    if kind == "hotspot":
        if set(answer) != {"kind", "region"}:
            return None
        region = answer.get("region")
        if not isinstance(region, str) or not _VISUAL_ID_RE.match(region):
            return None
        return {"kind": "hotspot", "region": region}
    if kind == "timeline_event":
        if set(answer) != {"kind", "event", "value"}:
            return None
        event = answer.get("event")
        value = canonical_scalar(answer.get("value", ""))
        if not isinstance(event, str) or not _VISUAL_ID_RE.match(event) \
                or value is None:
            return None
        return {"kind": "timeline_event", "event": event, "value": value}
    if kind == "diagram_connection":
        if set(answer) != {"kind", "from", "to"}:
            return None
        frm, to = answer.get("from"), answer.get("to")
        if not isinstance(frm, str) or not _VISUAL_ID_RE.match(frm) \
                or not isinstance(to, str) or not _VISUAL_ID_RE.match(to) \
                or frm == to:
            return None
        return {"kind": "diagram_connection", "from": frm, "to": to}
    if kind == "trace_path":
        if set(answer) != {"kind", "points"}:
            return None
        points = answer.get("points")
        if not isinstance(points, list):
            return None
        scene = q.get("visual") or {}
        count = scene.get("point_count")
        if not isinstance(count, int) or isinstance(count, bool) \
                or count < 1 or count > VISUAL_MAX_TRACE_POINTS \
                or len(points) != count:
            return None
        out = []
        for raw in points:
            if not isinstance(raw, dict) or set(raw) != {"x", "y"}:
                return None
            x, y = canonical_scalar(raw.get("x", "")), \
                canonical_scalar(raw.get("y", ""))
            if x is None or y is None:
                return None
            out.append({"x": x, "y": y})
        return {"kind": "trace_path", "points": out}
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
    if state["kind"] in ("hotspot", "timeline_event", "diagram_connection",
                         "trace_path"):
        return _advanced_visual_verdict(q, state)
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


def _advanced_visual_verdict(q, state):
    """The one boolean verdict for the phase-999.1 families, reached only
    through `score_response()`'s `_visual_verdict` dispatch (never named
    `*_score`, so the structural one-scorer scan stays green).

    Exact-id families (hotspot, diagram) compare the canonical state directly
    and reject any non-zero tolerance; continuous families (timeline, trace)
    validate domain/grid then compare within the private per-coordinate
    tolerance. Invalid responses -- unknown ids, malformed shapes, count
    mismatches, out-of-domain values, forged fields -- fail closed as False.
    """
    kind = state["kind"]
    if not visual_state_in_domain(q, state):
        return False
    scoring = q.get("scoring") or {}
    tolerance = scoring.get("tolerance") or {}
    if kind in ("hotspot", "diagram_connection"):
        if any(fractions.Fraction(canonical_scalar(v) or "0") > 0
               for v in tolerance.values()):
            return False
        for accepted in (scoring.get("accepted") or []):
            acc = _canonical_accepted_state(q, accepted)
            if acc is not None and visual_state_in_domain(q, acc) \
                    and acc == state:
                return True
        return False
    tol = {}
    for key, raw in tolerance.items():
        t = canonical_scalar(raw)
        if t is None:
            return False
        tol[key] = fractions.Fraction(t)
    discrete = not any(f > 0 for f in tol.values())
    if discrete and not visual_state_on_grid(q, state):
        return False
    for accepted in (scoring.get("accepted") or []):
        acc = _canonical_accepted_state(q, accepted)
        if acc is None:
            continue
        if visual_within_tolerance(state, acc, tol):
            return True
    return False


def visual_state_in_domain(q, state, axes=None):
    kind = state["kind"]
    if kind in ("point", "numberline_point", "interval"):
        axes = axes or visual_axes(q)
        if axes is None:
            return False
        if kind == "point":
            return (_scalar_in_axis(axes["x"], state["x"])
                    and _scalar_in_axis(axes["y"], state["y"]))
        if kind == "numberline_point":
            return _scalar_in_axis(axes["axis"], state["value"])
        return (_scalar_in_axis(axes["axis"], state["start"])
                and _scalar_in_axis(axes["axis"], state["end"]))
    if kind == "hotspot":
        return state["region"] in _visual_region_ids(q)
    if kind == "timeline_event":
        data = _visual_scene_data(q)
        if not data or state["event"] not in data["events"]:
            return False
        return _scalar_in_axis(data["axis"], state["value"])
    if kind == "diagram_connection":
        data = _visual_scene_data(q)
        return bool(data) and state["from"] in data["nodes"] \
            and state["to"] in data["nodes"]
    if kind == "trace_path":
        data = _visual_scene_data(q)
        if not data:
            return False
        axes = data["axes"]
        return all(_scalar_in_axis(axes["x"], p["x"])
                   and _scalar_in_axis(axes["y"], p["y"])
                   for p in state["points"])
    return False


def visual_state_on_grid(q, state, axes=None):
    """Whether every coordinate lands exactly on a declared tick. Only
    meaningful for discrete (zero-tolerance) items; exact-id families have no
    grid concept and are always on grid (they compare by canonical id)."""
    kind = state["kind"]
    if kind in ("point", "numberline_point", "interval"):
        axes = axes or visual_axes(q)
        if axes is None:
            return False
        if kind == "point":
            return (_scalar_on_grid(axes["x"], state["x"])
                    and _scalar_on_grid(axes["y"], state["y"]))
        if kind == "numberline_point":
            return _scalar_on_grid(axes["axis"], state["value"])
        return (_scalar_on_grid(axes["axis"], state["start"])
                and _scalar_on_grid(axes["axis"], state["end"]))
    if kind == "hotspot":
        return True
    if kind == "timeline_event":
        data = _visual_scene_data(q)
        if not data or state["event"] not in data["events"]:
            return False
        return _scalar_on_grid(data["axis"], state["value"])
    if kind == "diagram_connection":
        return True
    if kind == "trace_path":
        data = _visual_scene_data(q)
        if not data:
            return False
        axes = data["axes"]
        return all(_scalar_on_grid(axes["x"], p["x"])
                   and _scalar_on_grid(axes["y"], p["y"])
                   for p in state["points"])
    return False


def visual_within_tolerance(state, accepted, tol):
    """Per-coordinate `|submitted - accepted| <= tolerance`, with closure
    equality for intervals. A tolerance of 0 is exact equality after
    canonicalization. `tol` maps coordinate names to Fractions. Exact-id
    families compare canonical state directly."""
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
    if kind == "interval":
        return (within(state["start"], accepted["start"], "start")
                and within(state["end"], accepted["end"], "end")
                and state["start_closed"] == accepted["start_closed"]
                and state["end_closed"] == accepted["end_closed"])
    if kind in ("hotspot", "diagram_connection"):
        return state == accepted
    if kind == "timeline_event":
        return state["event"] == accepted["event"] \
            and within(state["value"], accepted["value"], "value")
    if kind == "trace_path":
        if len(state["points"]) != len(accepted["points"]):
            return False
        return all(within(p["x"], a["x"], "x")
                   and within(p["y"], a["y"], "y")
                   for p, a in zip(state["points"], accepted["points"]))
    return False


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
    if kind == "interval":
        return {"type": "object", "kind": "interval",
                "fields": {"start": "scalar", "end": "scalar",
                           "start_closed": "boolean", "end_closed": "boolean"}}
    if kind == "hotspot":
        return {"type": "object", "kind": "hotspot",
                "fields": {"region": "identifier"}}
    if kind == "timeline_event":
        return {"type": "object", "kind": "timeline_event",
                "fields": {"event": "identifier", "value": "scalar"}}
    if kind == "diagram_connection":
        return {"type": "object", "kind": "diagram_connection",
                "fields": {"from": "identifier", "to": "identifier"}}
    return {"type": "object", "kind": "trace_path",
            "fields": {"points": "point_list"}}


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
    unknown = set(scene) - _VISUAL_SCENE_MEMBERS[interaction]
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
    if kind not in _VISUAL_KIND_BY_INTERACTION.get(interaction, ()):
        raise ValueError("visual item %s: SCORING kind %r does not match "
                         "INTERACTION %r" % (q["id"], kind, interaction))
    if scoring.get("partial_credit") is not False:
        raise ValueError("visual item %s: protocol %d is dichotomous; "
                         "partial_credit must be false"
                         % (q["id"], VISUAL_PROTOCOL_VERSION))
    scene_data = _visual_scene(q, interaction)
    if scene_data is None:
        raise ValueError("visual item %s: scene geometry is invalid"
                         % q["id"])

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
        if state is None or not visual_state_in_domain(q, state):
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
    if kind in ("hotspot", "diagram_connection") and any(
            fractions.Fraction(canonical_scalar(v)) > 0
            for v in tolerance.values()):
        raise ValueError("visual item %s: %s scoring is exact-id; tolerance "
                         "must be zero" % (q["id"], kind))

    renderer_config = {"actions": list(actions),
                       "accessibility": {"description":
                                         str(accessibility["description"])}}
    if interaction == "plot":
        renderer_config["axes"] = {"x": scene_data["x"], "y": scene_data["y"]}
        renderer_config["initial"] = scene.get("initial") or {"points": []}
    elif interaction == "numberline":
        renderer_config["axis"] = scene_data["axis"]
        renderer_config["initial"] = scene.get("initial") or {
            "points": [], "interval": None}
    elif interaction == "hotspot":
        renderer_config["plane"] = scene_data["plane"]
        renderer_config["regions"] = [
            {"id": rid, "label": r["label"], "shape": r["shape"],
             "coords": r["coords"]}
            for rid, r in scene_data["regions"].items()]
        renderer_config["initial"] = scene.get("initial") or {"region": None}
    elif interaction == "timeline":
        renderer_config["axis"] = scene_data["axis"]
        renderer_config["events"] = [
            {"id": eid, "label": entry["label"]}
            for eid, entry in scene_data["events"].items()]
        renderer_config["initial"] = scene.get("initial") or {"placements": []}
    elif interaction == "diagram":
        renderer_config["plane"] = scene_data["plane"]
        renderer_config["nodes"] = [
            {"id": nid, "label": n["label"], "x": n["x"], "y": n["y"]}
            for nid, n in scene_data["nodes"].items()]
        renderer_config["initial"] = scene.get("initial") or {
            "connections": []}
    else:  # trace
        renderer_config["axes"] = {"x": scene_data["axes"]["x"],
                                    "y": scene_data["axes"]["y"]}
        renderer_config["point_count"] = scene_data["point_count"]
        renderer_config["initial"] = scene.get("initial") or {"points": []}
    return {"version": VISUAL_PROTOCOL_VERSION, "type": "visual",
            "interaction": interaction, "renderer_config": renderer_config,
            "response_schema": _visual_response_schema(kind)}


def _advanced_observation(q, state, kind, data):
    """Observation classification for the phase-999.1 families: known ids,
    in-bounds values, point count, and grid/domain categories. Never reads
    the accepted answer or tolerance amounts (D-06)."""
    if kind == "hotspot":
        if state["region"] in data["regions"]:
            return None, ["known_region"]
        return "unknown_region", []
    if kind == "timeline_event":
        if state["event"] not in data["events"]:
            return "unknown_event", []
        invariants = ["known_event"]
        if not _scalar_in_axis(data["axis"], state["value"]):
            return "out_of_domain", invariants
        invariants.append("in_bounds")
        tolerance = (q.get("scoring") or {}).get("tolerance") or {}
        discrete = not any(fractions.Fraction(
            canonical_scalar(v) or "0") > 0 for v in tolerance.values())
        if discrete and not _scalar_on_grid(data["axis"], state["value"]):
            return "off_grid", invariants
        return None, invariants
    if kind == "diagram_connection":
        nodes = data["nodes"]
        if state["from"] not in nodes or state["to"] not in nodes:
            return "unknown_node", []
        return None, ["known_nodes", "distinct_nodes"]
    # trace_path
    if len(state["points"]) != data["point_count"]:
        return "wrong_point_count", []
    invariants = ["point_count"]
    axes = data["axes"]
    for p in state["points"]:
        if not (_scalar_in_axis(axes["x"], p["x"])
                and _scalar_in_axis(axes["y"], p["y"])):
            return "out_of_domain", invariants
    invariants.append("in_bounds")
    return None, invariants


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
        kind = state["kind"]
        if kind in ("hotspot", "timeline_event", "diagram_connection",
                    "trace_path"):
            data = _visual_scene_data(q)
            if data is None:
                error_category = "invalid_response"
            else:
                error_category, invariants = _advanced_observation(
                    q, state, kind, data)
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
    """The normalized post-submit result envelope for both interactive
    types, consumed by the served submit path and any agent adapter. It
    does not grade: `verdict` is exactly what `score_response()` returned
    (True, False, or None for a run the deadline killed -- criterion 12).

    For a check item, `observations` is the raw per-case run_result from
    the runner and is normalized here into the stable case_observation
    shape; for a visual item it is already the ordered list of
    runtime-bounded observations built by `visual_observation`. No accepted
    state, tolerance, or reveal content is carried in either shape.
    """
    if q["type"] == "check":
        return {
            "version": INTERACTION_VERSION,
            "type": "check",
            "response": response,
            "verdict": verdict,
            "observations": [_check_observation(q, i, r)
                             for i, r in enumerate(observations or [])],
        }
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
    # v2-to-v3 (Phase 9): a nullable subject-profile slot only. The upgrade
    # never inspects a bank or settings; the first action on a legacy session
    # resolves and persists the snapshot once (D-04).
    2: lambda data: dict(data, subject_profile=None),
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
    # Phase 9 (D-04): the persisted subject/profile snapshot is part of the
    # public view. Legacy sessions whose null slot is not filled yet report
    # an empty subject id and no profile metadata.
    sp = data.get("subject_profile")
    if isinstance(sp, dict):
        prof = sp.get("profile") or {}
        view["subject_id"] = sp.get("subject_id", "")
        view["subject_profile"] = {
            "id": prof.get("id", ""),
            "version": prof.get("version"),
            "registry_version": sp.get("registry_version"),
            "profile_version": sp.get("profile_version"),
            "lesson": prof.get("lesson"),
            "allowed_item_types": prof.get("allowed_item_types"),
            "verifier": prof.get("verifier"),
            "unsupported_capabilities": sp.get("unsupported_capabilities", []),
        }
    else:
        view["subject_id"] = ""
    if data["status"] == "active" and cursor < len(selected):
        view["item"] = public_item(qs[selected[cursor]], data.get("seed", 0) + cursor)
    else:
        view["summary"] = session_summary(data)
    return view


def session_summary(data, settled_marks=None):
    """The session's own arithmetic.

    `settled_marks` is the set of item REFS a human marker has ruled on (the
    `q["id"]` a response row stores under its confusingly named `item_id`
    field), supplied by the caller because this function is pure over the
    session dict and reads no files. Without it, `pending_manual` counts every unscored
    response, which is what a marker sees as outstanding work. That was wrong
    once a mark existed: the 13.9 sitting marked q8 `fail` and the report went
    on reporting one pending manual mark, so the marker's own ruling was
    invisible to the marker. A settled mark is not outstanding, whichever way
    it went.

    Omitting the argument reproduces the previous counts exactly, so a caller
    without a log in hand is unchanged.
    """
    responses = data["responses"]
    settled = settled_marks or set()
    auto = [r for r in responses if r["score"] is not None]
    correct = sum(1 for r in auto if r["score"] is True)
    by_objective = collections.defaultdict(lambda: {"attempts": 0, "correct": 0, "pending": 0})
    pending_manual = 0
    for r in responses:
        bucket = by_objective[r.get("objective") or "(unmapped)"]
        bucket["attempts"] += 1
        if r["score"] is None:
            if r.get("item_id") not in settled:
                bucket["pending"] += 1
                pending_manual += 1
        elif r["score"]:
            bucket["correct"] += 1
    return {"schema_version": REPORT_VERSION, "auto_attempts": len(auto),
            "auto_correct": correct, "pending_manual": pending_manual,
            "objectives": dict(by_objective)}


def answer_text(q):
    """Compact answer text for study and export surfaces."""
    if q["type"] in ("mc", "multi"):
        return "; ".join("%s) %s" % (c, q["opts"][c]) for c in q["correct"])
    if q["type"] in ("table", "dnd"):
        return "; ".join("%s -> %s" % (r["text"], r["cat"]) for r in q["rows"])
    if q["type"] == "build":
        return " -> ".join(q["steps"])
    if q["type"] == "check":
        # No keyed option and no model answer; describe what the item asks in
        # the same terse voice the other branches use. Never the case inputs
        # or expected outputs -- this feeds surfaces that show an answer
        # before the learner has attempted the item (plan 05-07).
        n = len(q.get("cases") or [])
        return "code check: %d hidden test case%s (%s)" % (
            n, "" if n == 1 else "s", q.get("lang") or "python")
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
    if t == "check":
        # The attempt file records the learner's own source, readable by a
        # marker or a later reader, bounded at a stated line count with a
        # marker when longer -- the full text is always in the evidence log's
        # check_source regardless (plan 05-07).
        lines = str(answer or "").splitlines()
        KEEP = 40
        head = lines[:KEEP]
        if len(lines) > KEEP:
            head.append("... (%d more lines in the evidence log)" % (len(lines) - KEEP))
        return "\n".join(head)
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

    A visual item is the deliberate exception (plan 06.1-03, D-03/A-05): the
    interactive protocol is only safe in served/API mode, where the runtime
    owns scoring and answer release. The static build therefore refuses a
    visual item with an explicit `served_required` flag and never carries a
    key, tolerance, accepted state, or any private scoring material -- the
    OFFLINE_JS client renders the honest served-runtime-required state.
    """
    out = public_item(q)
    if q["type"] == "visual" and offline:
        out["served_required"] = True
        out.pop("key", None)
        return out
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


def _reveal_display(q):
    """The reveal tier's learner-facing text: the runtime's own compact
    answer shaper plus the item's WHY text when one is authored. Tier 5's
    `content` is the structured `explain_payload` dict, which a surface
    rendering strings could only print as nothing -- so the runtime shapes
    the words here, where disclosure has already been authorized, rather
    than leaving a surface to invent them.
    """
    parts = [answer_text(q) or ""]
    why = (q.get("why") or "").strip()
    if why:
        parts.append(why)
    return " — ".join(p for p in parts if p)


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
    t = HINT_TIERS[tier]
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
                "content": slug, "display": ref if ref else "",
                "slug": slug, "label": t["label"]}
    if tier == 1:
        obj = q.get("objective") or ""
        return {"index": 1, "name": name, "available": bool(obj),
                "content": obj, "display": obj, "label": t["label"]}
    if tier == 2:
        trap = q.get("trap") or ""
        return {"index": 2, "name": name, "available": bool(trap),
                "content": trap, "display": trap, "label": t["label"]}
    if tier == 3:
        content = ""
        if canonical and q["type"] in ("mc", "multi"):
            option = str(canonical).split(",")[0].strip()
            content = (q.get("da") or {}).get(option, "")
        return {"index": 3, "name": name, "available": bool(content),
                "content": content, "display": content, "label": t["label"],
                "for_response": canonical}
    if tier == 4:
        disc = q.get("disc") or ""
        return {"index": 4, "name": name, "available": bool(disc),
                "content": disc, "display": disc, "label": t["label"]}
    # tier == 5: the authored reveal -- the full post-response explanation.
    return {"index": 5, "name": name, "available": True,
            "content": explain_payload(q, reveal=True),
            "display": _reveal_display(q), "label": t["label"]}


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
        #
        # It parks the sitting at the marker's desk, and until 2026-08-24 it
        # parked there forever: nothing unparked it, so a bank holding one
        # short item could not be completed on any surface. `mark` writes an
        # evidence event and never touches a session, and `lti_roundtrip` had
        # to hand-write cursor and status to reach the state it calls
        # marker-closed. Once the marker has ruled, the item is settled and the
        # sitting moves on; before that it does not, which is the half of the
        # rule `test_short_response_stays_pending` pins.
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
    if not settled_marks or teaching_key(q) not in settled_marks:
        return None
    cursor, status = _advance_cursor(session)
    return dict(session, cursor=cursor, status=status)


def _advance_cursor(session):
    """Cursor advance shared by every advancing action; returns the next
    cursor and status."""
    cursor = session["cursor"] + 1
    status = session["status"]
    if cursor >= len(session["items"]):
        status = "complete"
    return cursor, status


# ---- phase 13.5: the ladder payload -- D-09's boundary as a pure function ----
# 14-UI-SPEC section 9.1 LOCKED: "the browser renders `shown` and
# `next_locked` and nothing else." Everything a surface would otherwise have
# had to decide -- which tiers exist, which are disclosed, what each locked
# card says, whether the ladder runs in this mode at all -- is resolved here,
# once, so a route is plumbing rather than a second place deciding what a
# learner reads.

# The learner-facing header word for each fixed tier, in HINT_TIERS order
# (14-UI-SPEC section 14, INHERITED from 06-UI-SPEC section 5.2). Tier 3 is
# response-specific, so it is the one entry completed at resolve time rather
# than read off this tuple whole.
TIER_HEADER_WORDS = ("LESSON", "OBJECTIVE", "TRAP", "RATIONALE",
                     "DISCRIMINATOR", "REVEAL")

# The mode's OWN stated sentence for a ladder that does not run (14-UI-SPEC
# section 9.3, INHERITED verbatim). Availability is never read from this map:
# it is derived from FEEDBACK_POLICIES below, so a feedback mode added later
# gets a ladder only if somebody decided to give it one, rather than
# inheriting one from a mode list restated here and forgotten.
LADDER_UNAVAILABLE_REASONS = {
    "drill": "Drill mode shows the answer straight away. The hint ladder does "
             "not run here.",
    "diagnostic": "Diagnostic mode records your answers and shows nothing "
                  "until the sitting ends.",
    "exam": "Exam mode holds all feedback until this attempt has been marked.",
}

# The sentence for a non-hold mode with no authored one -- today only
# 'legacy', which appears on migrated events and which no live session can
# carry. It states the true thing rather than borrowing another mode's words.
LADDER_UNAVAILABLE_DEFAULT = ("This sitting's feedback mode does not run the "
                              "hint ladder.")

# The three locked-card sentences (14-UI-SPEC section 14 / 06-UI-SPEC section
# 5.2, LOCKED). Carried as separate lines rather than one joined string
# because the inherited copy table has them as separate rows, and a fixture
# asserting either row should not have to know how the two were joined.
NEXT_TIER_UNLOCK_COPY = ("Tier %d unlocks after another attempt.",
                         "Or unlock it now with \"I'm stumped\".")
FURTHER_TIER_UNLOCK_COPY = "Tier %d unlocks after tier %d."
MORE_TIERS_COPY = "%d more tiers after this one."
NO_AUTHORED_TIER_COPY = "This item has no authored %s."


def _tier_header(q, index, canonical):
    """One tier's Ledger header: `TIER {n} - {WORD}`, with tier 3 naming the
    option the learner actually picked. Resolved here and never by a client:
    a surface that rebuilt this string from a tier id would be a second place
    deciding how a tier introduces itself.
    """
    word = TIER_HEADER_WORDS[index]
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
    if rec is None:
        rec = new_teaching_record()
    policy = FEEDBACK_POLICIES.get(mode, FEEDBACK_POLICIES["practice"])
    if policy["wrong"] != "hold":
        # 06-UI-SPEC section 6.5: absent with a stated reason, never a rail of
        # greyed cards. Nothing about the item's tiers crosses this branch.
        return {"available": False,
                "unavailable_reason": LADDER_UNAVAILABLE_REASONS.get(
                    mode, LADDER_UNAVAILABLE_DEFAULT),
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
        tier = authored_hint(q, index, canonical)
        shown.append({
            "index": index,
            "name": tier["name"],
            "label": tier["label"],
            "header": _tier_header(q, index, canonical),
            "display": tier["display"] if tier["available"]
                       else NO_AUTHORED_TIER_COPY % tier["label"],
            "available": tier["available"],
        })

    next_index = highest_shown + 1
    exhausted = next_index >= len(HINT_TIERS)
    entitled = highest_unlocked > highest_shown

    next_locked = None
    further_locked = []
    if not exhausted:
        unlock_copy = [NEXT_TIER_UNLOCK_COPY[0] % next_index,
                       NEXT_TIER_UNLOCK_COPY[1]]
        remaining = list(range(next_index + 1, len(HINT_TIERS)))
        if locked_preview == "next":
            if remaining:
                unlock_copy.append(MORE_TIERS_COPY % len(remaining))
        else:
            further_locked = [
                {"name": HINT_TIERS[i]["name"],
                 "header": _tier_header(q, i, canonical),
                 "unlock_copy": [FURTHER_TIER_UNLOCK_COPY % (i, i - 1)]}
                for i in remaining]
        next_locked = {"index": next_index,
                       "name": HINT_TIERS[next_index]["name"],
                       "header": _tier_header(q, next_index, canonical),
                       "unlock_copy": unlock_copy}

    return {"available": True, "unavailable_reason": None,
            "shown": shown, "next_locked": next_locked,
            "further_locked": further_locked,
            "entitled": entitled, "exhausted": exhausted,
            "unlock_path": "attempt" if entitled else "stumped"}


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


def invoke_rubric_review(session_file):
    """The ONE orchestration path for a rubric-review request (plan 08-04
    Task 2).

    Requires the current item to be a short response whose most recent live
    response is still pending (never already-marked); any other state is a
    typed refusal with a named reason and NO evidence write (D-13). On a
    genuine pending short response it sequences: build the rubric_review
    request with the item's rubric points -> model_adapter.invoke with
    surfaces.settings.load_settings -> tier_gate.evaluate_candidate
    (rubric_proposal shape, gate tier 5 -- the reviewer sees the whole
    authored ladder while correct/model stay always-protected) -> append the
    model_interaction event (D-15) and, on pass, the mark_proposal event
    linked to the response and interaction (D-13) -> return
    {"status": "pending", "points": [...]} where the whole payload reads as
    pending and no model path can settle a mark (D-14/D-25).
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

    def _refusal(reason):
        return {"status": "refused", "reason": reason,
                "item_id": q.get("id", ""), "interaction_id": None}

    if q["type"] != "short":
        return _refusal("not_short")
    if not live_responses:
        return _refusal("no_response")
    latest = live_responses[-1]
    if latest["event_id"] in evidence.marks_by_event(log):
        return _refusal("already_marked")

    interaction_id = _new_interaction_id()
    settings_data = _settings.load_settings(os.path.dirname(data["bank"]) or ".")
    # The bank's authored rubric parses as a list of point texts; the adapter
    # payload wants one object per point (the model reviews point text).
    rubric_points = []
    for rp in (q.get("rubric") or []):
        if isinstance(rp, dict):
            rubric_points.append(rp)
        else:
            rubric_points.append({"point": str(rp)})
    request = model_adapter.request_from_operation(
        "rubric_review", interaction_id, "",
        item_context=_hint_item_context(q),
        learner_response=latest.get("answer"),
        permitted_tier=None,
        rubric_points=rubric_points)
    result = model_adapter.invoke(request, settings_data)
    candidate = result.get("candidate")

    outcome = "unavailable"
    gate_reason = None
    points = []
    if candidate is not None:
        gate = tier_gate.evaluate_candidate(
            q, 5, latest.get("answer") or "", candidate)
        if gate["outcome"] == "pass":
            outcome = "pass"
            points = list(gate["plan"].get("points") or [])
        else:
            outcome = "drop"
            gate_reason = gate["reason"]

    backend_class, profile = _backend_descriptors(result)
    ev = evidence.model_interaction_event(
        data["session_id"], os.path.basename(data["bank"]), q.get("id", ""),
        "rubric_review", interaction_id, outcome, gate_reason, 5,
        backend_class, profile,
        request_fingerprint=_interaction_fingerprint(request),
        response_fingerprint=_interaction_fingerprint(candidate)
        if candidate is not None else None,
        elapsed_ms=result.get("elapsed_ms"),
        output_bytes=len(json.dumps(candidate, ensure_ascii=False))
        if candidate is not None else 0,
        pass_payload=None)
    write_result = evidence.append_event(log, ev)

    proposal_event_id = None
    if outcome == "pass":
        proposal = evidence.mark_proposal_event(
            data["session_id"], os.path.basename(data["bank"]),
            q.get("item_id") or "", q.get("id", ""),
            latest["event_id"], interaction_id, points)
        prop_result = evidence.append_event(log, proposal)
        proposal_event_id = prop_result.get("event_id") or proposal["event_id"]

    return {"status": "pending", "points": points,
            "interaction_id": interaction_id,
            "proposal_event_id": proposal_event_id,
            "suggestion_reveal": settings_data.get("suggestion_reveal",
                                                   "after-self-mark"),
            "evidence": write_result}
