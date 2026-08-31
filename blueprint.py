#!/usr/bin/env python3
"""Blueprint fidelity, the one new gate of ACTIVITY-02's five.

A peer module beside `authoring.py` and `auditor.py`, importable on its own,
holding no state between calls, opening no file, and taking no lock.

**This module imports `model` and `runtime` and nothing else from this
repository, and the absence of every other import is the contract.** It cannot
write, because it does not import `journal` or `course`. It cannot read the
evidence store, because it does not import `evidence`. It cannot authorize
anything, because it does not import `director`. Those three rules are
structural rather than maintained by care, and a test asserts each one by the
absence of the attribute.

The two imports it does have are the point. Gate 5 calls
`runtime.score_response`, the one scorer, rather than deciding a verdict of its
own, and every question this module reads was parsed by `model.parse_bank`, the
one parser. ACTIVITY-02's own goal text forbids a second parser or scorer, and
this module is arranged so it could not become one.

**What this gate covers, and what it deliberately does not.** It covers
ACTIVITY-02's eight declared blueprint dimensions: construct, domain weight,
demand, format, difficulty, timing, tools, and feedback conditions. It covers
nothing else. Duplicate stems, answer-position skew, answer leak, and
distractor rationale already belong to `model.lint` and
`authoring.quality_gate`, and a third pass over the same failure mode at a
third rigor level is how two detectors come to disagree in public.

**Three of the eight are checkable from a parsed bank; five are not.** Format,
difficulty and domain weight come from the question dicts `model.parse_bank`
already produces. Construct, demand, timing, tools and feedback conditions are
not carried by the bank format, so the caller supplies them as facts. A field
with no supplied fact produces a `blueprint.unverifiable` finding at severity
`warn`, never a silent pass: a silent pass would let an exam-fidelity claim
rest on three checked fields while claiming eight.

**No aggregate.** No function here returns a float, a percentage, or a single
number standing for overall compliance. Findings are per field and per item,
for the same reason `authoring.py`'s second quality gate is never an aggregate
score: a number hides which of the eight fields actually failed, and the whole
value of the gate is knowing that.
"""
import json

import model
import runtime

BLUEPRINT_SCHEMA_VERSION = 1
BLUEPRINT_SCHEMA_RESOURCE = "schemas/blueprint.schema.json"

# ACTIVITY-02's eight declared dimensions, in the requirement's own order:
# "construct, domain weight, demand, format, difficulty, timing, tools,
# feedback conditions". Transcribed rather than chosen, so the vocabulary and
# the requirement cannot drift apart.
BLUEPRINT_FIELDS = ("construct", "domain_weight", "demand", "format",
                    "difficulty", "timing", "tools", "feedback_conditions")

BLUEPRINT_DETECTOR = "blueprint_fidelity"
BLUEPRINT_DETECTOR_VERSION = 1

# ACTIVITY-02's five gates, in the order they run. The order is not arbitrary:
# gate 4 runs after gate 3 because `authoring.quality_gate`'s findings are an
# input a blueprint finding may cite, and running blueprint first would make it
# the first thing a bad draft hits, so its findings would describe a set lint
# and quality were going to reject anyway. That is noise rather than signal.
GATE_STEPS = ("parser", "lint", "review", "blueprint", "runtime")

GATE_RESULT_KEYS = ("step", "passed", "findings")

# The facts the bank format does not carry, supplied by the caller. Set-level
# facts describe the whole drafted set; item-level facts are keyed by item id.
SET_FACT_KEYS = ("construct", "feedback_conditions")
ITEM_FACT_KEYS = ("demand", "timing_seconds", "tools")

