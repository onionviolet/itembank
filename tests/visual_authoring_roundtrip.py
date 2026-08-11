#!/usr/bin/env python3
"""Plan 06.1-02 Task 1: the visual authoring contract.

Proves that a model with only `itembank spec`, the published schemas, and the
golden fixture can author or repair plot and number-line items: SPEC documents
the grammar and its restrictions, named lint codes reject every unsafe or
malformed family with the offending field, schemas/item.schema.json validates
the public interaction contract while refusing scoring material inside the
public renderer configuration, and the golden fixture carries one valid plot
and one valid number-line item plus isolated invalid cases for every lint
family.

A contract-only consumer at the end constructs a valid semantic response and
interprets the result without importing surfaces.quiz_page.

Standard library only, no test framework, runnable as
`python tests/visual_authoring_roundtrip.py`.
"""
import json, os, re, subprocess, sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ITEMBANK = os.path.join(ROOT, "itembank.py")
GOLDEN = os.path.join(ROOT, "fixtures", "visual_authoring_golden.md")
SCHEMAS = os.path.join(ROOT, "schemas")
sys.path.insert(0, ROOT)

import model                                   # noqa: E402
import runtime                                 # noqa: E402
import schema_validate                         # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def ok(msg):
    print("ok: " + msg)


def load_schema(name):
    return json.load(open(os.path.join(SCHEMAS, name), encoding="utf-8"))


# ---- 1. SPEC documents the visual grammar and its restrictions --------------

