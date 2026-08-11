#!/usr/bin/env python3
"""The Phase 11 closed authoring loop: bounded, repository-blind generation
through both quality gates to a single writer handoff (plan 11-01; retry
state machine and autonomy modes completed by plan 11-04).

One orchestration shape performs the whole D-05 loop:

    run_authoring(request, author_callable, bank_text, writer, config)

- `request` is a bounded authoring request (exact objectives, count, item
  types, and source citations -- D-07/AUTH-02). Anything the model returns
  outside those bounds is rejected before lint and before any writer call.
- `author_callable` is provider-neutral and repository-blind (AUTH-03): it
  receives only the public format contract (`model.SPEC`), the serialized
  bounded request, the attempt number, and versioned structured findings
  (D-06). No repository paths, bank contents beyond the scoped request, or
  module access ever cross this boundary.
- `bank_text` is the exact current bank text; the candidate bank is
  composed in memory, ids assigned with `model.assign_ids`, parsed with
  `model.parse_bank`, linted with `model.lint`, and run through the four
  deterministic quality detectors -- all before the writer is invoked.
- `writer` is the one mutation seam (`audit_writer.write_units` in
  production): it accepts only an immutable preflighted proposal plus the
  expected bank fingerprint and rechecks under its own lock.

The second quality gate (AUDIT-07/D-09/D-10) is a separate, versioned
`quality_gate()` result with exactly four independently named detectors:
answer-position skew, near-duplicate stems, answer leak, and distractor-
rationale completeness. Each emits its own record with measured evidence --
never an aggregate score (D-10, 11-RESEARCH "Do not combine detector scores
into one opaque score").
"""
import difflib
import hashlib
import json
import os
import re

import model

# The schema version of the authoring_request payload family, published by
# schemas/authoring_request.schema.json in plan 11-02.
AUTHORING_SCHEMA_VERSION = 1
# The schema version of the quality_finding payload family (plan 11-02).
QUALITY_SCHEMA_VERSION = 1
# The schema version of the write_manifest payload family (plan 11-02).
WRITE_SCHEMA_VERSION = 1
# The schema version of the audit_report payload family (plan 11-02).
REPORT_SCHEMA_VERSION = 1

# The public tool identity recorded in every report/manifest (D-17). Mirrors
# itembank.__version__ without importing the CLI shim into the domain layer.
TOOL_VERSION = "itembank-0.3.0"

# Schema-bounded caps (T-11-04, T-11-14): a request may ask for at most
# this many items, retries, and per-objective items. The bounds live here so
# the request schema and the runtime agree on one number set.
MAX_ITEMS_PER_REQUEST = 20
MAX_RETRY_CAP = 10
MAX_ITEMS_PER_OBJECTIVE = 20

# The four-detector quality profile (11-RESEARCH "Second Quality Gate").
# Versions bump only when a detector's rule changes; findings carry the
# version that produced them (D-09).
DETECTOR_VERSIONS = {
    "answer_skew": 1,
    "near_duplicate_stems": 1,
    "answer_leak": 1,
    "distractor_rationale": 1,
}

# The permission modes (D-12): report_only never mutates a bank;
# draft_and_approve requires exact write-id acceptance per unit; full is
# explicit opt-in with caps. The model can never select or change the mode.
MODES = ("report_only", "draft_and_approve", "full")

# The documented fixed stopword set for the near-duplicate detector (plan
# 11-04 Task 1: "remove a documented fixed stopword set"). English function
# words that carry no stem identity; the set is deliberately small and fixed
# so a score is reproducible forever.
STOPWORDS = frozenset(
    "a an the and or but if then else of to in on at for with from by as "
    "is are was were be been being it its this that these those which who "
    "whom whose what when where why how not no do does did done can could "
    "will would shall should may might must have has had having about into "
    "over under between out up down off than so too very just".split())

# The thresholds (11-RESEARCH): skew blocks only above 40% at 12+ MC items
# (equality passes, matching the live lint precedent); near duplicates block
# at Jaccard >= 0.85 with at least six tokens in each stem; answer leak
# blocks a unique contiguous run of at least three normalized content
# tokens; distractor rationale requires a "would be correct" condition.
SKEW_MIN_ITEMS = 12
SKEW_BLOCK_ABOVE = 0.40
JACCARD_BLOCK_AT = 0.85
JACCARD_MIN_TOKENS = 6
LEAK_MIN_RUN = 3


# ---------------------------------------------------------------------------
# request validation
# ---------------------------------------------------------------------------