# Built from a set-then-sorted tuple so sortedness is structural, the
# ADAPTER_CODES construction precedent.
# Built from a set-then-sorted tuple so sortedness is structural, the
# ADAPTER_CODES construction precedent.
#
# Fourteen, not the thirteen plan 15B-02 Task 1 asserted. Task 1 described the
# gate's thin form and Task 2 widened it, and the widening names
# `blueprint.difficulty_out_of_band` as its own code: a question in a band the
# form does not permit at all is a different defect from a band that appears
# too often, and collapsing the two would report one number for two problems.
# Task 2 also renames three of Task 1's codes to the names it uses throughout.
# The count assertion in `tests/blueprint_roundtrip.py` was updated to match,
# and the divergence is recorded here rather than resolved by dropping the
# code Task 2 needs.
BLUEPRINT_CODES = tuple(sorted({
    "blueprint.absent",
    "blueprint.construct_mismatch",
    "blueprint.demand_out_of_tolerance",
    "blueprint.disposition_rationale_required",
    "blueprint.disposition_reviewer_required",
    "blueprint.disposition_superseded",
    "blueprint.difficulty_out_of_band",
    "blueprint.difficulty_share_out_of_tolerance",
    "blueprint.domain_weight_out_of_tolerance",
    "blueprint.feedback_conditions_mismatch",
    "blueprint.format_not_permitted",
    "blueprint.invalid",
    "blueprint.item_count_out_of_tolerance",
    "blueprint.runtime_mismatch",
    "blueprint.stale_dependent",
    "blueprint.timing_out_of_tolerance",
    "blueprint.tools_not_permitted",
    "blueprint.unknown_disposition",
    "blueprint.unverifiable",
}))

WARN_CODES = ("blueprint.absent", "blueprint.unverifiable")


