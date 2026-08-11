#!/usr/bin/env python3
"""The tier gate: a deterministic, fail-closed boundary between provider
output and a learner-facing payload (Phase 8, plan 08-01).

This is the phase's hardest constraint, scheduled first: the no-leak boundary
must be proven before any provider is connected. The gate follows RESEARCH
Pattern 1's five-step algorithm:

  1. Build a fact manifest from the private item + the learner's most recent
     genuine wrong response + the Phase 6 permitted tier. Stable internal
     fact ids come from an explicit include map (TIER_FACTS); everything at a
     tier above the permitted one, plus the correct/model answer at any tier,
     is protected. A fact whose resolved text contains a normalized protected
     fragment is itself marked ambiguous and may never be referenced.
  2. Strict schema validation against schemas/tier_gate.schema.json -- a
     closed envelope with no learner-facing free-prose field. Any error is a
     drop (gate.schema_invalid).
  3. Span resolution: the candidate's focus_span must be a normalized-whitespace
     exact substring of the learner response, matching exactly once.
  4. Fact resolution: every fact_ids entry must exist in the manifest, be
     allowed, be unique, and be non-ambiguous.
  5. Move validation against the fixed renderable tutoring moves.

It never rewrites a leaking candidate into something that might change
meaning (D-06); uncertain output is dropped whole. Only `render_hint` /
`render_proposal` emit learner text, from fixed runtime templates, and
`learner_payload` is the single constructor for a learner-facing payload --
drop/unavailable carry no reason, tier, fact, provider, or detector detail
(D-08, D-09). Pure functions: no I/O, no side effects, deterministic across
calls (the reason-code stability replay guarantee).
"""
import json

import resources
import schema_validate


# The fixed, machine-readable reason codes a drop can carry. Stable values:
# evidence (plan 08-03) records them per interaction, and identical candidate
# replays always return the same outcome and reason.
GATE_REASON_CODES = (
    "gate.schema_invalid",
    "gate.span_unmatched",
    "gate.fact_protected",
    "gate.fact_unknown",
    "gate.ambiguous",
    "gate.unsupported_move",
)

# The explicit include map (D-06 / content_fingerprint precedent): which item
# fields are facts at which authored tier. Tier 3 is response-specific -- the
# distractor analysis for the learner's picked option only. `correct` and
# `model` are deliberately not facts here: they are always protected.
TIER_FACTS = {
    0: ("lesson_ref", "lesson_slug"),
    1: ("objective", "objective_line"),
    2: ("trap",),
    3: ("da",),
    4: ("disc", "second"),
    5: ("why", "notes"),
}

# The answer material protected at *every* tier: the key and the model answer.
ALWAYS_PROTECTED_KEYS = ("correct", "model")

# A protected fragment shorter than this is not treated as an overlap signal
# (e.g. the canonical key "B", or a two-letter option text) -- below this
# length the substring would make almost every fact ambiguous and would turn
# the conservative rule into a useless one.
MIN_FRAGMENT_LEN = 4

# The fixed tutoring-move templates. They reference only the learner's own
# span and the one allowed fact text; they never assert correctness of any
# option, never emit the model answer, and never accept provider prose.
_HINT_TEMPLATES = {
    "anchor_error": "You answered \"{span}\". Consider the trap this points to: {fact}",
    "guide_fact": "You answered \"{span}\". A guide to keep in mind: {fact}",
    "prompt_reflection": "You answered \"{span}\". Reflect on this point: {fact}",
}


def _norm(s):
    """Normalized text for span matching and protected-fragment overlap:
    casefold plus whitespace collapse (RESEARCH Pattern 1 step 4).
    """
    return " ".join(str(s or "").split()).lower()


def _resolve_fact_text(item, key, picked_option):
    """Resolve one fact's text from the item. Returns "" when the field is
    absent so the fact simply is not part of the manifest.
    """
    if key == "lesson_ref":
        return item.get("lesson_ref") or ""
    if key == "lesson_slug":
        return item.get("lesson_slug") or ""
    if key == "objective":
        return item.get("objective") or ""
    if key == "objective_line":
        return item.get("objective_line") or ""
    if key == "trap":
        return item.get("trap") or ""
    if key == "da":
        return (item.get("da") or {}).get(picked_option, "") if picked_option else ""
    if key == "disc":
        return item.get("disc") or ""
    if key == "second":
        return item.get("second") or ""
    if key == "why":
        return item.get("why") or ""
    if key == "notes":
        return "; ".join(str(n) for n in (item.get("notes") or []) if n)
    if key == "correct":
        if item.get("type") in ("mc", "multi"):
            texts = [item.get("opts", {}).get(c, "")
                     for c in (item.get("correct") or [])]
            return "; ".join(t for t in texts if t)
        return ", ".join(str(c) for c in (item.get("correct") or []))
    if key == "model":
        return item.get("model") or ""
    return ""


