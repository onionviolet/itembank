#!/usr/bin/env python3
"""The Phase 11 auditor domain: locator-faithful source normalization and
exact citation primitives (plan 11-01, expanded by plan 11-03).

This module is the service-layer home of the curriculum-audit half of the
closed authoring loop. It knows nothing about models, providers, writers or
surfaces (the evidence.py house pattern): it turns UTF-8 bytes into a
versioned normalized-document record whose spans carry exact locators and
verbatim text, and it defines the citation record shape every coverage claim
and authoring request must use (D-01, D-04).

Design rules from the phase contract:

- D-03/D-04: original source bytes are read once and never written. Every
  derived record carries the SHA-256 of the original bytes so staleness is
  detectable; normalization is a pure transform over bytes.
- A malformed UTF-8 decode is an explicit typed error, never a lossy
  replacement, so no derived artifact is produced for bytes that cannot be
  represented exactly (11-AI-SPEC section 4b: "Never silently truncate a
  cited objective").
- Citation records are exact: source id + fingerprint + span identity. A
  claim that cannot name an exact span cannot cite it (D-02).
- PDF/DOCX ingestion is a separate architectural gate with its own fixture
  corpus (plan 11-03, locator_fidelity_cases.py); the registry below
  contains only the first-class formats until that gate proves exact
  round-trips.
"""
import hashlib
import re

# The schema version of the normalized_document payload family, published by
# schemas/normalized_document.schema.json in plan 11-02. Every runtime record
# must carry this and every runtime record must equal the schema's
# x-itembank-version (11-VALIDATION.md, T-11-22 parity rule).
NORMALIZED_DOCUMENT_VERSION = 1

# The registered first-class source adapters: exact, locator-faithful
# formats only (D-03). Anything else resolves to an explicit
# unsupported/lossy result with no spans and no fabricated locator until a
# future adapter proves exact round-trips against the fixture corpus.
REGISTERED_ADAPTERS = ("markdown", "text")

# The maximum source size accepted by normalization (11-VALIDATION.md
# T-11-10: schema-bounded source size). 4 MiB of UTF-8 text is far beyond
# any syllabus or chapter while still bounding a hostile input.
MAX_SOURCE_BYTES = 4 * 1024 * 1024

# The maximum number of objective candidates one source may extract
# (T-11-10). A real syllabus has dozens, not thousands.
MAX_OBJECTIVE_CANDIDATES = 500

_HEADING_RE = re.compile(r"(?m)^(#{1,6})\s+(.*?)\s*$")
_LIST_ITEM_RE = re.compile(r"(?m)^\s*(?:[-*+]|\d+[.)])\s+(.*?)\s*$")
_SENTENCE_RE = re.compile(r"[^.!?\n]+[.!?]")


def source_fingerprint(raw_bytes):
    """The SHA-256 of the exact original bytes, hex (D-04). Every derived
    record carries this so a stale report is detectable by recomputation."""
    return hashlib.sha256(raw_bytes).hexdigest()


def _span_key(text):
    """The deterministic identity key of a span's verbatim text: the
    collapsed lowercase form, used for stable objective-candidate keys."""
    return re.sub(r"\s+", " ", text).strip().lower()