class BlueprintError(Exception):
    """A typed blueprint failure: machine-readable `code` plus `message`, the
    same two-argument shape `graph.GraphError` and `director.DirectorError`
    use."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


def canonical_json(obj):
    """Deterministic UTF-8 JSON serialization, the same shape
    `authoring.canonical_json` uses.

    Duplicated deliberately rather than imported: importing `authoring` here
    would make the dependency circular, since `authoring` imports this module
    to run the gate. Two identical five-line serializers is a smaller cost than
    a cycle, and the sort key they feed is the only thing either is used for.
    """
    return json.dumps(obj, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"))


def _load_schema():
    import resources
    return json.loads(resources.read_text(BLUEPRINT_SCHEMA_RESOURCE))


def validate_blueprint(doc):
    """A blueprint document, validated before any field of it is read.

    The schema call comes first and no field is read until it returns clean,
    the same discipline `director.validate_recommendation` follows: a blueprint
    may arrive from a file, a model, or a hand edit, and reading a field to
    decide whether to validate makes the read the thing validation was supposed
    to protect.
    """
    import schema_validate

    errors = schema_validate.validate(doc, _load_schema())
    if errors:
        raise BlueprintError(
            "blueprint.invalid",
            "the blueprint does not validate against the blueprint contract: "
            "%s; nothing was accepted" % errors[0])
    return dict(doc)


def blueprint_finding(code, severity, item, evidence, remediation):
    """One finding, in `quality_finding.schema.json`'s record shape.

    The shape is reused rather than reinvented so a blueprint finding slots
    into `audit_report.schema.json`'s existing `proposal.gates` object as one
    more named array. A second report envelope would mean two ways to read a
    gate result.
    """
    if code not in BLUEPRINT_CODES:
        raise BlueprintError(
            "blueprint.invalid",
            "%s is not one of the thirteen blueprint codes; the vocabulary is "
            "closed" % code)
    return {"schema_version": BLUEPRINT_SCHEMA_VERSION,
            "detector": BLUEPRINT_DETECTOR,
            "detector_version": BLUEPRINT_DETECTOR_VERSION,
            "severity": severity,
            "code": code,
            "item": item,
            "evidence": evidence,
            "remediation": remediation}


def _unverifiable(field, reason):
    return blueprint_finding(
        "blueprint.unverifiable", "warn", "BANK",
        {"field": field, "reason": reason},
        "supply the %s fact for this set, or accept that the exam-fidelity "
        "claim rests on fewer than eight checked fields" % field)


def observed_share(count, total):
    """One observed share as integer percentage points.

    Integer arithmetic throughout, rounded to the nearest point with ties
    rounding up. Floats never enter: the tolerance boundary is an exact integer
    comparison, and a float would reintroduce the comparison ambiguity the
    inclusive-boundary rule exists to settle.

    A total of zero returns zero rather than raising. An empty set has no
    observed share, and the count check is where an empty set is caught.
    """
    if not total:
        return 0
    return (count * 200 + total) // (total * 2)


def within_tolerance(observed, declared, tolerance):
    """Whether an observed value is within tolerance of a declared one.

    Less than or equal, deliberately: the boundary is INCLUSIVE, so a value
    differing by exactly the tolerance passes. That matches the shipped
    precedent in `authoring.SKEW_BLOCK_ABOVE`, which blocks only ABOVE its
    threshold, and `authoring.py`'s own comment recording that equality passes
    to match the live lint precedent.

    Every tolerance check in this module calls this. One boundary rule means
    the equality case cannot be right in one dimension and wrong in another.
    """
    return abs(observed - declared) <= (tolerance or 0)


def _format_findings(questions, bp):
    """Field 4, format: the one dimension fully checkable from a parsed bank."""
    findings = []
    fmt = bp.get("format") or {}
    permitted = list(fmt.get("permitted_types") or ())
    for q in questions:
        if q.get("type") not in permitted:
            findings.append(blueprint_finding(
                "blueprint.format_not_permitted", "block", q.get("id") or "",
                {"observed_type": q.get("type"), "permitted": permitted},
                "rewrite this item as one of the permitted types, or record a "
                "blueprint version that permits this type"))
    declared = fmt.get("item_count")
    tolerance = fmt.get("count_tolerance") or 0
    if isinstance(declared, int):
        observed = len(questions)
        if not within_tolerance(observed, declared, tolerance):
            findings.append(blueprint_finding(
                "blueprint.item_count_out_of_tolerance", "block", "BANK",
                {"observed_count": observed, "declared_count": declared,
                 "tolerance": tolerance},
                "add or remove items until the count is within %d of %d"
                % (tolerance, declared)))
    return findings


def _domain_weight_findings(questions, bp):
    """Field 2, domain weight: observed share per declared domain.

    A question counts toward a domain when its `objective` starts with that
    domain's `objective_prefix`. A prefix rather than an exact match, because a
    bank authors objectives at a finer grain than a blueprint declares domains,
    and requiring equality would make the blueprint dictate the bank's wording.
    """
    findings = []
    block = bp.get("domain_weight") or {}
    tolerance = block.get("tolerance") or 0
    total = len(questions)
    for row in block.get("shares") or ():
        prefix = row.get("objective_prefix") or ""
        declared = row.get("share")
        if not isinstance(declared, int):
            continue
        count = sum(1 for q in questions
                    if (q.get("objective") or "").startswith(prefix))
        share = observed_share(count, total)
        if not within_tolerance(share, declared, tolerance):
            findings.append(blueprint_finding(
                "blueprint.domain_weight_out_of_tolerance", "block", "BANK",
                {"domain": row.get("domain"), "observed_share": share,
                 "declared_share": declared, "tolerance": tolerance,
                 "observed_items": count, "total_items": total},
                "adjust the set until %s carries %d percent plus or minus %d"
                % (row.get("domain"), declared, tolerance)))
    return findings


def _difficulty_findings(questions, bp):
    """Field 5, difficulty: the permitted bands, then the band shares.

    Two separate codes on purpose. A question in a band the form does not
    permit at all is a different defect from a band that appears too often, and
    one code for both would report a single number for two problems that need
    two different fixes.
    """
    findings = []
    block = bp.get("difficulty") or {}
    permitted = list(block.get("permitted_bands") or ())
    if permitted:
        for q in questions:
            if q.get("difficulty") not in permitted:
                findings.append(blueprint_finding(
                    "blueprint.difficulty_out_of_band", "block",
                    q.get("id") or "",
                    {"observed_band": q.get("difficulty"),
                     "permitted": permitted},
                    "rewrite this item at a permitted difficulty band, or "
                    "record a blueprint version that permits this band"))
    tolerance = block.get("tolerance") or 0
    total = len(questions)
    for row in block.get("shares") or ():
        band = row.get("band")
        declared = row.get("share")
        if not isinstance(declared, int):
            continue
        count = sum(1 for q in questions if q.get("difficulty") == band)
        share = observed_share(count, total)
        if not within_tolerance(share, declared, tolerance):
            findings.append(blueprint_finding(
                "blueprint.difficulty_share_out_of_tolerance", "block", "BANK",
                {"band": band, "observed_share": share,
                 "declared_share": declared, "tolerance": tolerance,
                 "observed_items": count, "total_items": total},
                "adjust the set until the %s band carries %d percent plus or "
                "minus %d" % (band, declared, tolerance)))
    return findings


def _demand_findings(questions, bp, facts):
    """Field 3, demand: a supplied fact per item, or one unverifiable finding.

    An item with no supplied fact contributes to the field's single
    unverifiable finding rather than to one finding per item. An unsupplied
    fact is one gap in the operator's inputs, not N gaps in the draft.
    """
    block = bp.get("demand") or {}
    supplied = {q.get("id"): (facts.get(q.get("item_id")) or {}).get("demand")
                for q in questions}
    known = {qid: value for qid, value in supplied.items() if value}
    if not known:
        return [_unverifiable("demand",
                              "no demand fact was supplied for any item")]

    findings = []
    permitted = list(block.get("permitted") or ())
    tolerance = block.get("tolerance") or 0
    total = len(questions)
    for row in block.get("shares") or ():
        level = row.get("level")
        declared = row.get("share")
        if not isinstance(declared, int):
            continue
        count = sum(1 for value in known.values() if value == level)
        share = observed_share(count, total)
        if not within_tolerance(share, declared, tolerance):
            findings.append(blueprint_finding(
                "blueprint.demand_out_of_tolerance", "block", "BANK",
                {"level": level, "observed_share": share,
                 "declared_share": declared, "tolerance": tolerance,
                 "observed_items": count, "total_items": total},
                "adjust the set until the %s demand carries %d percent plus "
                "or minus %d" % (level, declared, tolerance)))
    if permitted:
        for qid, value in sorted(known.items()):
            if value not in permitted:
                findings.append(blueprint_finding(
                    "blueprint.demand_out_of_tolerance", "block", qid or "",
                    {"observed_demand": value, "permitted": permitted},
                    "rewrite this item at a permitted demand, or record a "
                    "blueprint version that permits this demand"))
    return findings


def _timing_findings(questions, bp, facts):
    """Field 6, timing: the summed total and each item, both against their own
    tolerance."""
    block = bp.get("timing") or {}
    supplied = {q.get("id"): (facts.get(q.get("item_id")) or {})
                .get("timing_seconds") for q in questions}
    known = {qid: value for qid, value in supplied.items()
             if isinstance(value, int)}
    if not known:
        return [_unverifiable(
            "timing", "no timing_seconds fact was supplied for any item")]

    findings = []
    tolerance = block.get("tolerance_seconds") or 0
    per_item = block.get("per_item_seconds")
    total_declared = block.get("total_seconds")
    if isinstance(total_declared, int):
        observed = sum(known.values())
        if not within_tolerance(observed, total_declared, tolerance):
            findings.append(blueprint_finding(
                "blueprint.timing_out_of_tolerance", "block", "BANK",
                {"observed_seconds": observed,
                 "declared_total_seconds": total_declared,
                 "tolerance_seconds": tolerance},
                "adjust the set until the summed time is within %d seconds "
                "of %d" % (tolerance, total_declared)))
    if isinstance(per_item, int):
        for qid, value in sorted(known.items()):
            if value > per_item + tolerance:
                findings.append(blueprint_finding(
                    "blueprint.timing_out_of_tolerance", "block", qid or "",
                    {"observed_seconds": value,
                     "declared_per_item_seconds": per_item,
                     "tolerance_seconds": tolerance},
                    "shorten this item to %d seconds or fewer, or record a "
                    "blueprint version with a longer per-item allowance"
                    % (per_item + tolerance)))
    return findings


def _tools_findings(questions, bp, facts):
    """Field 7, tools: every supplied tool must be permitted.

    An empty `permitted` array with an empty supplied list produces nothing: a
    form that permits no tools and an item that uses none agree.
    """
    block = bp.get("tools") or {}
    supplied = {q.get("id"): (facts.get(q.get("item_id")) or {}).get("tools")
                for q in questions}
    known = {qid: value for qid, value in supplied.items()
             if value is not None}
    if not known:
        return [_unverifiable("tools",
                              "no tools fact was supplied for any item")]

    findings = []
    permitted = list(block.get("permitted") or ())
    for qid, values in sorted(known.items()):
        for value in values or ():
            if value not in permitted:
                findings.append(blueprint_finding(
                    "blueprint.tools_not_permitted", "block", qid or "",
                    {"observed_tool": value, "permitted": permitted},
                    "remove the dependency on %s, or record a blueprint "
                    "version that permits it" % value))
    return findings


def _construct_findings(bp, facts):
    """Field 1, construct: the supplied statement against the declared one.

    Compared as exact ASCII after stripping. Not a similarity match: a
    construct that nearly matches is a construct the form does not measure,
    and deciding how near is near enough would be this module inventing an
    opinion about meaning.
    """
    declared = ((bp.get("construct") or {}).get("statement") or "").strip()
    supplied = (facts.get("SET") or {}).get("construct")
    if not supplied:
        return [_unverifiable("construct",
                              "no construct fact was supplied for this set")]
    if declared and supplied.strip() != declared:
        return [blueprint_finding(
            "blueprint.construct_mismatch", "block", "BANK",
            {"observed_construct": supplied.strip(),
             "declared_construct": declared},
            "state the set's construct in the blueprint's own words, or "
            "record a blueprint version whose construct matches")]
    return []


def _feedback_findings(bp, facts):
    """Field 8, feedback conditions: two named keys, compared key by key.

    One finding per differing key rather than one for the pair, so the
    evidence names which key differed and a reader is not left comparing two
    dicts by eye.
    """
    declared = bp.get("feedback_conditions") or {}
    supplied = (facts.get("SET") or {}).get("feedback_conditions")
    if not supplied:
        return [_unverifiable(
            "feedback_conditions",
            "no feedback_conditions fact was supplied for this set")]
    findings = []
    for key in ("disclosure", "retry"):
        want = declared.get(key)
        got = supplied.get(key) if isinstance(supplied, dict) else None
        if want and got != want:
            findings.append(blueprint_finding(
                "blueprint.feedback_conditions_mismatch", "block", "BANK",
                {"key": key, "observed_value": got, "declared_value": want},
                "set the form's %s to %r, or record a blueprint version "
                "whose %s matches" % (key, want, key)))
    return findings


def blueprint_gate(questions, blueprint_doc, item_facts=None):
    """Gate 4: the drafted set against the accepted blueprint.

    Returns findings sorted by `(item, code, canonical_json(evidence))`, the
    same three-part deterministic key `authoring.quality_gate` sorts by, so two
    runs over the same input produce byte-identical lists and findings that
    compare equal still have a specified order.

    With no blueprint, returns exactly one `blueprint.absent` finding at
    severity `warn` and blocks nothing. That is ACTIVITY-02's degraded clause
    working: the course presents practice, and only the exam-fidelity claim is
    withheld.

    Takes an already-validated blueprint dict as an argument and never reads
    the course sidecar, exactly as `auditor.coverage_report` takes an
    already-normalized document. That is what keeps this module pure and keeps
    the two write paths the only code that touches disk.
    """
    if not blueprint_doc:
        return [blueprint_finding(
            "blueprint.absent", "warn", "BANK", {"blueprint": None},
            "bind a cited, versioned blueprint to this course to make an "
            "exam-fidelity claim possible; practice is unaffected")]

    bp = blueprint_doc
    questions = list(questions or ())
    facts = item_facts or {}

    # The eight checks in BLUEPRINT_FIELDS order, which is ACTIVITY-02's own
    # order. The single `sorted` call below is the ONLY thing that decides
    # output order, so the order these run in never leaks into the result.
    #
    # Every per-question check is skipped when there are no questions. A share
    # has no denominator over an empty set, and reporting "0 percent observed
    # against 67 declared" would present a derived number as a measurement of
    # something that was never measured. The same reasoning GRAPH-03 applies to
    # an indeterminate progress claim applies here. Emptiness is a real defect
    # and it is caught once, by `format`'s item-count check, rather than
    # reported again by every share.
    findings = []
    findings.extend(_construct_findings(bp, facts))
    findings.extend(_format_findings(questions, bp))
    findings.extend(_feedback_findings(bp, facts))
    if questions:
        findings.extend(_domain_weight_findings(questions, bp))
        findings.extend(_demand_findings(questions, bp, facts))
        findings.extend(_difficulty_findings(questions, bp))
        findings.extend(_timing_findings(questions, bp, facts))
        findings.extend(_tools_findings(questions, bp, facts))
    return sorted(findings,
                  key=lambda f: (f["item"], f["code"],
                                 canonical_json(f["evidence"])))


def blueprint_gate_blocks(questions, blueprint_doc, item_facts=None):
    """True when any blueprint finding blocks. An absent blueprint and an
    unverifiable field are both `warn`, so neither blocks a write."""
    return any(f["severity"] == "block"
               for f in blueprint_gate(questions, blueprint_doc, item_facts))


def runtime_conformance(questions):
    """Gate 5: every drafted question scores its own key through the one
    scorer.

    This is a conformance smoke test, not a second scorer. It calls
    `runtime.score_response` with the answer derived from that question's own
    `runtime.canonical_key`, and a question whose recorded key does not score
    True is a question the runtime and the bank disagree about.

    A constructed-response question returns `None` from both functions, and
    that produces no finding at all. Not-yet-marked is not a failure, and
    treating it as one would make every `short` item a blocking defect.
    """
    findings = []
    for q in questions or ():
        key = runtime.canonical_key(q)
        if key is None:
            continue
        verdict = runtime.score_response(q, key)
        if verdict is None:
            continue
        if verdict is not True:
            findings.append(blueprint_finding(
                "blueprint.runtime_mismatch", "block", q.get("id") or "",
                {"canonical_key": key, "verdict": verdict},
                "the recorded key does not score correct through the one "
                "scorer; fix the key or the options before accepting"))
    return findings


def gate_result(step, passed, findings):
    """One gate's outcome, carrying exactly GATE_RESULT_KEYS."""
    if step not in GATE_STEPS:
        raise BlueprintError(
            "blueprint.invalid",
            "%s is not one of the five ACTIVITY-02 gates: %s"
            % (step, ", ".join(GATE_STEPS)))
    return {"step": step, "passed": bool(passed),
            "findings": list(findings or ())}


