#!/usr/bin/env python3
"""Exact detector threshold and ordering suite for the Phase 11 second
quality gate (plan 11-04 Task 1, AUDIT-07/D-09/D-10).

Run:
    python tests/audit_quality_roundtrip.py

Stdlib only. Boundary fixtures live in fixtures/audit/quality_cases.json; the
suite also proves co-reporting without aggregate scores, deterministic
ordering under reordered input, identity/fingerprint immutability, detector
versions, and strict schema conformance of every finding.
"""
import copy
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import authoring
import model


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def load_cases():
    path = os.path.join(ROOT, "fixtures", "audit", "quality_cases.json")
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def run_case(case_id, spec):
    questions = model.parse_bank(spec["bank"])
    if not questions:
        fail("%s: fixture bank must parse into questions" % case_id)
    findings = authoring.quality_gate(questions)
    codes = {f["code"] for f in findings}
    expect = spec["expect"]
    for code in expect["codes"]:
        if code not in codes:
            fail("%s: expected finding %s, got %s"
                 % (case_id, code, sorted(codes)))
    for code in expect["absent"]:
        if code in codes:
            fail("%s: unexpected finding %s" % (case_id, code))
    return findings


def main():
    cases = load_cases()
    if len(cases) < 10:
        fail("fixture must carry the full boundary matrix, got %d cases"
             % len(cases))

    # --- exact thresholds and floors --------------------------------------
    skew_findings = run_case("skew_blocks_above_40", cases["skew_blocks_above_40"])
    run_case("skew_equality_at_40_passes", cases["skew_equality_at_40_passes"])
    run_case("skew_inactive_below_12", cases["skew_inactive_below_12"])
    run_case("near_duplicate_blocks_at_0_85",
             cases["near_duplicate_blocks_at_0_85"])
    run_case("near_duplicate_just_below_passes",
             cases["near_duplicate_just_below_passes"])
    run_case("near_duplicate_five_token_floor_passes",
             cases["near_duplicate_five_token_floor_passes"])
    run_case("answer_leak_blocks_unique_run",
             cases["answer_leak_blocks_unique_run"])
    run_case("answer_leak_two_token_run_passes",
             cases["answer_leak_two_token_run_passes"])
    run_case("answer_leak_shared_with_distractor_passes",
             cases["answer_leak_shared_with_distractor_passes"])
    run_case("rationale_missing_line_blocks",
             cases["rationale_missing_line_blocks"])
    run_case("rationale_missing_would_be_blocks",
             cases["rationale_missing_would_be_blocks"])
    run_case("rationale_complete_passes", cases["rationale_complete_passes"])

    # --- measured evidence is present on every blocking finding ------------
    for f in skew_findings:
        if f["severity"] != "block" or not f.get("evidence"):
            fail("skew finding must carry severity block and measured "
                 "evidence")
        for key in ("total_mc", "max_share", "block_above"):
            if key not in f["evidence"]:
                fail("skew evidence missing %r" % key)

    # --- co-reporting without an aggregate score (D-10) --------------------
    co_bank = "\n\n".join([
        cases["skew_blocks_above_40"]["bank"],
        cases["near_duplicate_blocks_at_0_85"]["bank"],
        cases["answer_leak_blocks_unique_run"]["bank"],
        cases["rationale_missing_would_be_blocks"]["bank"],
    ]) + "\n"
    questions = model.parse_bank(co_bank)
    findings = authoring.quality_gate(questions)
    codes = {f["code"] for f in findings}
    expected = {"quality.answer_skew", "quality.near_duplicate_stems",
                "quality.answer_leak", "quality.distractor_rationale"}
    if not expected <= codes:
        fail("co-reporting: expected all four detectors to fire together, "
             "got %s" % sorted(codes))
    for f in findings:
        if "score" in f:
            fail("co-reporting: a finding must never carry an aggregate "
                 "score field")
        if f["detector_version"] != authoring.DETECTOR_VERSIONS[f["detector"]]:
            fail("co-reporting: detector %s version drift" % f["detector"])

    # --- deterministic ordering under reordered input ----------------------
    shuffled = list(questions)
    shuffled.reverse()
    findings2 = authoring.quality_gate(shuffled)
    if authoring.canonical_json(findings) != \
            authoring.canonical_json(findings2):
        fail("ordering: reordered questions must serialize identical "
             "findings")

    # --- the gate never mutates ids, objectives, or fingerprints -----------
    before = copy.deepcopy(questions)
    authoring.quality_gate(questions)
    if before != questions:
        fail("identity: quality_gate mutated the parsed questions")
    fprint_before = [model.content_fingerprint(q) for q in before]
    fprint_after = [model.content_fingerprint(q) for q in questions]
    if fprint_before != fprint_after:
        fail("identity: quality_gate changed content fingerprints")

    # --- every finding validates against the strict schema -----------------
    import resources
    import schema_validate as sv
    schema = json.loads(resources.read_text(
        "schemas/quality_finding.schema.json"))
    for f in findings:
        errs = sv.validate(f, schema)
        if errs:
            fail("schema: finding fails quality_finding schema: %s" % errs[:2])

    print("OK: quality -- exact four-detector thresholds and floors, "
          "co-reporting without aggregate score, deterministic ordering, "
          "identity/fingerprint immutability, schema conformance")


if __name__ == "__main__":
    sys.exit(main())