def check_spec():
    r = subprocess.run([sys.executable, ITEMBANK, "spec"],
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        fail("itembank spec exited %d: %s" % (r.returncode, r.stderr))
    spec = r.stdout
    for needle in ("[TYPE: visual]", "[INTERACTION:", "[VISUAL:", "[SCORING:",
                   "protocol integer", "place_point", "move_point",
                   "select_numberline_point", "set_interval",
                   "numberline_point", "start_closed", "partial_credit",
                   "tolerance", "accessibility", "SCALAR",
                   "visual_json_malformed", "visual_unknown_interaction",
                   "visual_unknown_action", "visual_unknown_scoring_kind",
                   "visual_unknown_member", "visual_invalid_axis",
                   "visual_invalid_scalar", "visual_invalid_tolerance",
                   "visual_empty_accessibility", "visual_duplicate_id",
                   "visual_executable_member"):
        if needle not in spec:
            fail("spec does not document %r" % needle)
    ok("spec: visual grammar, protocol integer, lint codes documented")


# ---- 2. named lint codes with the offending field ---------------------------

# golden fixture layout: the first two items are the valid plot and
# number-line examples; every later item isolates exactly one invalid family.
# Each invalid family maps to the one code lint must emit for that item.
INVALID_FAMILIES = {
    # number: (code, expected field substring)
    3: ("item.visual_json_malformed", "visual"),
    4: ("item.visual_json_malformed", "scoring"),
    5: ("item.visual_unknown_interaction", "interaction"),
    6: ("item.visual_unknown_action", "actions"),
    7: ("item.visual_unknown_scoring_kind", "kind"),
    8: ("item.visual_unknown_member", "visual"),
    9: ("item.visual_unknown_member", "scoring"),
    10: ("item.visual_invalid_axis", "axes"),
    11: ("item.visual_invalid_scalar", "step"),
    12: ("item.visual_invalid_tolerance", "tolerance"),
    13: ("item.visual_empty_accessibility", "accessibility"),
    14: ("item.visual_duplicate_id", "initial"),
    15: ("item.visual_executable_member", "visual"),
}


def check_lint_codes():
    qs = model.parse_bank(open(GOLDEN, encoding="utf-8").read())
    by_number = {q["number"]: q for q in qs}
    errors, warnings = model.lint(qs)
    by_item = {}
    for e in errors + warnings:
        by_item.setdefault(e.item, []).append(e)

    # The two valid items must lint clean of every visual_* finding.
    for num in (1, 2):
        item = by_number.get(num)
        if item is None:
            fail("golden fixture is missing valid item %d" % num)
        tag = "Q%d" % num
        visual_findings = [e for e in by_item.get(tag, [])
                           if e.code.startswith("item.visual_")]
        if visual_findings:
            fail("valid item Q%d produced visual findings: %r"
                 % (num, [(e.code, e.field) for e in visual_findings]))

    for num, (code, field_part) in INVALID_FAMILIES.items():
        tag = "Q%d" % num
        found = [e for e in by_item.get(tag, []) if e.code == code]
        if not found:
            have = sorted({e.code for e in by_item.get(tag, [])})
            fail("Q%d: expected %r, got %r" % (num, code, have))
        if field_part not in found[0].field:
            fail("Q%d: %r names field %r, expected it to address %r"
                 % (num, code, found[0].field, field_part))

    # Every emitted visual code is declared in LINT_CODES (protocol_roundtrip
    # re-checks this structurally; here we pin the ones the fixture exercises).
    for e in errors + warnings:
        if e.code.startswith("item.visual_") and e.code not in model.LINT_CODES:
            fail("code %r not declared in LINT_CODES" % e.code)
    ok("lint: every invalid family fails with a named, field-addressed code; "
       "valid examples stay clean")


# ---- 3. schemas/item.schema.json: the public visual contract ----------------

def check_item_schema():
    doc = load_schema("item.schema.json")
    visual_def = doc.get("$defs", {}).get("visual_item")
    if visual_def is None:
        fail("item.schema.json has no $defs.visual_item")
    if any(ref == "#/$defs/visual_item" for ref in
           [b.get("$ref") for b in doc.get("oneOf", [])]):
        ok("item.schema.json: visual_item is a published oneOf branch")
    else:
        fail("item.schema.json: visual_item is not reachable from oneOf")

    # A real public visual item validates.
    qs = model.parse_bank(open(GOLDEN, encoding="utf-8").read())
    plot = next(q for q in qs if q["number"] == 1)
    public = runtime.public_item(plot)
    errs = schema_validate.validate(public, doc)
    if errs:
        fail("item.schema.json rejects a valid public visual item: %s" % errs[0])

    # Scoring material smuggled into the public renderer_config must fail.
    forged = json.loads(json.dumps(public))
    forged["interaction_contract"]["renderer_config"]["accepted"] = \
        [{"x": "2", "y": "3"}]
    errs = schema_validate.validate(forged, doc)
    if not errs:
        fail("item.schema.json accepted scoring material inside "
             "renderer_config")
    ok("item.schema.json: public visual contract validates; scoring material "
       "in renderer_config is refused")


# ---- 4. a contract-only consumer (no surfaces.quiz_page) --------------------

def check_contract_only_consumer():
    qs = model.parse_bank(open(GOLDEN, encoding="utf-8").read())
    plot = next(q for q in qs if q["number"] == 1)
    nl = next(q for q in qs if q["number"] == 2)

    # The consumer reads ONLY the public contract (as an agent would).
    public_plot = runtime.public_item(plot)
    contract = public_plot["interaction_contract"]
    if contract["response_schema"]["kind"] != "point":
        fail("contract-only consumer cannot determine the response kind")
    # It builds a response from the declared grammar and submits it.
    resp = {"kind": "point", "x": "2", "y": "3"}
    verdict = runtime.score_response(plot, resp)
    if verdict is not True:
        fail("contract-only consumer's response scored %r" % verdict)
    state = runtime.canonical_response(plot, resp)
    observation = runtime.visual_observation(plot, state, verdict, hint_tier=None)
    result = runtime.visual_interaction_result(plot, state, verdict, [observation])
    if result["verdict"] is not True:
        fail("contract-only consumer misread the interaction result")

    # The number-line half-step case from the locked fixtures.
    public_nl = runtime.public_item(nl)
    if public_nl["interaction_contract"]["response_schema"]["kind"] \
            != "numberline_point":
        fail("numberline public schema kind mismatch")
    if runtime.score_response(nl, {"kind": "numberline_point", "value": "1/2"}) \
            is not True:
        fail("contract-only consumer cannot answer the number-line golden case")
    ok("contract-only consumer: SPEC/schema/fixture are enough to author, "
       "respond, and interpret the result without the renderer")


def main():
    check_spec()
    check_lint_codes()
    check_item_schema()
    check_contract_only_consumer()
    print("PASS visual_authoring_roundtrip.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