def fidelity_claim(gate_results):
    """True only when all five gates are present and all five passed.

    Reads a list of gate results and never the questions, the blueprint, or
    the proposal. If it re-derived any gate's verdict itself there would be two
    answers to whether a gate passed, and the claim could disagree with the
    report that recorded it.

    A missing gate is a False claim, not a partial one. Returning something
    truthy for four of five would let an exam-fidelity claim rest on an
    unfinished check, which is the exact thing ACTIVITY-02 forbids.
    """
    passed = {}
    for result in gate_results or ():
        if not isinstance(result, dict):
            return False
        step = result.get("step")
        if step in GATE_STEPS:
            passed[step] = result.get("passed") is True
    return all(passed.get(step) is True for step in GATE_STEPS)


# ---------------------------------------------------------------------------
# staleness (RELIABILITY-03)
# ---------------------------------------------------------------------------

# RELIABILITY-03's own four words, in the requirement's own order: "require a
# rebind, migrate, supersede, or retain review". Transcribed, not chosen, so
# the vocabulary and the requirement cannot drift apart. Comparison is exact
# ASCII with no case folding and no synonyms, and a fifth disposition is a
# change to the requirement rather than to this module.
#
# `retain` is not weaker than the other three. It is a recorded reviewer
# decision that the dependent stays as it is despite the change, and it clears
# the block exactly as the others do. A `retain` that did not clear the block
# would make the requirement's own fourth word unusable.
STALENESS_DISPOSITIONS = ("rebind", "migrate", "supersede", "retain")