def _picked_option(item, wrong_response):
    """Derive the picked option from the learner's canonical response the way
    Phase 6's authored_hint does: the first letter of the canonical form.
    """
    if item.get("type") in ("mc", "multi"):
        return str(wrong_response or "").split(",")[0].strip().upper()
    return None


def build_fact_manifest(item, tier, wrong_response, picked_option=None):
    """Build the permitted/reserved fact manifest for one (item, tier,
    learner-response) triple (RESEARCH Pattern 1 step 1).

    Returns a dict with:
      - `facts`: every resolvable authored fact by stable id (tier 0..5)
      - `allowed_ids`: facts at or below `tier`, not ambiguous
      - `protected_ids`: facts above `tier`, plus correct/model at any tier
      - `ambiguous_ids`: allowed facts whose resolved text contains a
        normalized protected fragment -- these may never be referenced
      - `protected_fragments`: the normalized texts a render or reference may
        never reproduce (used for the payload-boundary scan too)
      - `span`: the exact learner response the gate matches spans against
    """
    facts = {}
    for t in range(6):
        for key in TIER_FACTS[t]:
            if key == "da":
                text = _resolve_fact_text(item, key, picked_option)
                if not text:
                    continue
                fid = "tier%d.da.%s" % (t, picked_option)
            else:
                text = _resolve_fact_text(item, key, None)
                if not text:
                    continue
                fid = "tier%d.%s" % (t, key)
            facts[fid] = {"id": fid, "tier": t, "key": key, "text": text}

    protected = {}
    for key in ALWAYS_PROTECTED_KEYS:
        text = _resolve_fact_text(item, key, None)
        if text:
            protected[key] = {"id": key, "key": key, "text": text}

    protected_ids = set(protected)
    for fid, f in facts.items():
        if f["tier"] > tier:
            protected_ids.add(fid)

    protected_fragments = []
    for fid in sorted(protected_ids):
        f = facts.get(fid) or protected.get(fid)
        n = _norm(f["text"])
        if len(n) >= MIN_FRAGMENT_LEN:
            protected_fragments.append(n)
    protected_fragments = sorted(set(protected_fragments))

    ambiguous_ids = set()
    for fid, f in facts.items():
        if fid in protected_ids:
            continue
        n = _norm(f["text"])
        if any(frag in n for frag in protected_fragments):
            ambiguous_ids.add(fid)

    allowed_ids = set(facts) - protected_ids - ambiguous_ids
    return {
        "tier": tier,
        "wrong_response": wrong_response,
        "span": wrong_response,
        "picked_option": picked_option,
        "facts": facts,
        "allowed_ids": allowed_ids,
        "protected_ids": protected_ids,
        "ambiguous_ids": ambiguous_ids,
        "protected_fragments": protected_fragments,
    }


def evaluate_candidate(item, tier, wrong_response, candidate):
    """Run the four gate layers over one provider candidate.

    Returns {"outcome": "pass", "reason": None, "plan": candidate} or
    {"outcome": "drop", "reason": <GATE_REASON_CODES member>, "plan": None}.
    Pure and deterministic: the same candidate twice returns the same outcome
    and reason.
    """
    picked = _picked_option(item, wrong_response)
    manifest = build_fact_manifest(item, tier, wrong_response, picked)

    # Layer 1: strict schema. Any validation error is a drop; unknown fields
    # and unknown kinds never reach a renderer (T-08-01).
    errs = schema_validate.validate(candidate, _CANDIDATE_SCHEMA)
    if errs:
        return {"outcome": "drop", "reason": "gate.schema_invalid", "plan": None}

    if candidate.get("kind") == "hint_plan":
        return _evaluate_hint_plan(manifest, candidate)
    return _evaluate_proposal(manifest, candidate)


