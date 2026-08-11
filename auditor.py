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
    unregistered adapter). Carries a machine-readable code and message; no
    derived artifact is produced."""


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
    offset = 0
    for lineno, line in enumerate(lines, start=1):
        line_len = len(line)
        stripped = line.strip()
        if not stripped:
            offset += line_len + 1  # +1 for the newline split consumed
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
        elif _LIST_ITEM_RE.match(line) and kind != "text":
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
    the candidate key so bank `[OBJECTIVE:]` lines can match it exactly."""
    candidates = []
    seen = set()
    for span in spans:
        if span["kind"] == "heading":
            text = span["objective_candidate"]
            key = _span_key(text)
        elif span["kind"] == "list":
            text = span["objective_candidate"]
            km = _OBJECTIVE_KEY_RE.match(text)
            key = km.group(1).lower() if km else _span_key(text)
        else:
            text = ""
            for m in _SENTENCE_RE.finditer(span["verbatim"]):
                sentence = m.group(0).strip()
                if _looks_like_objective(sentence):
                    text = sentence
                    break
            if not text:
                continue
            key = _span_key(text)
        if not key or key in seen:
            continue
        seen.add(key)
        candidates.append({
            "key": key,
            "span_id": span["span_id"],
            "text": text,
        })
        if len(candidates) >= MAX_OBJECTIVE_CANDIDATES:
            break
    return candidates


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