REVIEWER_ROLE = "reviewer"

STALENESS_ROW_KEYS = ("object_id", "object_kind", "dependency_object_id",
                      "dependency_kind", "base_fingerprint",
                      "current_fingerprint", "stale")

DISPOSITION_KEYS = ("schema_version", "object_id", "dependency_object_id",
                    "disposition", "reviewer_role", "reviewer_name",
                    "rationale", "base_fingerprint", "current_fingerprint")


def classify_staleness(base_fingerprint, current_fingerprint):
    """Whether a dependent is stale, from two fingerprints and nothing else.

    Takes both fingerprints as arguments and computes neither. The caller reads
    the live one through `identity.object_fingerprint` at the moment of the
    check. If this function computed it, `blueprint.py` would need a file read
    and the structural ban that it never touches disk would be gone, and the
    recomputed-on-read discipline would become a promise instead of a property.

    An absent or empty fingerprint reads STALE. An unprovable freshness is not
    freshness, and reading an unknown as fresh would let a dependent whose base
    fingerprint was never recorded pass acceptance forever. That is the
    failure-open direction, and this is the only place the choice is made.

    Comparison is exact ASCII: no case folding, no stripping, no normalization.
    Both values come from one function that produces hex digests, so any
    transformation before comparing is an opportunity for two different digests
    to compare equal. A false stale costs a reviewer one look; a false fresh
    costs the guarantee.
    """
    if not base_fingerprint or not current_fingerprint:
        return True
    return base_fingerprint != current_fingerprint