def _evaluate_hint_plan(manifest, plan):
    # Layer 2: span resolution. The focus_span must be a normalized exact
    # substring of the learner response, matching exactly once; empty spans
    # and adjacency/ordering duplicates are a drop (D-10 probe edges).
    norm_wr = _norm(manifest["wrong_response"])
    norm_span = _norm(plan.get("focus_span") or "")
    if not norm_span or norm_wr.count(norm_span) != 1:
        return {"outcome": "drop", "reason": "gate.span_unmatched", "plan": None}

    # Layer 3: fact resolution. Every id must exist, be allowed, be unique,
    # and be non-ambiguous. Provider labels are never trusted (Pitfall 1).
    known = set(manifest["facts"]) | manifest["protected_ids"]
    seen = []
    for fid in plan.get("fact_ids") or []:
        if fid in seen:
            return {"outcome": "drop", "reason": "gate.schema_invalid", "plan": None}
        seen.append(fid)
        if fid not in known:
            return {"outcome": "drop", "reason": "gate.fact_unknown", "plan": None}
        if fid in manifest["protected_ids"]:
            return {"outcome": "drop", "reason": "gate.fact_protected", "plan": None}
        if fid in manifest["ambiguous_ids"]:
            return {"outcome": "drop", "reason": "gate.ambiguous", "plan": None}
    if len(seen) > 2:
        # The schema cannot express maxItems (not in SUPPORTED), so the
        # bounded-plan ceiling of two distinct fact references is gate policy.
        return {"outcome": "drop", "reason": "gate.schema_invalid", "plan": None}

    # Layer 4: move validation. The schema already enum-constrains moves; this
    # check is the renderability net -- a move with no template never renders.
    if plan.get("move") not in _HINT_TEMPLATES:
        return {"outcome": "drop", "reason": "gate.unsupported_move", "plan": None}

    return {"outcome": "pass", "reason": None, "plan": plan}


def _evaluate_proposal(manifest, plan):
    # A rubric proposal passes schema validation; the one additional gate is
    # the conservative protected-fragment scan over each rationale (D-06), so
    # no key/model/higher-tier material rides into a reviewer-facing payload
    # through the bounded free-text channel.
    for point in plan.get("points") or []:
        rat = _norm(point.get("rationale") or "")
        if any(frag in rat for frag in manifest["protected_fragments"]):
            return {"outcome": "drop", "reason": "gate.ambiguous", "plan": None}
    return {"outcome": "pass", "reason": None, "plan": plan}


def _allowed_fact_texts(plan, manifest):
    """The resolved, allowed fact texts the renderer may emit, in fact_ids
    order (already proven allowed and non-ambiguous by the gate).
    """
    out = []
    for fid in plan.get("fact_ids") or []:
        f = manifest["facts"].get(fid)
        if f:
            out.append(f["text"])
    return out


def render_hint(plan, manifest):
    """Render a passed hint plan through the fixed tutoring-move template.

    Returns a dict {"kind": "hint", "move", "text"} or None when the plan
    (or its move) is not renderable. The text contains exactly the learner's
    span and the allowed fact texts -- never provider prose.
    """
    if not plan:
        return None
    template = _HINT_TEMPLATES.get(plan.get("move"))
    if template is None:
        return None
    facts = _allowed_fact_texts(plan, manifest)
    if not facts:
        return None
    text = template.format(span=plan.get("focus_span") or "",
                           fact="; ".join(facts))
    return {"kind": "hint", "move": plan["move"], "text": text}


def render_proposal(plan, manifest):
    """Render a passed rubric proposal as a pending-shaped suggestion.

    Returns {"kind": "proposal", "points": [...], "pending": True}. An empty
    points array stays pending/unknown -- never a default pass (D-13/D-14).
    """
    if not plan:
        return None
    return {"kind": "proposal",
            "points": [dict(p) for p in (plan.get("points") or [])],
            "pending": True}


def learner_payload(outcome, generated=None):
    """The single constructor for a learner-facing payload (D-08).

    pass -> {"status": "pass", "generated": <rendered dict>}; drop and
    unavailable -> {"status": outcome, "generated": None}. The learner-facing
    shape never carries a reason code, a tier number, fact text, provider
    bytes, backend/profile ids, or detector detail -- a drop never reveals
    why. Any non-pass outcome forces generated to None.
    """
    if outcome == "pass":
        return {"status": "pass", "generated": generated}
    return {"status": outcome, "generated": None}


def _load_candidate_schema():
    return json.loads(resources.read_text("schemas/tier_gate.schema.json"))


_CANDIDATE_SCHEMA = _load_candidate_schema()