class SourceError(Exception):
    """A typed normalization failure (malformed UTF-8, oversize input, an
    unregistered adapter). Carries a machine-readable `code` and message; no
    derived artifact is produced."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def _decode_utf8(raw_bytes, source_id):
    try:
        return raw_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SourceError(
            "source.decode_failed",
            "source %s is not valid UTF-8 (byte offset %d); no derived "
            "artifact was produced" % (source_id, exc.start))


def _split_spans(text, kind):
    """Split normalized text into ordered spans with exact locators.

    Every span records a stable span id, a heading path when the span sits
    under a markdown heading, 1-based start/end line, 0-based start/end
    character offsets into the original text, and the exact verbatim text.
    Offsets are computed on the decoded string, so reconstructing every span
    from recorded offsets yields byte-for-byte-equivalent Unicode text
    (plan 11-03 fidelity requirement).

    Returns (spans, heading_path) where heading_path is the current heading
    stack as the walk proceeds -- the caller threads it across lines.
    """
    spans = []
    heading_path = []
    lines = text.split("\n")
    # The final element of split("\n") is the line terminator (empty when the
    # text ends with a newline), never a real blank line: per-line spans plus
    # newline joins reconstruct the text byte-for-byte.
    content_lines = lines[:-1] if lines else []
    offset = 0
    for lineno, line in enumerate(content_lines, start=1):
        line_len = len(line)
        stripped = line.strip()
        if not stripped:
            # Blank lines are real spans with empty verbatim so that
            # reconstructing every span in order with newline joins yields
            # byte-for-byte-equivalent text (11-03 fidelity requirement).
            spans.append({
                "span_id": "sp-%d" % len(spans),
                "kind": "blank",
                "locator": {
                    "heading_path": list(heading_path),
                    "start_line": lineno,
                    "end_line": lineno,
                    "start_char": offset,
                    "end_char": offset + line_len,
                },
                "verbatim": "",
            })
            offset += line_len + 1
            continue
        hm = _HEADING_RE.match(line)
        if hm:
            level = len(hm.group(1))
            heading = hm.group(2).strip()
            heading_path = heading_path[: level - 1] + [heading]
            spans.append({
                "span_id": "sp-%d" % len(spans),
                "kind": "heading",
                "locator": {
                    "heading_path": list(heading_path),
                    "start_line": lineno,
                    "end_line": lineno,
                    "start_char": offset,
                    "end_char": offset + line_len,
                },
                "verbatim": line,
                "objective_candidate": heading,
            })
        elif _LIST_ITEM_RE.match(line):
            text = _LIST_ITEM_RE.match(line).group(1)
            spans.append({
                "span_id": "sp-%d" % len(spans),
                "kind": "list",
                "locator": {
                    "heading_path": list(heading_path),
                    "start_line": lineno,
                    "end_line": lineno,
                    "start_char": offset,
                    "end_char": offset + line_len,
                },
                "verbatim": line,
                "objective_candidate": text,
            })
        else:
            # Body prose. Keep the whole line as one span; a body paragraph
            # spanning lines keeps its per-line spans so locators stay
            # exact and reproducible.
            spans.append({
                "span_id": "sp-%d" % len(spans),
                "kind": "body",
                "locator": {
                    "heading_path": list(heading_path),
                    "start_line": lineno,
                    "end_line": lineno,
                    "start_char": offset,
                    "end_char": offset + line_len,
                },
                "verbatim": line,
            })
        offset += line_len + 1
    return spans


_OBJECTIVE_KEY_RE = re.compile(
    r"^([A-Za-z0-9_.]+:[A-Za-z0-9_./-]+)\s*(?:[-\u2013\u2014:]\s*)?(.*)$")


def _objective_candidates(spans):
    """Deterministic candidate extraction that does not collapse to heading
    scraping (plan 11-03 AUDIT-01): headings, list entries, and declarative
    body sentences that state a learning outcome all become candidates,
    each retaining its exact originating span. A list entry that leads with
    an explicit `subject:path` key (the syllabus idiom) yields that key as
    the candidate key so bank `[OBJECTIVE:]` lines can match it exactly.
    Body sentences are detected at paragraph level -- consecutive body
    lines are joined, so a multi-line learning outcome is still a candidate;
    its originating span is the paragraph's first body span."""
    candidates = []
    seen = set()
    paragraph = []
    for span in spans:
        if span["kind"] == "heading":
            paragraph = _flush_paragraph(paragraph, candidates, seen)
            text = span["objective_candidate"]
            key = _span_key(text)
            _add_candidate(candidates, seen, key, span["span_id"], text)
        elif span["kind"] == "list":
            paragraph = _flush_paragraph(paragraph, candidates, seen)
            text = span["objective_candidate"]
            km = _OBJECTIVE_KEY_RE.match(text)
            key = km.group(1).lower() if km else _span_key(text)
            _add_candidate(candidates, seen, key, span["span_id"], text)
        else:
            paragraph.append(span)
    _flush_paragraph(paragraph, candidates, seen)
    return candidates