def staleness_row(object_id, object_kind, dependency_object_id,
                  dependency_kind, base_fingerprint, current_fingerprint):
    """One dependent's staleness, carrying exactly STALENESS_ROW_KEYS.

    `stale` is derived here and is never stored anywhere durable. The only
    durable values are the two fingerprints; the verdict is recomputed every
    time it is needed, so a stored True cannot go quietly out of date and a
    stored False cannot quietly authorize.
    """
    return {"object_id": object_id,
            "object_kind": object_kind,
            "dependency_object_id": dependency_object_id,
            "dependency_kind": dependency_kind,
            "base_fingerprint": base_fingerprint or "",
            "current_fingerprint": current_fingerprint or "",
            "stale": classify_staleness(base_fingerprint,
                                        current_fingerprint)}


def staleness_report(dependents):
    """Every dependent's row, sorted by `(object_id, dependency_object_id)`.

    Sorted so two runs over the same input produce byte-identical output and a
    diff of two reports shows a real change rather than a reordering. Pure:
    reads no file, takes no lock, and consults no registry.
    """
    rows = [staleness_row(d.get("object_id"), d.get("object_kind"),
                          d.get("dependency_object_id"),
                          d.get("dependency_kind"),
                          d.get("base_fingerprint"),
                          d.get("current_fingerprint"))
            for d in (dependents or ())]
    return sorted(rows, key=lambda r: (r["object_id"] or "",
                                       r["dependency_object_id"] or ""))