def validate_request(request):
    """Validate the bounded authoring request shape. Returns a list of
    machine-readable scope findings; empty means the request is well formed.
    This is the schema-level gate; plan 11-02 publishes the strict JSON
    Schema and plan 11-04 wires schema_validate in. The bounds are enforced
    here regardless so a malformed request can never reach the callable."""
    findings = []
    if not isinstance(request, dict):
        return [{"code": "request.not_object", "message": "request must be a JSON object"}]
    if request.get("schema_version") != AUTHORING_SCHEMA_VERSION:
        findings.append({
            "code": "request.schema_version",
            "message": "request schema_version must be %d" % AUTHORING_SCHEMA_VERSION})
    objectives = request.get("objectives")
    if not isinstance(objectives, list) or not objectives:
        findings.append({"code": "request.objectives",
                         "message": "request needs a non-empty objectives list"})
    elif not all(isinstance(o, str) and o.strip() for o in objectives):
        findings.append({"code": "request.objective_invalid",
                         "message": "every objective must be a non-empty string"})
    count = request.get("count")
    if not isinstance(count, int) or isinstance(count, bool) or not 1 <= count <= MAX_ITEMS_PER_REQUEST:
        findings.append({"code": "request.count",
                         "message": "count must be an integer in 1..%d" % MAX_ITEMS_PER_REQUEST})
    types = request.get("item_types")
    if not isinstance(types, list) or not types:
        findings.append({"code": "request.item_types",
                         "message": "request needs a non-empty item_types list"})
    elif not all(t in ("mc", "multi", "table", "build", "dnd", "short")
                 for t in types):
        findings.append({"code": "request.item_type_invalid",
                         "message": "item_types may contain only mc/multi/table/build/dnd/short"})
    citations = request.get("citations")
    if not isinstance(citations, list) or not citations:
        findings.append({"code": "request.citations",
                         "message": "request needs a non-empty citations list"})
    else:
        for i, c in enumerate(citations):
            if not isinstance(c, dict) or not (c.get("source_id") and
                                               c.get("fingerprint") and
                                               c.get("span_id")):
                findings.append({"code": "request.citation_invalid",
                                 "message": "citation %d needs source_id, fingerprint and span_id" % i})
    retry_cap = request.get("retry_cap", 3)
    if not isinstance(retry_cap, int) or isinstance(retry_cap, bool) or \
            not 1 <= retry_cap <= MAX_RETRY_CAP:
        findings.append({"code": "request.retry_cap",
                         "message": "retry_cap must be an integer in 1..%d" % MAX_RETRY_CAP})
    mode = request.get("mode", "report_only")
    if mode not in ("report_only", "draft_and_approve", "full"):
        findings.append({"code": "request.mode",
                         "message": "mode must be report_only, draft_and_approve or full"})
    per_objective = request.get("per_objective_cap", MAX_ITEMS_PER_OBJECTIVE)
    if not isinstance(per_objective, int) or isinstance(per_objective, bool) or \
            not 1 <= per_objective <= MAX_ITEMS_PER_OBJECTIVE:
        findings.append({"code": "request.per_objective_cap",
                         "message": "per_objective_cap must be an integer in 1..%d"
                         % MAX_ITEMS_PER_OBJECTIVE})
    return findings


# ---------------------------------------------------------------------------
# fingerprints and deterministic identity
# ---------------------------------------------------------------------------