def _flush_paragraph(paragraph, candidates, seen):
    """Extract one candidate from a run of consecutive body spans (the first
    objective-stating sentence), then clear the run. Returns the cleared
    list."""
    if not paragraph:
        return paragraph
    text = " ".join(s["verbatim"].strip() for s in paragraph)
    for m in _SENTENCE_RE.finditer(text):
        sentence = m.group(0).strip()
        if _looks_like_objective(sentence):
            _add_candidate(candidates, seen, _span_key(sentence),
                           paragraph[0]["span_id"], sentence)
            break
    return []


def _add_candidate(candidates, seen, key, span_id, text):
    if not key or key in seen:
        return
    if len(candidates) >= MAX_OBJECTIVE_CANDIDATES:
        return
    seen.add(key)
    candidates.append({
        "key": key,
        "span_id": span_id,
        "text": text,
    })


_OBJECTIVE_HINT_RE = re.compile(
    r"\b(?:student|learner|candidate|participant|should|will be able|"
    r"must be able|demonstrate|identify|explain|describe|perform|"
    r"manage|assess|recognize|differentiate|prioritize|apply)\b",
    re.I)


def _looks_like_objective(sentence):
    """A body sentence is a candidate objective when it carries a learning-
    outcome marker (a subject or an action verb typical of outcome
    statements). Deterministic and conservative: an unmarked sentence is
    simply not a candidate; coverage never depends on this heuristic."""
    return bool(_OBJECTIVE_HINT_RE.search(sentence)) and len(sentence) >= 8


def normalize_source(raw_bytes, source_id, kind="markdown"):
    """Normalize UTF-8 source bytes into a versioned normalized-document
    record (D-01/D-04). `kind` selects a registered adapter; anything else
    raises SourceError with the explicit unsupported code. Pure transform:
    never touches the source file."""
    if kind not in REGISTERED_ADAPTERS:
        raise SourceError(
            "source.adapter_unregistered",
            "no registered adapter for kind %r; first-class kinds are %s; "
            "PDF/DOCX remain unsupported until the locator-fidelity gate "
            "proves exact round-trips" %
            (kind, ", ".join(REGISTERED_ADAPTERS)))
    if len(raw_bytes) > MAX_SOURCE_BYTES:
        raise SourceError(
            "source.oversize",
            "source %s is %d bytes, over the %d-byte normalization cap"
            % (source_id, len(raw_bytes), MAX_SOURCE_BYTES))
    text = _decode_utf8(raw_bytes, source_id)
    spans = _split_spans(text, kind)
    candidates = _objective_candidates(spans)
    return {
        "schema_version": NORMALIZED_DOCUMENT_VERSION,
        "source_id": source_id,
        "kind": kind,
        "fingerprint": source_fingerprint(raw_bytes),
        "byte_length": len(raw_bytes),
        "spans": spans,
        "objective_candidates": candidates,
    }


def citation(source_id, fingerprint, span_id):
    """The exact citation record every coverage claim and authoring request
    uses (D-01/D-02): source identity, the source's byte fingerprint, and
    the exact span within it. A citation that cannot name all three is not
    a citation."""
    return {
        "source_id": source_id,
        "fingerprint": fingerprint,
        "span_id": span_id,
    }


def citations_for_objective(normalized, objective_key):
    """Return every span whose candidate key equals `objective_key`, as
    exact citation records. Empty when the objective is not present: a gap
    or unknown result is the caller's to derive (plan 11-03 coverage)."""
    out = []
    for cand in normalized["objective_candidates"]:
        if cand["key"] == objective_key:
            out.append(citation(normalized["source_id"],
                                normalized["fingerprint"],
                                cand["span_id"]))
    return out


# ---------------------------------------------------------------------------
# citation-first coverage engine (plan 11-03, AUDIT-02/AUDIT-03)
# ---------------------------------------------------------------------------

REPORT_SCHEMA_VERSION = 1
TOOL_VERSION = "itembank-0.4.0"
AUTHORING_REQUEST_VERSION = 1
DEFAULT_PER_OBJECTIVE_CAP = 20


def _canonical_objective_key(text):
    """The canonical key equality used to match source candidates to bank
    objective fields: lowercased, whitespace collapsed (mirrors the source
    candidate key normalization)."""
    return re.sub(r"\s+", " ", text).strip().lower()