def disposition_record(object_id, dependency_object_id, disposition,
                       reviewer_role, reviewer_name, rationale,
                       base_fingerprint, current_fingerprint):
    """One reviewer decision about one stale dependent.

    Raises rather than returning an invalid record. A disposition record is the
    thing that unblocks an acceptance, so a malformed one must not exist at
    all: returning a record with an empty rationale and letting a later check
    catch it would leave a window in which the record looks like authority.

    Carries the `current_fingerprint` it was recorded against, not only the
    base. That is what makes reconciliation per change: matching a disposition
    compares its recorded current fingerprint to the live one, so once the
    dependency moves again the recorded decision no longer matches. Recording
    only the base would let one reviewer decision clear every future change to
    the same dependency, forever.
    """
    if disposition not in STALENESS_DISPOSITIONS:
        raise BlueprintError(
            "blueprint.unknown_disposition",
            "%s is not one of the four staleness dispositions (%s); the "
            "vocabulary is RELIABILITY-03's own and is closed"
            % (disposition, ", ".join(STALENESS_DISPOSITIONS)))
    if reviewer_role != REVIEWER_ROLE:
        raise BlueprintError(
            "blueprint.disposition_reviewer_required",
            "a staleness disposition is recorded by a %s and this record "
            "names the role %r; RELIABILITY-03 gives the authority for "
            "rebinding to a reviewer" % (REVIEWER_ROLE, reviewer_role))
    if not (rationale or "").strip():
        raise BlueprintError(
            "blueprint.disposition_rationale_required",
            "a staleness disposition needs a stated rationale; a recorded "
            "decision with no reason is a decision nobody can review")
    return {"schema_version": BLUEPRINT_SCHEMA_VERSION,
            "object_id": object_id,
            "dependency_object_id": dependency_object_id,
            "disposition": disposition,
            "reviewer_role": reviewer_role,
            "reviewer_name": reviewer_name,
            "rationale": rationale,
            "base_fingerprint": base_fingerprint or "",
            "current_fingerprint": current_fingerprint or ""}


