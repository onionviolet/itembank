#!/usr/bin/env python3
"""Wave-0 release gate for the Phase 8 tier gate (plan 08-01).

The deterministic adversarial gate between provider output and a
learner-facing payload: a legal bounded hint plan passes and renders only a
fixed runtime template, every leakage class drops whole with a stable reason
code, and learner payloads are provably free of key, tier, fact, provider,
and detector detail (D-05 through D-09, D-11).

Stdlib only; run as `python tests/model_gate_roundtrip.py`.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import runtime                                                    # noqa: E402
import schema_validate                                            # noqa: E402
import tier_gate                                                  # noqa: E402

CASES_PATH = os.path.join(ROOT, "fixtures", "model_gate_cases.json")
SCHEMA_PATH = os.path.join(ROOT, "schemas", "tier_gate.schema.json")


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def norm(s):
    """Normalized text for span matching and overlap checks: casefold plus
    whitespace collapse (RESEARCH Pattern 1 step 4).
    """
    return " ".join(str(s or "").split()).lower()


def flatten(obj):
    """Yield (key, value) for every key at every depth of a JSON-like
    structure -- used to assert a forbidden string never appears anywhere in
    a learner-facing payload (the same discipline evidence_roundtrip's
    flatten() applies to its forbidden keys).
    """
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield (k, v)
            yield from flatten(v)
    elif isinstance(obj, list):
        for el in obj:
            yield from flatten(el)


def base_mc_item():
    """A synthetic mc item whose tier-0..2 authored facts are all clean of
    protected fragments, so a tier-2 hint plan can legitimately reference the
    trap. The correct option text ("Paris") appears only in protected
    material (da/why/correct), never in an allowed fact.
    """
    return {
        "type": "mc",
        "id": "q1",
        "number": 1,
        "stem": "Which city is the capital of France?",
        "opts": {"A": "London", "B": "Paris", "C": "Berlin", "D": "Rome"},
        "correct": ["B"],
        "select": 1,
        "objective": "geo/capital-cities",
        "objective_line": "Identify the capital of France.",
        "lesson_ref": "Capitals of Europe",
        "lesson_slug": "capitals-of-europe",
        "why": "Paris is the seat of the French government and the seat of national power.",
        "disc": "The item turns on the seat of government, not the most populous city.",
        "second": "Berlin is the seat of Germany's government and is often over-picked by analogy.",
        "trap": "Learners are drawn to the most famous city rather than the one that governs the country.",
        "da": {
            "A": "London is the capital of the United Kingdom, not of France.",
            "B": "Paris is the seat of the French government; it is the capital of France.",
            "C": "Berlin is the capital of Germany, not France.",
            "D": "Rome is the capital of Italy, not France.",
        },
        "notes": ["The distinction is between seat of government and largest city."],
        "conf": "high",
    }


def base_short_item():
    """A synthetic short item with a model answer and rubric -- the object of
    a rubric proposal and the only place a provider could try to reproduce the
    model answer directly.
    """
    return {
        "type": "short",
        "id": "q9",
        "number": 9,
        "stem": "Explain the role of Paris in France's government.",
        "model": "Paris is the capital and the seat of government of France.",
        "rubric": ["Names the capital", "States the seat of government",
                   "Notes that Paris is the nation's capital"],
        "objective": "geo/capital-cities",
        "objective_line": "Explain the role of Paris.",
        "why": "The response must identify Paris as the capital and seat of government.",
        "disc": "The item turns on naming both the capital and the seat of government.",
        "second": "",
        "trap": "A response naming only a large city is incomplete.",
        "notes": [],
        "conf": "high",
    }


# ---- Task 1: the tracer -- one legal path passes, one leak drops whole ----

def test_manifest_exposes_allowed_and_protected_facts():
    item = base_mc_item()
    m = tier_gate.build_fact_manifest(item, tier=2, wrong_response="B",
                                      picked_option="B")
    for fid in ("tier0.lesson_ref", "tier0.lesson_slug", "tier1.objective",
                "tier1.objective_line", "tier2.trap"):
        if fid not in m["facts"]:
            fail("tier-2 manifest must expose fact %r, facts=%r"
                 % (fid, sorted(m["facts"])))
        if fid not in m["allowed_ids"]:
            fail("tier-2 manifest must allow %r, allowed=%r"
                 % (fid, sorted(m["allowed_ids"])))
    for fid in ("tier3.da.B", "tier4.disc", "tier4.second", "tier5.why",
                "tier5.notes", "correct"):
        if fid not in m["protected_ids"]:
            fail("tier-2 manifest must protect %r, protected=%r"
                 % (fid, sorted(m["protected_ids"])))
    if m["span"] != "B":
        fail("manifest must carry the exact learner span 'B', got %r" % m["span"])


def test_legal_hint_passes_and_renders_fixed_template():
    item = base_mc_item()
    candidate = {
        "kind": "hint_plan",
        "interaction_id": "int-000001",
        "focus_span": "B",
        "fact_ids": ["tier2.trap"],
        "move": "anchor_error",
    }
    res = tier_gate.evaluate_candidate(item, 2, "B", candidate)
    if res["outcome"] != "pass" or res["reason"] is not None:
        fail("a legal hint_plan must pass, got %r" % (res,))
    manifest = tier_gate.build_fact_manifest(item, 2, "B", "B")
    rendered = tier_gate.render_hint(candidate, manifest)
    if rendered is None:
        fail("a passed hint plan must render, got None")
    text = rendered["text"]
    if "B" not in text:
        fail("rendered hint must carry the learner's exact span, got %r" % text)
    if item["trap"] not in text:
        fail("rendered hint must carry the one allowed fact text, got %r" % text)
    for key in ("why", "disc", "second"):
        if item[key] and item[key] in text:
            fail("rendered hint leaked protected fact %r: %r" % (key, text))
    if "Paris" in text:
        fail("rendered hint leaked the correct option text: %r" % text)


def test_protected_fact_drops_whole():
    item = base_mc_item()
    candidate = {
        "kind": "hint_plan",
        "interaction_id": "int-000002",
        "focus_span": "B",
        "fact_ids": ["tier5.why"],
        "move": "anchor_error",
    }
    res = tier_gate.evaluate_candidate(item, 2, "B", candidate)
    if res["outcome"] != "drop" or res["reason"] != "gate.fact_protected":
        fail("protected-fact reference must drop with gate.fact_protected, got %r"
             % (res,))
    if res["plan"] is not None:
        fail("a dropped candidate must never be rendered, plan=%r" % (res["plan"],))
    blob = json.dumps(res)
    if "Paris" in blob:
        fail("drop result leaked provider/private text: %r" % blob)


def test_extra_field_drops_schema_invalid():
    item = base_mc_item()
    candidate = {
        "kind": "hint_plan",
        "interaction_id": "int-000003",
        "focus_span": "B",
        "fact_ids": ["tier2.trap"],
        "move": "anchor_error",
        "text": "The correct answer is Paris.",
    }
    res = tier_gate.evaluate_candidate(item, 2, "B", candidate)
    if res["outcome"] != "drop" or res["reason"] != "gate.schema_invalid":
        fail("an extra free-prose field must drop with gate.schema_invalid, got %r"
             % (res,))
    schema = json.load(open(SCHEMA_PATH, encoding="utf-8"))
    hint_props = schema["$defs"]["hint_plan"]["properties"]
    for free in ("text", "content", "prose", "explanation"):
        if free in hint_props:
            fail("hint_plan schema must not carry a learner-facing "
                 "free-prose property %r" % free)


def test_schema_uses_supported_keywords_only():
    schema = json.load(open(SCHEMA_PATH, encoding="utf-8"))
    # check_schema walks the whole document and raises SchemaError on any
    # keyword outside schema_validate.SUPPORTED -- a green call proves the
    # new tier-gate schema stays inside the in-repo validator's contract.
    schema_validate.check_schema(schema)
    good = {"kind": "hint_plan", "interaction_id": "int-000001",
            "focus_span": "B", "fact_ids": ["tier2.trap"], "move": "anchor_error"}
    if schema_validate.validate(good, schema):
        fail("a legal hint_plan must validate against the tier-gate schema")
    bad = dict(good, text="free prose")
    if not schema_validate.validate(bad, schema):
        fail("an extra free-prose field must fail the tier-gate schema")


def main():
    test_schema_uses_supported_keywords_only()
    test_manifest_exposes_allowed_and_protected_facts()
    test_legal_hint_passes_and_renders_fixed_template()
    test_protected_fact_drops_whole()
    test_extra_field_drops_schema_invalid()
    print("model gate roundtrip: ok")


if __name__ == "__main__":
    main()