def _span_ids(normalized):
    return {s["span_id"] for s in normalized["spans"]}


def _valid_source_citations(normalized, cites):
    """A citation side is valid only when every record is non-empty and
    exactly matches the current normalized document (source id, byte
    fingerprint, and an existing span id) -- D-02/D-04. Empty or null is
    invalid; a mismatched fingerprint is invalid; a fabricated span id is
    invalid. Confidence never upgrades an invalid side."""
    if not cites:
        return False
    span_ids = _span_ids(normalized)
    for c in cites:
        if not isinstance(c, dict):
            return False
        if (c.get("source_id") != normalized["source_id"] or
                c.get("fingerprint") != normalized["fingerprint"] or
                c.get("span_id") not in span_ids):
            return False
    return True


def _bank_fingerprint_current(rows, current_bank_fingerprint):
    """A bank-fingerprint assertion is valid only when it equals the current
    bank fingerprint; an absent assertion is accepted (the caller vouches
    for the bank by passing the parsed questions)."""
    for row in rows:
        asserted = row.get("bank_fingerprint")
        if asserted is not None and asserted != current_bank_fingerprint:
            return False
    return True


def coverage_report(normalized, questions, bank_fingerprint=None,
                    evidence=None, tool_version=TOOL_VERSION):
    """The deterministic citation-first coverage transform (AUDIT-02/AUDIT-03,
    D-01/D-02/D-04).

    Pure function: a normalized document, the exact parsed bank questions,
    and optional evidence assertions in, a strict audit_report dict out --
    nothing is read or written. Every objective of the normalized source
    becomes a row; covered requires an exact current source citation AND an
    exact stable bank item id citation on every side. Empty/null/mismatched
    citations are unknown, never covered; a source-backed objective with no
    covering item is a gap; partial and conflicting stay distinct; a
    mismatched bank fingerprint marks the row stale.

    `evidence` is a list of rows: {"objective_key", "source_citations",
    "bank_item_ids", optional "bank_fingerprint"}. Rows are validated, never
    trusted: an id that does not exist in the parsed bank or does not carry
    the objective is invalid.
    """
    questions = questions or []
    evidence = evidence or []
    current_bank_fp = bank_fingerprint
    by_key = {}
    for q in questions:
        key = _canonical_objective_key(q.get("objective") or "")
        if key:
            by_key.setdefault(key, []).append(q)
    item_ids = {q.get("item_id") for q in questions if q.get("item_id")}

    evidence_by_key = {}
    for row in evidence:
        evidence_by_key.setdefault(row.get("objective_key"), []).append(row)

    keys = sorted(set(
        [c["key"] for c in normalized["objective_candidates"]] +
        list(evidence_by_key.keys())))
    rows = []
    for key in keys:
        rows.append(_coverage_row(
            key, normalized, by_key.get(key, []), item_ids,
            evidence_by_key.get(key, []), current_bank_fp))

    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "status": "coverage",
        "request_fingerprint": "",
        "coverage": rows,
        "stale": _evidence_stale(normalized, evidence, current_bank_fp),
        "bank_fingerprint": current_bank_fp or "",
        "source_fingerprints": [normalized["fingerprint"]],
        "tool_version": tool_version,
    }


