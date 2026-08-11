#!/usr/bin/env python3
"""Standalone fidelity, state-boundary, and read-only audit suite for the
Phase 11 curriculum auditor (plan 11-03, AUDIT-01..AUDIT-04).

Run:
    python tests/audit_coverage_roundtrip.py --case normalize
    python tests/audit_coverage_roundtrip.py --case coverage
    python tests/audit_coverage_roundtrip.py --case material
    python tests/audit_coverage_roundtrip.py            (all cases)

Stdlib only, no packages, no live model, and no mutation of committed
fixtures: source bytes are read, PDF/DOCX fixtures are materialized into a
temporary directory, and every normalization/coverage result is a pure
transform.
"""
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import auditor
import authoring
import model

FIXTURES = os.path.join(ROOT, "fixtures", "audit")


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def read_bytes(path):
    with open(path, "rb") as fh:
        return fh.read()


def read_text(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def fixture(name):
    return os.path.join(FIXTURES, name)


# ---------------------------------------------------------------------------
# case: normalize (plan 11-03 Task 1, AUDIT-01)
# ---------------------------------------------------------------------------

def case_normalize():
    workdir = tempfile.mkdtemp(prefix="audit-normalize-")
    try:
        # --- deterministic Markdown normalization with exact spans --------
        raw_md = read_bytes(fixture("syllabus.md"))
        doc1 = auditor.normalize_source(raw_md, source_id="syllabus.md",
                                        kind="markdown")
        doc2 = auditor.normalize_source(raw_md, source_id="syllabus.md",
                                        kind="markdown")
        if json.dumps(doc1, ensure_ascii=False, sort_keys=True) != \
                json.dumps(doc2, ensure_ascii=False, sort_keys=True):
            fail("normalize: repeated normalization must be byte-identical")

        if doc1["fingerprint"] != auditor.source_fingerprint(raw_md):
            fail("normalize: fingerprint must be SHA-256 of the exact bytes")
        if doc1["schema_version"] != 1:
            fail("normalize: schema_version must be 1")

        # --- fidelity: spans reconstruct the exact text --------------------
        text = raw_md.decode("utf-8")
        for span in doc1["spans"]:
            loc = span["locator"]
            if text[loc["start_char"]:loc["end_char"]] != span["verbatim"]:
                fail("normalize: span %s does not reconstruct from offsets"
                     % span["span_id"])
            if loc["end_line"] < loc["start_line"] or \
                    loc["start_char"] < 0 or loc["end_char"] < loc["start_char"]:
                fail("normalize: span %s has an inconsistent locator"
                     % span["span_id"])
        joined = "\n".join(s["verbatim"] for s in doc1["spans"])
        expected = text[:-1] if text.endswith("\n") else text
        if joined != expected:
            fail("normalize: joining spans does not reproduce the source "
                 "text byte-for-byte")

        # --- heading/list/body objective candidates (AUDIT-01) -------------
        keys = {c["key"] for c in doc1["objective_candidates"]}
        for expected in ("emt:airway.opa", "emt:airway.adjunct",
                         "emt:airway.ventilation"):
            if expected not in keys:
                fail("normalize: list objective %r not extracted" % expected)
        body_keys = [c for c in doc1["objective_candidates"]
                     if "prioritize airway management" in c["key"]]
        if not body_keys:
            fail("normalize: body-level objective must be a candidate "
                 "(not heading scraping)")
        span_ids = {s["span_id"] for s in doc1["spans"]}
        for cand in doc1["objective_candidates"]:
            if cand["span_id"] not in span_ids:
                fail("normalize: candidate %r cites a missing span"
                     % cand["key"])

        # --- text (non-markdown) adapter -----------------------------------
        raw_txt = read_bytes(fixture("syllabus.txt"))
        doc_txt = auditor.normalize_source(raw_txt, source_id="syllabus.txt",
                                           kind="text")
        if doc_txt["kind"] != "text":
            fail("normalize: text adapter must report kind text")
        txt_keys = {c["key"] for c in doc_txt["objective_candidates"]}
        if "emt:airway.opa" not in txt_keys:
            fail("normalize: text list objective not extracted")
        if not any("suctioning precedes ventilation" in k
                   for k in txt_keys):
            fail("normalize: text body objective not extracted")

        # --- malformed UTF-8 fails explicitly ------------------------------
        try:
            auditor.normalize_source(b"\xff\xfe\x00bad", "bad",
                                     kind="text")
            fail("normalize: invalid UTF-8 must fail explicitly")
        except auditor.SourceError as exc:
            if exc.code != "source.decode_failed":
                fail("normalize: wrong decode-failure code %r" % exc.code)

        # --- unregistered adapters fail explicitly (D-03) ------------------
        for kind in ("pdf", "docx"):
            try:
                auditor.normalize_source(raw_md, "x", kind=kind)
                fail("normalize: %s adapter must be unregistered" % kind)
            except auditor.SourceError as exc:
                if exc.code != "source.adapter_unregistered":
                    fail("normalize: wrong unregistered code %r" % exc.code)

        # --- oversize input fails explicitly --------------------------------
        try:
            auditor.normalize_source(b"x" * (auditor.MAX_SOURCE_BYTES + 1),
                                     "big", kind="text")
            fail("normalize: oversize source must fail")
        except auditor.SourceError as exc:
            if exc.code != "source.oversize":
                fail("normalize: wrong oversize code %r" % exc.code)

        # --- PDF/DOCX architectural gate (T-11-27) -------------------------
        sys.path.insert(0, FIXTURES)
        import locator_fidelity_cases as gate
        records = gate.materialize(os.path.join(workdir, "fixtures"))
        if len(records) != len(gate.CASE_TABLE):
            fail("normalize: gate must materialize every case")
        for case in gate.CASE_TABLE:
            rec = [r for r in records if r[0] == case["id"]][0]
            path = rec[1]
            raw = read_bytes(path)
            if gate.sha256(raw) != case["gold"]["sha256"]:
                fail("normalize: fixture %s drifted from its gold sha256"
                     % case["id"])
            if "structures" not in case["gold"] or \
                    "reading_order" not in case["gold"] or \
                    "unsupported" not in case["gold"]:
                fail("normalize: fixture %s gold manifest incomplete"
                     % case["id"])
            if case["gold"]["expectation"] != "unsupported_now":
                fail("normalize: fixture %s expectation changed" % case["id"])
            st_before = os.stat(path)
            first = second = None
            for _ in range(2):
                try:
                    auditor.normalize_source(raw, source_id=case["id"],
                                             kind=case["kind"])
                    fail("normalize: %s must return explicit unsupported"
                         % case["id"])
                except auditor.SourceError as exc:
                    if exc.code != "source.adapter_unregistered":
                        fail("normalize: %s wrong unsupported code %r"
                             % (case["id"], exc.code))
                    if first is None:
                        first = (exc.code, str(exc))
                    else:
                        second = (exc.code, str(exc))
            if first != second:
                fail("normalize: %s repeated unsupported result must be "
                     "byte-stable" % case["id"])
            st_after = os.stat(path)
            if read_bytes(path) != raw or st_after.st_mtime_ns != \
                    st_before.st_mtime_ns:
                fail("normalize: %s source bytes/timestamp changed"
                     % case["id"])
        print("OK: normalize -- deterministic Markdown/text spans, "
              "heading/list/body objectives, invalid-UTF-8 and oversize "
              "failures, 18-case PDF/DOCX gate with stable unsupported "
              "results and unchanged bytes")
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


# ---------------------------------------------------------------------------
# case: coverage (plan 11-03 Task 2, AUDIT-02/AUDIT-03)
# ---------------------------------------------------------------------------

def _bank_state():
    bank_text = read_text(fixture("coverage_bank.md"))
    questions = model.parse_bank(bank_text)
    if len(questions) != 3:
        fail("coverage: fixture bank must parse into 3 items")
    return bank_text, questions


def _syllabus():
    raw = read_bytes(fixture("syllabus.md"))
    return auditor.normalize_source(raw, source_id="syllabus.md",
                                    kind="markdown")


def _ids_for(questions, objective):
    return sorted(q["item_id"] for q in questions
                  if q.get("objective") == objective)


def _row(report, key):
    for r in report["coverage"]:
        if r["objective_key"] == key:
            return r
    fail("coverage: no row for %r" % key)


def case_coverage():
    bank_text, questions = _bank_state()
    normalized = _syllabus()
    bank_fp = authoring.bank_fingerprint(bank_text)
    opa_ids = _ids_for(questions, "emt:airway.opa")
    adjunct_ids = _ids_for(questions, "emt:airway.adjunct")

    report = auditor.coverage_report(normalized, questions,
                                     bank_fingerprint=bank_fp)
    rows = {r["objective_key"]: r for r in report["coverage"]}

    # --- states from the fixture (no evidence) -----------------------------
    if rows["emt:airway.opa"]["state"] != "covered":
        fail("coverage: emt:airway.opa must be covered (2 bank items)")
    if sorted(rows["emt:airway.opa"]["bank_item_ids"]) != opa_ids:
        fail("coverage: opa row must cite both bank item ids")
    if rows["emt:airway.adjunct"]["state"] != "covered":
        fail("coverage: emt:airway.adjunct must be covered")
    if rows["emt:airway.ventilation"]["state"] != "gap":
        fail("coverage: emt:airway.ventilation must be a gap (no bank item)")
    if not rows["emt:airway.ventilation"]["source_citations"]:
        fail("coverage: a gap row must carry the exact source citations")
    body_key = [k for k in rows if "prioritize airway management" in k]
    if not body_key or rows[body_key[0]]["state"] != "gap":
        fail("coverage: body objective with no bank item must be a gap")

    # every source citation on a covered row is exact and current
    for r in report["coverage"]:
        if r["state"] == "covered":
            for c in r["source_citations"]:
                if c["source_id"] != "syllabus.md" or \
                        c["fingerprint"] != normalized["fingerprint"] or \
                        c["span_id"] not in {s["span_id"]
                                             for s in normalized["spans"]}:
                    fail("coverage: covered row carries an inexact citation")

    # --- report provenance and determinism (D-04/D-17) ---------------------
    if report["bank_fingerprint"] != bank_fp or \
            report["source_fingerprints"] != [normalized["fingerprint"]]:
        fail("coverage: report must record both input fingerprints")
    if report["stale"] is not False:
        fail("coverage: a fresh report must not be stale")
    again = auditor.coverage_report(normalized, questions,
                                    bank_fingerprint=bank_fp)
    if json.dumps(report, ensure_ascii=False, sort_keys=True) != \
            json.dumps(again, ensure_ascii=False, sort_keys=True):
        fail("coverage: repeated computation must be byte-identical")

    # --- the report validates against the strict schema --------------------
    import resources
    import schema_validate as sv
    schema = json.loads(resources.read_text(
        "schemas/audit_report.schema.json"))
    errs = sv.validate(report, schema)
    if errs:
        fail("coverage: report fails the audit_report schema: %s" % errs[:3])

    # --- fail-closed state boundaries (AUDIT-03) ---------------------------
    def ev(key, cites, ids, **extra):
        row = {"objective_key": key, "source_citations": cites,
               "bank_item_ids": ids}
        row.update(extra)
        return row

    bad_span = {"source_id": "syllabus.md",
                "fingerprint": normalized["fingerprint"],
                "span_id": "sp-does-not-exist"}
    wrong_fp = {"source_id": "syllabus.md",
                "fingerprint": "a" * 64,
                "span_id": _row(auditor.coverage_report(
                    normalized, questions, bank_fingerprint=bank_fp),
                    "emt:airway.opa")["source_citations"][0]["span_id"]}

    unknown_cases = [
        ("empty citations", ev("emt:airway.opa", [], opa_ids)),
        ("null citations", ev("emt:airway.opa", None, opa_ids)),
        ("nonexistent span", ev("emt:airway.opa", [bad_span], opa_ids)),
        ("wrong fingerprint", ev("emt:airway.opa", [wrong_fp], opa_ids)),
        ("unresolvable ids", ev("emt:airway.opa",
                                _row(auditor.coverage_report(
                                    normalized, questions,
                                    bank_fingerprint=bank_fp),
                                    "emt:airway.opa")["source_citations"],
                                ["no-such-item"])),
    ]
    for label, evidence in unknown_cases:
        rep = auditor.coverage_report(normalized, questions,
                                      bank_fingerprint=bank_fp,
                                      evidence=[evidence])
        if _row(rep, "emt:airway.opa")["state"] != "unknown":
            fail("coverage: %s must yield unknown" % label)

    # confidence never upgrades an uncited claim
    confident = ev("emt:airway.opa", [],
                   ["no-such-item"], confidence="high")
    rep = auditor.coverage_report(normalized, questions,
                                  bank_fingerprint=bank_fp,
                                  evidence=[confident])
    if _row(rep, "emt:airway.opa")["state"] != "unknown":
        fail("coverage: confidence must never upgrade an uncited claim")

    # explicit empty id list with valid source side is a gap claim
    gap_ev = ev("emt:airway.opa",
                _row(auditor.coverage_report(normalized, questions,
                                             bank_fingerprint=bank_fp),
                     "emt:airway.opa")["source_citations"], [])
    rep = auditor.coverage_report(normalized, questions,
                                  bank_fingerprint=bank_fp,
                                  evidence=[gap_ev])
    if _row(rep, "emt:airway.opa")["state"] != "gap":
        fail("coverage: empty cited id list with valid source is a gap")

    # valid singleton on each side can be covered (adjunct has one item)
    adjunct_row = _row(auditor.coverage_report(normalized, questions,
                                               bank_fingerprint=bank_fp),
                       "emt:airway.adjunct")
    singleton = ev("emt:airway.adjunct",
                   adjunct_row["source_citations"][:1],
                   adjunct_row["bank_item_ids"][:1])
    rep = auditor.coverage_report(normalized, questions,
                                  bank_fingerprint=bank_fp,
                                  evidence=[singleton])
    if _row(rep, "emt:airway.adjunct")["state"] != "covered":
        fail("coverage: a valid singleton on each side can be covered")

    # partial: citing a subset of the covering items
    partial = ev("emt:airway.opa",
                 _row(auditor.coverage_report(normalized, questions,
                                              bank_fingerprint=bank_fp),
                      "emt:airway.opa")["source_citations"], opa_ids[:1])
    rep = auditor.coverage_report(normalized, questions,
                                  bank_fingerprint=bank_fp,
                                  evidence=[partial])
    if _row(rep, "emt:airway.opa")["state"] != "partial":
        fail("coverage: citing a subset of covering items must be partial")

    # conflicting: a valid claim and a contradictory invalid claim (same key)
    opa_valid = ev("emt:airway.opa",
                   _row(auditor.coverage_report(normalized, questions,
                                                bank_fingerprint=bank_fp),
                        "emt:airway.opa")["source_citations"], opa_ids)
    conflicting = [opa_valid, ev("emt:airway.opa", [bad_span], opa_ids)]
    rep = auditor.coverage_report(normalized, questions,
                                  bank_fingerprint=bank_fp,
                                  evidence=conflicting)
    if _row(rep, "emt:airway.opa")["state"] != "conflicting":
        fail("coverage: mixed valid/invalid claims must be conflicting")

    # --- deterministic under reordered input -------------------------------
    import random
    shuffled = list(questions)
    rng = random.Random(7)
    rng.shuffle(shuffled)
    shuffled_ev = list(conflicting)
    rng.shuffle(shuffled_ev)
    rep_a = auditor.coverage_report(normalized, questions,
                                    bank_fingerprint=bank_fp,
                                    evidence=conflicting)
    rep_b = auditor.coverage_report(normalized, shuffled,
                                    bank_fingerprint=bank_fp,
                                    evidence=shuffled_ev)
    if authoring.canonical_json(rep_a) != authoring.canonical_json(rep_b):
        fail("coverage: reordered questions/evidence must serialize "
             "identically")

    # --- stale fingerprints: never covered, report marks stale -------------
    stale_ev = ev("emt:airway.opa",
                  _row(auditor.coverage_report(normalized, questions,
                                               bank_fingerprint=bank_fp),
                       "emt:airway.opa")["source_citations"], opa_ids,
                  bank_fingerprint="sha256:" + "0" * 64)
    rep = auditor.coverage_report(normalized, questions,
                                  bank_fingerprint=bank_fp,
                                  evidence=[stale_ev])
    if _row(rep, "emt:airway.opa")["state"] == "covered":
        fail("coverage: a stale bank fingerprint must never be covered")
    if rep["stale"] is not True:
        fail("coverage: a stale fingerprint assertion must mark the report "
             "stale")

    # --- staleness recomputable from recorded fingerprints (D-04) ----------
    changed_bank = bank_text + "\n\nQ4. (new item) stem\n[OBJECTIVE: emt:airway.opa]\nA) x\nB) y\nC) z\nCORRECT: A\nWHY BEST: w\nKEY DISCRIMINATOR: d\nSECOND-BEST: s\nDISTRACTOR ANALYSIS:\n- B) b would be correct if c.\n- C) c would be correct if b.\n- D) d would be correct if a.\nTRAP: t\nCONFIDENCE: high\n"
    changed_bank, _ = model.assign_ids(changed_bank)
    new_fp = authoring.bank_fingerprint(changed_bank)
    rep_old = auditor.coverage_report(normalized, questions,
                                      bank_fingerprint=bank_fp)
    rep_new = auditor.coverage_report(normalized,
                                      model.parse_bank(changed_bank),
                                      bank_fingerprint=new_fp)
    if rep_old["bank_fingerprint"] == rep_new["bank_fingerprint"]:
        fail("coverage: changed bank must produce a different report "
             "fingerprint")
    if len(_row(rep_new, "emt:airway.opa")["bank_item_ids"]) != \
            len(_row(rep_old, "emt:airway.opa")["bank_item_ids"]) + 1:
        fail("coverage: recomputation must reflect the changed bank")

    print("OK: coverage -- all five states, fail-closed dual citations, "
          "confidence non-escalation, singleton/partial/conflicting, "
          "stale handling, deterministic ordering")
    return bank_fp


# ---------------------------------------------------------------------------
# case: material (plan 11-03 Task 3, AUDIT-04)
# ---------------------------------------------------------------------------

def case_material():
    bank_text, questions = _bank_state()
    normalized = _syllabus()
    bank_fp = authoring.bank_fingerprint(bank_text)
    report = auditor.coverage_report(normalized, questions,
                                     bank_fingerprint=bank_fp)

    # candidate materials are inert report data: no draft, no writer
    serialized = json.dumps(report, ensure_ascii=False)
    for forbidden in ("bank_after_text", "\"diff\"", "\"manifest\"",
                      "\"proposal\"", "author_callable", "write_units"):
        if forbidden in serialized:
            fail("material: coverage report must never carry draft/writer "
                 "authority (%s)" % forbidden)

    # the coverage/material domain APIs cannot reach an author or writer
    for fn in (auditor.coverage_report, auditor.material_request,
               auditor.apply_weak_priority):
        try:
            fn(normalized, questions, author=object(),
               bank_fingerprint=bank_fp)
            fail("material: %s must not accept an author" % fn.__name__)
        except TypeError:
            pass
        try:
            fn(normalized, questions, writer=object(),
               bank_fingerprint=bank_fp)
            fail("material: %s must not accept a writer" % fn.__name__)
        except TypeError:
            pass

    # supplied obtained material creates a separate cited request only
    obtained = (
        "# Obtained: Airway suctioning\n"
        "- emt:airway.suction: The learner suctions an obstructed airway\n")
    raw = obtained.encode("utf-8")
    req = auditor.material_request(
        raw, source_id="material.md", kind="markdown",
        objectives=["emt:airway.suction"], count=1, item_types=["mc"],
        retry_cap=3, mode="report_only")
    if req["schema_version"] != 1 or req["count"] != 1 or \
            req["item_types"] != ["mc"]:
        fail("material: request must preserve the exact bounds")
    if not req["citations"] or \
            req["citations"][0]["source_id"] != "material.md" or \
            req["citations"][0]["fingerprint"] != \
            auditor.source_fingerprint(raw):
        fail("material: request must carry exact citations to the new source")
    if req["source_fingerprints"] != [auditor.source_fingerprint(raw)]:
        fail("material: request must carry the new source fingerprint")

    # the created request validates against the strict authoring schema
    import resources
    import schema_validate as sv
    schema = json.loads(resources.read_text(
        "schemas/authoring_request.schema.json"))
    errs = sv.validate(req, schema)
    if errs:
        fail("material: created request fails the authoring schema: %s"
             % errs[:3])

    # material without the requested objective creates nothing
    try:
        auditor.material_request(
            obtained.encode("utf-8"), "material.md", "markdown",
            objectives=["emt:airway.missing"], count=1, item_types=["mc"])
        fail("material: absent objective must produce no request")
    except auditor.SourceError as exc:
        if exc.code != "material.no_citations":
            fail("material: wrong no-citation code %r" % exc.code)

    # weak-objective signals only reorder existing ids (D-19)
    keys = ["emt:airway.opa", "emt:airway.adjunct", "emt:airway.ventilation"]
    ordered, unknown = auditor.apply_weak_priority(
        keys, ["emt:airway.ventilation", "emt:not.in.source",
               "emt:airway.opa"])
    if ordered != ["emt:airway.ventilation", "emt:airway.opa",
                   "emt:airway.adjunct"]:
        fail("material: weak signals must reorder existing keys only, got %s"
             % ordered)
    if unknown != ["emt:not.in.source"]:
        fail("material: unknown weak signals must be reported and ignored")
    if set(ordered) != set(keys):
        fail("material: weak priority must never add or drop an objective")

    print("OK: material -- gap materials inert, obtained material creates "
          "only a cited request, weak signals reorder without inventing, "
          "author/writer unreachable")


CASES = {
    "normalize": case_normalize,
    "coverage": case_coverage,
    "material": case_material,
}


def main(argv):
    case = None
    rest = list(argv)
    if rest and rest[0] == "--case":
        case = rest[1] if len(rest) > 1 else None
    if case is None:
        for name, fn in sorted(CASES.items()):
            fn()
        return 0
    if case not in CASES:
        print("unknown case %r; known: %s" % (case, sorted(CASES)))
        return 2
    CASES[case]()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