def acceptance_block(rows, dispositions):
    """Every stale dependent with no matching disposition, as refusals.

    Returns a list rather than raising, so a caller reporting three blocked
    dependents reports three rather than the first. Plan 15B-04's acceptance
    functions turn a non-empty list into a raised refusal, and nothing decides
    blocking twice.

    A disposition matches only when its `object_id`, its
    `dependency_object_id`, AND its recorded `current_fingerprint` all equal
    the row's. The fingerprint is the load-bearing part: a decision recorded
    against one version of a dependency does not clear a later change to it.
    A disposition whose fingerprint has moved on is reported as superseded,
    which is a different and more useful message than reporting no decision at
    all.
    """
    matched = {}
    for record in dispositions or ():
        key = (record.get("object_id"), record.get("dependency_object_id"))
        matched.setdefault(key, []).append(record)

    refusals = []
    for row in rows or ():
        if not row.get("stale"):
            continue
        key = (row.get("object_id"), row.get("dependency_object_id"))
        candidates = matched.get(key) or []
        current = row.get("current_fingerprint") or ""
        if any((r.get("current_fingerprint") or "") == current
               for r in candidates):
            continue
        if candidates:
            refusals.append({
                "code": "blueprint.disposition_superseded",
                "object_id": row.get("object_id"),
                "dependency_object_id": row.get("dependency_object_id"),
                "message":
                    "a %s disposition is recorded for this dependency, but "
                    "against fingerprint %r rather than the live %r; the "
                    "dependency changed again after the decision, so it needs "
                    "a fresh review"
                    % (candidates[0].get("disposition"),
                       candidates[0].get("current_fingerprint"), current)})
            continue
        refusals.append({
            "code": "blueprint.stale_dependent",
            "object_id": row.get("object_id"),
            "dependency_object_id": row.get("dependency_object_id"),
            "message":
                "this object depends on %s, which has changed since the "
                "dependent recorded fingerprint %r; acceptance is blocked "
                "until a reviewer records one of %s. A stale derivative is "
                "never rebuilt and accepted silently."
                % (row.get("dependency_object_id"),
                   row.get("base_fingerprint"),
                   ", ".join(STALENESS_DISPOSITIONS))})
    return sorted(refusals, key=lambda r: (r["object_id"] or "",
                                           r["dependency_object_id"] or "",
                                           r["code"]))