def _coverage_row(key, normalized, bank_items, item_ids, ev_rows,
                  current_bank_fp):
    source_cites = citations_for_objective(normalized, key)
    bank_ids = [q.get("item_id") for q in bank_items if q.get("item_id")]
    # canonical objective match for the cited ids
    objective_of = {}
    for q in bank_items:
        if q.get("item_id"):
            objective_of[q["item_id"]] = q.get("objective") or ""

    if not ev_rows:
        # No explicit claim: the source backs the objective; the bank side is
        # whatever items actually carry it. Still citation-first: covered
        # needs both sides non-empty and current.
        if not source_cites:
            return _row(key, "unknown", [], [])
        if current_bank_fp is None:
            state = "unknown"  # no bank fingerprint to vouch currency
        elif not bank_ids:
            state = "gap"
        else:
            state = "covered"
        return _row(key, state, source_cites, sorted(bank_ids))

    # Explicit evidence rows: a valid claim needs a current exact source
    # citation AND resolvable exact bank item ids. An empty id list with a
    # valid source side is an explicit gap claim. One invalid side makes the
    # claim unknown; mixed validity is conflicting; all-valid with an
    # uncovered bank subset is partial (AUDIT-02/AUDIT-03).
    valid = []
    gap_claims = []
    invalid = []
    for row in ev_rows:
        src_ok = _valid_source_citations(normalized, row.get("source_citations"))
        ids = row.get("bank_item_ids") or []
        bank_ok = _bank_fingerprint_current([row], current_bank_fp) \
            if current_bank_fp else True
        if not src_ok or not bank_ok:
            invalid.append(row)
        elif not ids:
            gap_claims.append(row)
        elif all(i in item_ids and
                 _canonical_objective_key(objective_of.get(i)) == key
                 for i in ids):
            valid.append(row)
        else:
            invalid.append(row)

    if invalid:
        return _row(key, "unknown" if not (valid or gap_claims)
                    else "conflicting", [], [])
    if gap_claims and not valid:
        return _row(key, "gap", source_cites, [])
    if not valid:
        return _row(key, "unknown", [], [])
    cited = sorted({i for row in valid for i in (row.get("bank_item_ids") or [])})
    if not cited:
        return _row(key, "gap", source_cites, [])
    if set(bank_ids) - set(cited):
        return _row(key, "partial", source_cites, cited)
    return _row(key, "covered", source_cites, cited)


def _row(key, state, source_citations, bank_item_ids):
    return {
        "objective_key": key,
        "state": state,
        "source_citations": source_citations,
        "bank_item_ids": bank_item_ids,
    }


def _evidence_stale(normalized, evidence, current_bank_fp):
    """A report is stale when any evidence assertion carries a bank
    fingerprint that no longer matches the current bank, or a source
    fingerprint that no longer matches the current source (D-04). The rows
    themselves stay fail-closed (never covered); this flag makes the
    staleness explicit and recomputable."""
    for row in evidence:
        if not isinstance(row, dict):
            continue
        asserted = row.get("bank_fingerprint")
        if asserted is not None and asserted != current_bank_fp:
            return True
        for cite in row.get("source_citations") or []:
            if isinstance(cite, dict) and \
                    cite.get("fingerprint") != normalized["fingerprint"]:
                return True
    return False


def material_request(raw_bytes, source_id, kind, objectives, count,
                     item_types, retry_cap=3, mode="report_only",
                     per_objective_cap=DEFAULT_PER_OBJECTIVE_CAP):
    """The explicit AUDIT-04 bridge (D-18): accepting bytes for OBTAINED
    material is a separate operation that normalizes the new source and
    returns a NEW bounded authoring request preserving exact citations. It
    never calls the author or the writer -- a gap or material pointer can
    never authorize generation (AUDIT-04/T-11-08)."""
    normalized = normalize_source(raw_bytes, source_id, kind=kind)
    citations = []
    for objective in objectives:
        citations.extend(citations_for_objective(normalized, objective))
    if not citations:
        raise SourceError(
            "material.no_citations",
            "none of the requested objectives %s appears in the obtained "
            "material %s; no request was created" % (objectives, source_id))
    return {
        "schema_version": AUTHORING_REQUEST_VERSION,
        "objectives": list(objectives),
        "count": count,
        "item_types": list(item_types),
        "citations": citations,
        "retry_cap": retry_cap,
        "mode": mode,
        "per_objective_cap": per_objective_cap,
        "source_fingerprints": [normalized["fingerprint"]],
    }


def apply_weak_priority(objective_keys, weak_signals):
    """Phase 10 weak-objective signals only reorder objective ids already
    present in the normalized source (D-19): unknown ids are reported and
    ignored, never added to curriculum. Returns (ordered_keys,
    unknown_signals)."""
    keys = list(objective_keys)
    known = set(keys)
    ordered = []
    unknown = []
    for signal in weak_signals:
        if signal in known:
            if signal not in ordered:
                ordered.append(signal)
        else:
            unknown.append(signal)
    for key in keys:
        if key not in ordered:
            ordered.append(key)
    return ordered, unknown