def canonical_json(obj):
    """Deterministic UTF-8 JSON serialization for fingerprints (D-17):
    sorted keys, no whitespace, non-ASCII preserved."""
    return json.dumps(obj, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"))


def bank_fingerprint(text):
    """The change-detection fingerprint of the exact bank text bytes, used
    as the writer's expected-fingerprint guard (D-17/T-11-02)."""
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def request_fingerprint(request):
    """The identity of the bounded request, independent of attempt state."""
    return "sha256:" + hashlib.sha256(
        canonical_json(request).encode("utf-8")).hexdigest()


def run_identity(request, bank_before_fingerprint, source_fingerprints, config):
    """The deterministic run identity (plan 11-04 AUTH-01 stateful review):
    same request + bank-before + source + profile + tool version => same run
    id, so a duplicate invocation returns the existing result instead of
    duplicating curriculum."""
    parts = [
        request_fingerprint(request),
        bank_before_fingerprint,
        "|".join(sorted(source_fingerprints)),
        str((config or {}).get("profile", "")),
        (config or {}).get("tool_version", TOOL_VERSION),
    ]
    return "sha256:" + hashlib.sha256(
        ("\x1f".join(parts)).encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# response scope validation (AUTH-02 / D-07)
# ---------------------------------------------------------------------------

def _validate_response_shape(response):
    """The response envelope must be a JSON object with the right schema
    version and an `items` array. Anything else is a malformed response
    (plan 11-04: empty/null response is malformed)."""
    if not isinstance(response, dict):
        return [{"code": "scope.response_not_object",
                 "message": "author response must be a JSON object"}]
    if response.get("schema_version") != AUTHORING_SCHEMA_VERSION:
        return [{"code": "scope.response_schema_version",
                 "message": "author response schema_version must be %d"
                 % AUTHORING_SCHEMA_VERSION}]
    items = response.get("items")
    if not isinstance(items, list):
        return [{"code": "scope.response_items",
                 "message": "author response needs an items array"}]
    return []


def _citation_in_request(citation, request_citations):
    """Exact citation membership (AUTH-02): the response item's citation
    must match one request citation field-for-field."""
    for rc in request_citations:
        if (citation.get("source_id") == rc.get("source_id") and
                citation.get("fingerprint") == rc.get("fingerprint") and
                citation.get("span_id") == rc.get("span_id")):
            return True
    return False


def validate_response_scope(request, response):
    """Scope validation precedes lint on every attempt (D-07/AUTH-02): the
    exact requested count, allowed item types, requested objectives, and
    request citation membership. Every response item must also parse into
    exactly one question block. Returns structured scope findings; empty
    means the response is in scope."""
    findings = _validate_response_shape(response)
    if findings:
        return findings
    items = response["items"]
    count = request["count"]
    objectives = set(request["objectives"])
    types = set(request["item_types"])
    citations = request["citations"]
    if len(items) != count:
        return [{"code": "scope.count",
                 "message": "requested %d item(s), author returned %d"
                 % (count, len(items))}]
    for i, item in enumerate(items):
        tag = "item[%d]" % i
        if not isinstance(item, dict):
            findings.append({"code": "scope.item_not_object",
                             "message": "%s is not an object" % tag})
            continue
        if item.get("type") not in types:
            findings.append({
                "code": "scope.item_type",
                "item": tag,
                "message": "item type %r is outside the requested item_types %s"
                % (item.get("type"), sorted(types))})
        if item.get("objective") not in objectives:
            findings.append({
                "code": "scope.objective",
                "item": tag,
                "message": "objective %r is outside the requested objectives %s"
                % (item.get("objective"), sorted(objectives))})
        item_citations = item.get("citations") or []
        if not item_citations or not all(
                isinstance(c, dict) and _citation_in_request(c, citations)
                for c in item_citations):
            findings.append({
                "code": "scope.citation",
                "item": tag,
                "message": "item citations must all be exact members of the "
                           "request citation set"})
        text = item.get("text")
        if not isinstance(text, str) or not text.strip():
            findings.append({"code": "scope.item_text",
                             "item": tag,
                             "message": "item has no text block"})
        else:
            parsed = model.parse_bank(_normalize_item_block(text))
            if len(parsed) != 1:
                findings.append({
                    "code": "scope.item_unparseable",
                    "item": tag,
                    "message": "item text must parse into exactly one question "
                               "block, got %d" % len(parsed)})
            elif (parsed[0]["type"] != item.get("type") or
                    parsed[0].get("objective") != item.get("objective")):
                findings.append({
                    "code": "scope.item_mismatch",
                    "item": tag,
                    "message": "parsed item type/objective disagree with the "
                               "declared values"})
    return findings


# ---------------------------------------------------------------------------
# candidate composition
# ---------------------------------------------------------------------------

_QUESTION_MARKER_RE = re.compile(r"(?m)^Q(\d+)\.\s")


def _renumber_questions(text):
    """Renumber every question block sequentially Q1..Qn in document order,
    preserving every other byte. The repository-blind author never learns
    the bank's current numbering, so the composed candidate is renumbered
    deterministically; an already-sequential bank is byte-identical after
    this transform (which the diff proves)."""
    blocks = []
    starts = [m.start() for m in _QUESTION_MARKER_RE.finditer(text)]
    if not starts:
        return text
    for i, start in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else len(text)
        blocks.append(text[start:end])
    out = []
    for i, block in enumerate(blocks, start=1):
        out.append(_QUESTION_MARKER_RE.sub("Q%d. " % i, block, count=1))
    return "".join(out)


def _normalize_item_block(text):
    """The canonical item block form: a Qn.-prefixed markdown block. The
    repository-blind author may emit a block without a number (it cannot
    know the bank's current numbering); the pipeline prefixes a placeholder
    and renumbers the full candidate deterministically."""
    block = text.rstrip("\n")
    if not re.match(r"(?m)^Q\d+\.\s", block):
        block = "Q1. " + block.lstrip()
    return block


def compose_candidate(bank_text, response):
    """Compose the full candidate bank text: current bank plus every response
    item block, renumbered, ids assigned with the existing public function.
    Pure in-memory transform -- nothing is written here (D-08)."""
    item_blocks = []
    for item in response["items"]:
        item_blocks.append(_normalize_item_block(item["text"]))
    combined = bank_text.rstrip("\n") + "\n\n" + "\n\n".join(item_blocks) + "\n"
    combined = _renumber_questions(combined)
    new_text, changes = model.assign_ids(combined)
    return new_text, changes


# ---------------------------------------------------------------------------
# the four-detector quality gate (AUDIT-07)
# ---------------------------------------------------------------------------

def _tokens(text):
    """Normalize text to content tokens: lowercase, punctuation stripped,
    stopwords removed (the documented fixed STOPWORDS set)."""
    words = re.findall(r"[A-Za-z0-9']+", text.lower())
    return [w for w in words if w not in STOPWORDS]


def _quality_finding(detector, severity, code, item, evidence, remediation):
    return {
        "schema_version": QUALITY_SCHEMA_VERSION,
        "detector": detector,
        "detector_version": DETECTOR_VERSIONS[detector],
        "severity": severity,
        "code": code,
        "item": item,
        "evidence": evidence,
        "threshold": None,
        "remediation": remediation,
    }


def detect_answer_skew(questions):
    """Answer-position skew: evaluated over the proposed full bank; inactive
    below 12 MC items; blocks only when one keyed position is above 40%
    (equality at 40% passes -- the live lint precedent, preserved)."""
    hits = {}
    for q in questions:
        if q["type"] == "mc" and q.get("correct"):
            hits[q["correct"][0]] = hits.get(q["correct"][0], 0) + 1
    total = sum(hits.values())
    if total < SKEW_MIN_ITEMS:
        return []
    letter, n = max(sorted(hits.items()), key=lambda kv: kv[1])
    share = n / total
    if share <= SKEW_BLOCK_ABOVE:
        return []
    return [_quality_finding(
        "answer_skew", "block", "quality.answer_skew", "BANK",
        {"total_mc": total, "per_letter_counts": hits,
         "max_position": letter, "max_share": round(share, 4),
         "min_items": SKEW_MIN_ITEMS, "block_above": SKEW_BLOCK_ABOVE},
        "one keyed position (%s) exceeds 40%% of %d multiple-choice items; "
        "rebalance the correct-answer positions" % (letter, total))]


def detect_near_duplicates(questions):
    """Near-duplicate stems: normalized non-stopword token Jaccard at or
    above 0.85 blocks only when both stems have at least six tokens. Every
    finding reports the compared item ids, sets, intersection, union and
    score (explainable evidence, never an aggregate)."""
    findings = []
    tokenized = []
    for q in questions:
        item_id = q.get("item_id") or q["id"]
        toks = _tokens(q["stem"])
        tokenized.append((item_id, set(toks), q["id"]))
    for i in range(len(tokenized)):
        for j in range(i + 1, len(tokenized)):
            a_id, a_set, a_num = tokenized[i]
            b_id, b_set, b_num = tokenized[j]
            if len(a_set) < JACCARD_MIN_TOKENS or len(b_set) < JACCARD_MIN_TOKENS:
                continue
            inter = a_set & b_set
            union = a_set | b_set
            if not union:
                continue
            score = len(inter) / len(union)
            if score >= JACCARD_BLOCK_AT:
                # Normalize the pair so the lower item id is always "a":
                # the finding must not depend on input iteration order.
                if b_id < a_id:
                    a_id, b_id = b_id, a_id
                    a_set, b_set = b_set, a_set
                    a_num, b_num = b_num, a_num
                inter = a_set & b_set
                union = a_set | b_set
                findings.append(_quality_finding(
                    "near_duplicate_stems", "block", "quality.near_duplicate_stems",
                    "%s/%s" % (a_num, b_num),
                    {"item_a": a_id, "item_b": b_id,
                     "tokens_a": sorted(a_set), "tokens_b": sorted(b_set),
                     "intersection": sorted(inter), "union": sorted(union),
                     "score": round(score, 4),
                     "min_tokens": JACCARD_MIN_TOKENS,
                     "block_at": JACCARD_BLOCK_AT},
                    "stems are near-duplicates (Jaccard %.2f >= %.2f with %d+ "
                    "tokens each); rewrite one stem around a different "
                    "distinction" % (score, JACCARD_BLOCK_AT, JACCARD_MIN_TOKENS)))
    return findings


def detect_answer_leak(questions):
    """Answer leak: a correct option contributes a contiguous run of at
    least three normalized content tokens to the stem, and no incorrect
    option carries that same run. Reports the run, the correct option, and
    the competing-option comparison."""
    findings = []
    for q in questions:
        if q["type"] != "mc":
            continue
        stem_toks = _tokens(q["stem"])
        for letter in sorted(q["correct"]):
            opt_toks = _tokens(q["opts"][letter])
            for run in _contiguous_runs(opt_toks, LEAK_MIN_RUN):
                if not _is_subsequence(run, stem_toks):
                    continue
                competitors = [l for l in sorted(q["opts"])
                               if l not in q["correct"]
                               and _is_subsequence(run, _tokens(q["opts"][l]))]
                if not competitors:
                    findings.append(_quality_finding(
                        "answer_leak", "block", "quality.answer_leak", q["id"],
                        {"run": list(run), "correct_option": letter,
                         "competing_options_with_run": competitors,
                         "min_run": LEAK_MIN_RUN},
                        "the correct option %s leaks a %d-token phrase "
                        "(%r) into the stem with no distractor sharing it; "
                        "rephrase the stem" % (letter, LEAK_MIN_RUN, " ".join(run))))
    return findings


def _contiguous_runs(tokens, min_run):
    """Every contiguous token window of length >= min_run, deduplicated, in
    first-seen order. A run is a sequence of adjacent tokens in the option's
    own token list; the leak check then asks whether that exact run also
    appears contiguously in the stem."""
    runs = []
    seen = set()
    n = len(tokens)
    for length in range(min_run, n + 1):
        for k in range(0, n - length + 1):
            window = tuple(tokens[k:k + length])
            if window not in seen:
                seen.add(window)
                runs.append(window)
    return runs


def _is_subsequence(run, tokens):
    """True when `run` appears as a contiguous slice of `tokens`."""
    run_len = len(run)
    for k in range(0, len(tokens) - run_len + 1):
        if tuple(tokens[k:k + run_len]) == run:
            return True
    return False


def detect_distractor_rationale(questions):
    """Distractor-rationale completeness: every non-correct MC option's
    rationale must exist and state the condition under which it would be
    correct. Promotes the lint-observable missing-rationale / missing-
    would-be-condition checks into an independent named quality finding
    (plan 11-04 Task 1) without duplicating parser/identity logic."""
    findings = []
    for q in questions:
        if q["type"] != "mc":
            continue
        for letter in sorted(q["opts"]):
            if letter in q["correct"]:
                continue
            line = (q.get("da") or {}).get(letter) or ""
            if not line:
                findings.append(_quality_finding(
                    "distractor_rationale", "block",
                    "quality.distractor_rationale", q["id"],
                    {"option": letter, "rationale_present": False,
                     "would_be_condition": False},
                    "distractor %s has no DISTRACTOR ANALYSIS line; state "
                    "when it would be correct" % letter))
            elif not model.WOULD_BE.search(line):
                findings.append(_quality_finding(
                    "distractor_rationale", "block",
                    "quality.distractor_rationale", q["id"],
                    {"option": letter, "rationale_present": True,
                     "would_be_condition": False},
                    "distractor %s never says when it WOULD be correct"
                    % letter))
    return findings


def quality_gate(questions, profile=None):
    """Run all four named detectors over the complete proposed bank and
    return versioned findings sorted deterministically by (item, detector,
    evidence key). Never an aggregate score; each contributing detector
    keeps its own record (D-10). `profile` is reserved for plan 11-04's
    configurable severities; evidence is never erased by a profile."""
    findings = (
        detect_answer_skew(questions) +
        detect_near_duplicates(questions) +
        detect_answer_leak(questions) +
        detect_distractor_rationale(questions))
    return sorted(findings,
                  key=lambda f: (f["item"], f["detector"],
                                 canonical_json(f["evidence"])))


def quality_gate_blocks(questions):
    """True when any detector produced a blocking finding. The gate never
    mutates ids, objectives, questions, or content fingerprints (plan 11-04
    assertion)."""
    return any(f["severity"] == "block" for f in quality_gate(questions))


# ---------------------------------------------------------------------------
# structured findings for the retry loop
# ---------------------------------------------------------------------------

def _scope_findings_payload(findings):
    return {"schema_version": 1, "kind": "scope", "records": findings}


def _lint_findings_payload(errors, warnings):
    return {"schema_version": 1, "kind": "lint",
            "records": [e._asdict() for e in errors] +
                       [w._asdict() for w in warnings]}


def _quality_findings_payload(findings):
    return {"schema_version": 1, "kind": "quality", "records": findings}


def _callable_payload(request, attempt, findings):
    """The only payload the repository-blind author ever receives (D-06,
    AUTH-03): the public format contract, the bounded request, the attempt
    number, and versioned structured findings. Nothing else -- no bank text,
    no repository paths, no modules. Findings are copied so the payload is
    immutable against later pipeline state changes."""
    return {
        "schema_version": 1,
        "contract": model.SPEC,
        "request": request,
        "attempt": attempt,
        "findings": list(findings),
    }


# ---------------------------------------------------------------------------
# the diff and proposal (D-17)
# ---------------------------------------------------------------------------

def make_diff(before_text, after_text):
    """A reproducible unified diff of the proposed bank change."""
    return "".join(difflib.unified_diff(
        before_text.splitlines(keepends=True),
        after_text.splitlines(keepends=True),
        fromfile="bank-before", tofile="bank-after"))


def build_proposal(request, bank_text, candidate_text, source_fingerprints,
                   config, lint_errors, lint_warnings, quality_findings,
                   changes, run_id):
    """The immutable preflighted proposal: everything the writer needs plus
    every provenance field D-17 requires. Built only after all gates pass.
    Units are the requested new items (the candidate questions beyond the
    existing bank), regardless of whether their ids were minted or kept."""
    before_fp = bank_fingerprint(bank_text)
    after_fp = bank_fingerprint(candidate_text)
    questions = model.parse_bank(candidate_text)
    before_count = len(model.parse_bank(bank_text))
    new_questions = questions[before_count:]
    units = []
    for q in new_questions:
        item_id = q.get("item_id") or ""
        if not item_id:
            continue
        units.append({"unit_id": item_id, "item_id": item_id,
                      "objective": q.get("objective", ""),
                      "tag": q["id"]})
    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "run_id": run_id,
        "request_fingerprint": request_fingerprint(request),
        "bank_before_fingerprint": before_fp,
        "bank_after_fingerprint": after_fp,
        "source_fingerprints": sorted(source_fingerprints),
        "profile": (config or {}).get("profile", ""),
        "tool_version": (config or {}).get("tool_version", TOOL_VERSION),
        "units": units,
        "diff": make_diff(bank_text, candidate_text),
        "bank_after_text": candidate_text,
        "gates": {
            "lint_errors": [e._asdict() for e in lint_errors],
            "lint_warnings": [w._asdict() for w in lint_warnings],
            "quality_findings": quality_findings,
        },
        "item_count": len(questions),
    }


# ---------------------------------------------------------------------------
# the orchestration pipeline
# ---------------------------------------------------------------------------

def _report(request, **fields):
    base = {"schema_version": REPORT_SCHEMA_VERSION,
            "request_fingerprint": request_fingerprint(request)}
    base.update(fields)
    return base


def run_authoring(request, author_callable, bank_text, writer, config=None):
    """The one orchestration command (D-05): bounded request -> repository-
    blind author -> scope -> lint -> quality -> full-candidate preflight ->
    permission decision -> writer, with structured retry findings and an
    explicit retained report on exhaustion (D-08). Returns a machine-
    readable report dict with volume accounting on every exit (D-13/AUDIT-09);
    raises AuthoringError only on programming-contract violations (a bad
    request shape), never on model or writer outcomes.

    `config` may carry: target_path (the bank path the writer mutates),
    state_dir (the writer's manifest/before-image directory), profile,
    blocking_warnings (lint warning codes that block, default none),
    writer_args, full_opt_in (the explicit opt-in for full autonomy, D-13),
    caps ({per_run, per_objective} bounded volumes, D-13), and
    approved_write_ids (the exact write-id acceptance set for
    draft_and_approve, D-12). The mode itself lives only in the request and
    can never be changed by model output or a prior run.
    """
    config = config or {}
    request_errors = validate_request(request)
    if request_errors:
        raise AuthoringError("invalid authoring request: %s"
                             % request_errors[0]["message"])
    source_fingerprints = sorted({c["fingerprint"]
                                  for c in request["citations"]})
    before_fp = bank_fingerprint(bank_text)
    run_id = run_identity(request, before_fp, source_fingerprints, config)
    mode = request.get("mode", "report_only")
    retry_cap = request.get("retry_cap", 3)
    blocking_warnings = set(config.get("blocking_warnings") or [])
    target_path = config.get("target_path")
    state_dir = config.get("state_dir")

    # AUTH-01 duplicate-run idempotency: the same request+bank+profile has
    # the same run id; if it already completed (manifest present and still
    # matching), return the existing result without generating again.
    if target_path and state_dir:
        existing = _find_completed_run(run_id, target_path, state_dir)
        if existing is not None:
            return _report(request, status="already_completed",
                           run_id=run_id, mode=mode, manifest=existing,
                           **volume_record(request, written=0,
                                           completed=len(existing.get("units") or [])))

    # draft_and_approve resumes its pending proposal by run id (AUTH-01
    # interruption/resume contract): an approval invocation with the same
    # request+bank must act on the previously prepared proposal, never
    # regenerate with new random unit ids.
    if mode == "draft_and_approve" and state_dir and \
            (config.get("approved_write_ids") or []):
        pending = _load_pending(run_id, state_dir)
        if pending is not None:
            if pending.get("bank_before_fingerprint") != before_fp:
                return _report(
                    request, status="refused", run_id=run_id, mode=mode,
                    outcome="stale_pending", write_allowed=False,
                    message="the pending proposal predates a bank change; "
                            "re-run the request to prepare a fresh proposal",
                    **volume_record(request, proposal=pending))
            return _finalize(request, pending, writer, config, run_id,
                             mode, 0, [])

    # D-13/D-14: full autonomy is an explicit, model-inaccessible opt-in
    # with bounded proposed volume, enforced BEFORE any generation.
    if mode == "full":
        refusal = _full_autonomy_gate(request, config)
        if refusal is not None:
            return refusal

    findings_chain = []
    attempts = 0
    final_response = None
    for attempt in range(1, retry_cap + 1):
        attempts = attempt
        payload = _callable_payload(request, attempt, findings_chain)
        response = author_callable(payload)

        scope_findings = validate_response_scope(request, response)
        if scope_findings:
            findings_chain.append(_scope_findings_payload(scope_findings))
            continue

        candidate_text, changes = compose_candidate(bank_text, response)
        questions = model.parse_bank(candidate_text)
        lint_errors, lint_warnings = model.lint(questions)
        blocking = [w for w in lint_warnings
                    if w.code in blocking_warnings]
        if lint_errors or blocking:
            findings_chain.append(_lint_findings_payload(
                lint_errors, lint_warnings))
            continue

        quality_findings = quality_gate(questions)
        if any(f["severity"] == "block" for f in quality_findings):
            findings_chain.append(_quality_findings_payload(quality_findings))
            continue

        final_response = response
        break

    if final_response is None:
        # D-08: exhausted retries (or a final failing attempt) retain the
        # complete draft and reasons; no writer call ever happens. A clean
        # prefix of a dirty batch is never written (all-or-nothing).
        rejected = _rejected_units(response)
        return _report(
            request, status="failed", run_id=run_id, mode=mode,
            attempts=attempts, outcome="retry_cap_exhausted",
            findings=findings_chain,
            retained_draft=response if response is not None else None,
            write_allowed=False,
            **volume_record(request, attempts=attempts, rejected=rejected))

    candidate_text, changes = compose_candidate(bank_text, final_response)
    questions = model.parse_bank(candidate_text)
    lint_errors, lint_warnings = model.lint(questions)
    quality_findings = quality_gate(questions)
    # Recheck immediately before the writer boundary (AUTH-02 stateful
    # review): the compose step is deterministic, so this can only pass if
    # the earlier gates passed; the recheck exists so a future code change
    # cannot bypass scope/lint/quality.
    scope_findings = validate_response_scope(request, final_response)
    if scope_findings or lint_errors or any(
            f["severity"] == "block" for f in quality_findings):
        rejected = _rejected_units(final_response)
        return _report(
            request, status="failed", run_id=run_id, mode=mode,
            outcome="preflight_recheck_failed",
            findings=(findings_chain +
                      [_scope_findings_payload(scope_findings)] if scope_findings
                      else findings_chain),
            retained_draft=final_response, write_allowed=False,
            **volume_record(request, attempts=attempts, rejected=rejected))

    proposal = build_proposal(request, bank_text, candidate_text,
                              source_fingerprints, config, lint_errors,
                              lint_warnings, quality_findings, changes,
                              run_id)
    return _finalize(request, proposal, writer, config, run_id, mode,
                     attempts, findings_chain)


def _full_autonomy_gate(request, config):
    """The explicit full-autonomy gate (D-13/AUDIT-09), enforced before any
    generation: explicit opt-in and bounded proposed volume. Returns a
    refusal report or None to proceed."""
    caps = config.get("caps") or {}
    per_run = caps.get("per_run") or MAX_ITEMS_PER_REQUEST
    per_objective = caps.get("per_objective") or \
        request.get("per_objective_cap", MAX_ITEMS_PER_OBJECTIVE)
    if not config.get("full_opt_in"):
        return _report(
            request, status="refused", mode="full",
            outcome="opt_in_required", write_allowed=False,
            message="full autonomy requires explicit opt-in "
                    "(config.full_opt_in); the model cannot select it",
            **volume_record(request, proposed=request["count"]))
    if request["count"] > per_run:
        return _report(
            request, status="refused", mode="full",
            outcome="cap_exceeded", write_allowed=False,
            message="requested %d items exceeds the per-run cap %d"
                    % (request["count"], per_run),
            **volume_record(request, proposed=request["count"]))
    if per_objective < 1:
        return _report(
            request, status="refused", mode="full",
            outcome="cap_exceeded", write_allowed=False,
            message="per-objective cap must be at least 1",
            **volume_record(request, proposed=request["count"]))
    return None


def _finalize(request, proposal, writer, config, run_id, mode, attempts,
              findings_chain):
    """The final domain permission decision over the validated proposal
    (D-12..D-14): all three modes share byte-equivalent gate/diff evidence
    and differ only at this decision. Returns the run report."""
    unit_ids = sorted(u["unit_id"] for u in proposal["units"])
    target_path = config.get("target_path")
    state_dir = config.get("state_dir")

    if mode == "report_only":
        return _report(request, status="proposed", run_id=run_id, mode=mode,
                       proposal=proposal, write_allowed=False,
                       **volume_record(request, proposal=proposal))

    if mode == "draft_and_approve":
        approved = sorted(config.get("approved_write_ids") or [])
        if not approved:
            if state_dir:
                _save_pending(run_id, proposal, state_dir)
            return _report(request, status="awaiting_approval", run_id=run_id,
                           mode=mode, proposal=proposal, write_allowed=False,
                           pending_write_ids=unit_ids,
                           **volume_record(request, proposal=proposal))
        if approved != unit_ids:
            return _report(
                request, status="refused", run_id=run_id, mode=mode,
                outcome="approval_mismatch", proposal=proposal,
                write_allowed=False, pending_write_ids=unit_ids,
                message="approval must name exactly the proposed write ids "
                        "%s, got %s" % (unit_ids, approved),
                **volume_record(request, proposal=proposal))
        return _write_proposal(request, proposal, writer, config, run_id,
                               mode, attempts)

    if mode == "full":
        return _write_proposal(request, proposal, writer, config, run_id,
                               mode, attempts)

    return _report(request, status="refused", run_id=run_id, mode=mode,
                   outcome="mode_unknown", write_allowed=False,
                   **volume_record(request, proposal=proposal))


def _write_proposal(request, proposal, writer, config, run_id, mode,
                    attempts):
    """Invoke the writer with the immutable proposal and expected bank
    fingerprint (AUTH-02 stateful review). A writer failure (stale preflight,
    interruption, duplicate conflict) is an explicit failed report with the
    retained proposal -- never a false completion without a matching writer
    result (AUTH-01)."""
    target_path = config.get("target_path")
    state_dir = config.get("state_dir")
    if not target_path or not state_dir:
        raise AuthoringError("mode %s requires config.target_path and "
                             "config.state_dir" % mode)
    before_fp = proposal["bank_before_fingerprint"]
    try:
        manifest = writer(proposal, target_path, state_dir,
                          expected_fingerprint=before_fp,
                          **(config.get("writer_args") or {}))
    except Exception as exc:  # the typed writer boundary is the one place
        # that may fail; surface it as an explicit failed report with the
        # writer's machine-readable code (stale_preflight, duplicate_conflict,
        # interruption), never as a false completion.
        code = getattr(exc, "code", "writer_failed")
        return _report(
            request, status="failed", run_id=run_id, mode=mode,
            outcome="writer_" + code, proposal=proposal,
            retained_draft=None, write_allowed=False,
            message=str(exc),
            **volume_record(request, proposal=proposal, attempts=attempts))
    written = len(manifest.get("units") or proposal.get("units") or [])
    return _report(request, status="written", run_id=run_id, mode=mode,
                   proposal=proposal, manifest=manifest, write_allowed=True,
                   **volume_record(request, proposal=proposal,
                                   attempts=attempts,
                                   written=written, completed=written))


def volume_record(request, proposal=None, attempts=0, rejected=0,
                  written=0, completed=None, proposed=None):
    """The D-13/AUDIT-09 volume accounting emitted on every exit: proposed,
    completed, rejected, retried, and written units, plus a per-objective
    breakdown. `completed` defaults to `written`; `proposed` defaults to the
    proposal item count or the request count."""
    total = proposed if proposed is not None else (
        len((proposal or {}).get("units") or [])
        if proposal else request.get("count", 0))
    completed = completed if completed is not None else written
    retried = max(0, attempts - 1)
    per_objective = {}
    for obj in request.get("objectives", []):
        per_objective[obj] = {
            "proposed": 0, "completed": 0, "rejected": 0,
            "retried": retried, "written": 0,
        }
    if proposal:
        for unit in proposal.get("units", []):
            obj = unit.get("objective") or ""
            bucket = per_objective.setdefault(obj, {
                "proposed": 0, "completed": 0, "rejected": 0,
                "retried": retried, "written": 0,
            })
            bucket["proposed"] += 1
            bucket["completed"] += 1 if completed else 0
            bucket["written"] += 1 if written else 0
    return {
        "proposed_volume": total,
        "completed_volume": completed,
        "rejected_volume": rejected,
        "retried_volume": retried,
        "written_volume": written,
        "per_objective_volume": per_objective,
    }


def _rejected_units(response):
    """The number of units a failing response carried (used as the rejected
    volume on exhaustion/recheck failure)."""
    if isinstance(response, dict):
        items = response.get("items")
        if isinstance(items, list):
            return len(items)
    return 0



def _find_completed_run(run_id, target_path, state_dir):
    """The writer-side idempotency probe: a manifest for this run whose
    write is applied and whose after-fingerprint still matches the target
    returns the existing manifest (AUTH-01); anything else returns None."""
    try:
        import audit_writer
    except ImportError:
        return None
    return audit_writer.find_applied_manifest(run_id, target_path, state_dir)


PENDING_DIRNAME = "pending"


def _save_pending(run_id, proposal, state_dir):
    """Durably record the prepared-but-unapproved proposal so an approval
    invocation can resume it without regenerating (AUTH-01 interruption
    contract). Atomic tmp-then-replace, same convention as the writer."""
    pending_dir = os.path.join(state_dir, PENDING_DIRNAME)
    os.makedirs(pending_dir, exist_ok=True)
    path = os.path.join(pending_dir, run_id + ".json")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(proposal, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    os.replace(tmp, path)


def _load_pending(run_id, state_dir):
    """Read a pending proposal for this run id, or None."""
    if not state_dir:
        return None
    path = os.path.join(state_dir, PENDING_DIRNAME, run_id + ".json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


class AuthoringError(Exception):
    """A programming-contract violation in the authoring pipeline (a bad
    request shape, missing writer config for full mode). Never raised for a
    model or writer outcome, which are always returned as reports."""
