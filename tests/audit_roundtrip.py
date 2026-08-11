#!/usr/bin/env python3
"""Wave 0 standalone tracer and contract suite for Phase 11 (plan 11-01,
extended by plan 11-02 with the strict-schema case).

Run:
    python tests/audit_roundtrip.py --case tracer
    python tests/audit_roundtrip.py --case schemas   (plan 11-02)

Stdlib only, no live model, no external packages, and safe against real
banks: every fixture is materialized inside a temporary directory and never
mutated in place.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import authoring
import audit_writer
import auditor
import model


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------

SYLLABUS_MD = """# Unit 1: Airway Management

- emt:airway.opa: Learner can open and maintain an airway
- emt:airway.adjunct: Learner selects the correct airway adjunct

The student should be able to prioritize airway management in a cardiac arrest.
"""

BANK_TEMPLATE = """# Synthetic EMT bank (phase 11 tracer)

Q1. Which device delivers oxygen at a fixed concentration regardless of flow?
[OBJECTIVE: emt:airway.adjunct]
A) Non-rebreather mask
B) Nasal cannula
C) Venturi mask
D) Simple face mask
CORRECT: C
WHY BEST: A Venturi mask entrains a fixed air-oxygen ratio, so the delivered concentration stays constant.
KEY DISCRIMINATOR: The item tests fixed-concentration delivery versus variable delivery.
SECOND-BEST: A non-rebreather mask would be correct if the question asked for the highest possible concentration.
DISTRACTOR ANALYSIS:
- A) A non-rebreather mask would be correct if the question asked for the highest delivered concentration.
- B) A nasal cannula would be correct for low-flow supplemental oxygen.
- D) A simple face mask would be correct for moderate concentrations without precision.
TRAP: Learners confuse "highest" with "fixed".
CONFIDENCE: high

Q2. What is the first sign of an inadequate airway?
[OBJECTIVE: emt:airway.opa]
A) Snoring respirations
B) Clear breath sounds
C) Normal chest rise
D) Pink mucous membranes
CORRECT: A
WHY BEST: Snoring respirations indicate partial upper-airway obstruction by the tongue.
KEY DISCRIMINATOR: The item tests recognition of partial obstruction.
SECOND-BEST: Clear breath sounds would be correct if the question asked for an adequate airway.
DISTRACTOR ANALYSIS:
- B) Clear breath sounds would be correct for a patent airway.
- C) Normal chest rise would be correct for adequate ventilation.
- D) Pink mucous membranes would be correct for adequate perfusion.
TRAP: Learners wait for cyanosis instead of listening for snoring.
CONFIDENCE: high
"""

CLEAN_ITEM_TEXT = """Q1. During a primary assessment, the first action for an unresponsive patient is:
[OBJECTIVE: emt:airway.opa]
A) Opening and maintaining the airway
B) Checking for a pulse
C) Applying supplemental oxygen
D) Rechecking the blood pressure
CORRECT: A
WHY BEST: Opening the airway comes first because an unresponsive patient cannot protect their own airway.
KEY DISCRIMINATOR: The item turns on the order of the primary assessment versus later vital-sign checks.
SECOND-BEST: Checking for a pulse would be the second priority after the airway is opened.
DISTRACTOR ANALYSIS:
- B) Checking for a pulse would be correct if the airway were already patent.
- C) Applying supplemental oxygen would be correct after the airway is secured.
- D) Rechecking the blood pressure would be correct if the patient were stable and awake.
TRAP: Learners jump to circulation; the airway still comes first.
CONFIDENCE: high
"""

LEAK_ITEM_TEXT = """Q1. When a patient is unresponsive, you must open the airway and maintain patency as the first action:
[OBJECTIVE: emt:airway.opa]
A) Open the airway and maintain patency
B) Check the blood pressure first
C) Recheck the pupils
D) Count the respirations
CORRECT: A
WHY BEST: The unresponsive patient's airway must be opened and kept patent before anything else.
KEY DISCRIMINATOR: The item tests the opening step itself.
SECOND-BEST: Checking the blood pressure would be correct after the airway is managed.
DISTRACTOR ANALYSIS:
- B) Checking the blood pressure would be correct after the airway is secured.
- C) Rechecking the pupils would be correct in a neurologic assessment.
- D) Counting the respirations would be correct for a ventilatory assessment.
TRAP: Learners answer with the assessment they find easiest rather than the priority.
CONFIDENCE: high
"""

OUT_OF_SCOPE_ITEM_TEXT = CLEAN_ITEM_TEXT.replace(
    "[OBJECTIVE: emt:airway.opa]", "[OBJECTIVE: emt:cardiac.arrest]")


def _draft_response(item_text, objective, item_type="mc", citations=None):
    return {
        "schema_version": authoring.AUTHORING_SCHEMA_VERSION,
        "items": [{"objective": objective, "type": item_type,
                   "citations": citations or [], "text": item_text}],
    }


# ---------------------------------------------------------------------------
# spies
# ---------------------------------------------------------------------------

class SpyAuthor:
    """Records every payload it receives (for the AUTH-03 allowlist
    assertions) and returns drafts by attempt number."""

    def __init__(self, drafts):
        self.drafts = drafts
        self.calls = []

    def __call__(self, payload):
        self.calls.append(payload)
        return self.drafts(len(self.calls))


class SpyWriter:
    """Counts and records writer invocations, delegating to the real shadow
    writer so the tracer exercises the production mutation path."""

    def __init__(self, state_dir):
        self.calls = []
        self.state_dir = state_dir

    def __call__(self, proposal, target_path, state_dir,
                 expected_fingerprint=None, **kwargs):
        self.calls.append({
            "proposal": proposal, "target_path": target_path,
            "expected_fingerprint": expected_fingerprint})
        return audit_writer.write_units(proposal, target_path, state_dir,
                                        expected_fingerprint)


# ---------------------------------------------------------------------------
# shared helpers
# ---------------------------------------------------------------------------

def make_workdir(prefix):
    return tempfile.mkdtemp(prefix=prefix)


def write_source(workdir, text=SYLLABUS_MD, name="syllabus.md"):
    path = os.path.join(workdir, name)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    return path


def read_text(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def read_bytes(path):
    with open(path, "rb") as fh:
        return fh.read()


def normalized_source(workdir):
    path = write_source(workdir)
    with open(path, "rb") as fh:
        raw = fh.read()
    return auditor.normalize_source(raw, source_id="syllabus.md",
                                    kind="markdown")


def request_for(normalized, objective="emt:airway.opa", count=1,
                mode="full", retry_cap=2):
    citations = auditor.citations_for_objective(normalized, objective)
    if not citations:
        fail("fixture syllabus produced no citations for %r" % objective)
    return {
        "schema_version": authoring.AUTHORING_SCHEMA_VERSION,
        "objectives": [objective],
        "count": count,
        "item_types": ["mc"],
        "citations": citations,
        "retry_cap": retry_cap,
        "mode": mode,
    }


def prepared_bank(workdir):
    """The synthetic bank with [ID:]/[HASH:] minted, written to disk, and
    returned as text."""
    text, _ = model.assign_ids(BANK_TEMPLATE)
    path = os.path.join(workdir, "bank.md")
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    return path, text


# ---------------------------------------------------------------------------
# case: tracer (plan 11-01)
# ---------------------------------------------------------------------------

def case_tracer():
    workdir = make_workdir("audit-tracer-")
    try:
        normalized = normalized_source(workdir)
        citations = auditor.citations_for_objective(normalized,
                                                    "emt:airway.opa")
        bank_path, bank_text = prepared_bank(workdir)
        state_dir = os.path.join(workdir, "state")
        request = request_for(normalized)
        clean_citations = citations

        # --- the happy path: malformed-first / clean-second -------------
        author_spy = SpyAuthor(lambda n: _draft_response(
            OUT_OF_SCOPE_ITEM_TEXT, "emt:cardiac.arrest",
            citations=clean_citations) if n == 1 else _draft_response(
            CLEAN_ITEM_TEXT, "emt:airway.opa", citations=clean_citations))
        writer_spy = SpyWriter(state_dir)
        config = {"target_path": bank_path, "state_dir": state_dir,
          "full_opt_in": True}

        report = authoring.run_authoring(request, author_spy, bank_text,
                                         writer_spy, config)
        if report.get("status") != "written":
            fail("tracer: expected status 'written', got %r (%s)"
                 % (report.get("status"), report.get("outcome")))
        if not report.get("write_allowed"):
            fail("tracer: full mode should allow the write")
        manifest = report["manifest"]
        if manifest.get("state") != "applied":
            fail("tracer: manifest not applied: %r" % manifest.get("state"))
        if not manifest.get("write_id", "").startswith("w-"):
            fail("tracer: write id must be deterministic w-*: %r"
                 % manifest.get("write_id"))
        if manifest.get("backend") != "shadow":
            fail("tracer: non-Git synthetic bank must use shadow backend")

        # exactly one writer call, and it carried the expected fingerprint
        if len(writer_spy.calls) != 1:
            fail("tracer: expected exactly 1 writer call, got %d"
                 % len(writer_spy.calls))
        if writer_spy.calls[0]["expected_fingerprint"] != \
                authoring.bank_fingerprint(bank_text):
            fail("tracer: writer did not receive the preflighted bank "
                 "fingerprint")

        # two callable attempts; attempt 2 received the attempt-1 scope
        # finding as structured retry input
        if len(author_spy.calls) != 2:
            fail("tracer: expected 2 author attempts, got %d"
                 % len(author_spy.calls))
        payload1, payload2 = author_spy.calls
        if payload1["findings"] != []:
            fail("tracer: first attempt must receive no findings")
        if not payload2["findings"] or \
                payload2["findings"][-1].get("kind") != "scope":
            fail("tracer: second attempt must receive the structured scope "
                 "finding")

        # AUTH-03: the callable payload is the exact allowlist, with no
        # repository path, bank text, un-cited source text, or credentials
        _assert_repository_blind(author_spy, bank_text)

        # the bank now carries three questions and the new item has an id
        bank_after = read_text(bank_path)
        if len(model.parse_bank(bank_after)) != 3:
            fail("tracer: bank should have 3 items after the write")
        new_ids = [q.get("item_id") for q in model.parse_bank(bank_after)]
        if not all(new_ids):
            fail("tracer: every item must carry a minted [ID:]")
        if manifest["after_fingerprint"] != \
                authoring.bank_fingerprint(bank_after):
            fail("tracer: manifest after-fingerprint does not match the "
                 "written bank")

        # duplicate run: identical request+bank+state returns the existing
        # result with zero new generation and zero new mutation
        report2 = authoring.run_authoring(request, author_spy, bank_text,
                                          writer_spy, config)
        if report2.get("status") != "already_completed":
            fail("tracer: duplicate run must be idempotent, got %r"
                 % report2.get("status"))
        if len(author_spy.calls) != 2 or len(writer_spy.calls) != 1:
            fail("tracer: duplicate run must not generate or mutate again")
        if read_text(bank_path) != bank_after:
            fail("tracer: duplicate run mutated the bank")

        # one-step undo restores the exact before bytes
        # ...but first: a stale undo on an APPLIED write must refuse without
        # a force path (T-11-17), so a human edit is never overwritten.
        with open(bank_path, "a", encoding="utf-8") as fh:
            fh.write("\n# human edit after write\n")
        try:
            audit_writer.undo(manifest["write_id"], bank_path, state_dir)
            fail("tracer: stale undo must refuse (no force path)")
        except audit_writer.WriterError as exc:
            if exc.code != "undo.stale_target":
                fail("tracer: stale undo refused with wrong code %r"
                     % exc.code)
        if "# human edit after write" not in read_text(bank_path):
            fail("tracer: stale undo must leave the human edit untouched")
        # restore the applied state so the real undo can proceed
        with open(bank_path, "w", encoding="utf-8", newline="") as fh:
            fh.write(bank_after)

        undo = audit_writer.undo(manifest["write_id"], bank_path, state_dir)
        if undo.get("status") != "reverted":
            fail("tracer: undo failed: %r" % undo)
        if read_bytes(bank_path) != bank_text.encode("utf-8"):
            fail("tracer: undo did not restore the exact before bytes")
        undo2 = audit_writer.undo(manifest["write_id"], bank_path, state_dir)
        if undo2.get("status") != "already_reverted":
            fail("tracer: second undo must be idempotent")

        # --- out-of-scope exhaustion: zero writer calls -----------------
        wd2 = make_workdir("audit-scope-")
        try:
            norm2 = normalized_source(wd2)
            bank2_path, bank2_text = prepared_bank(wd2)
            state2 = os.path.join(wd2, "state")
            req2 = request_for(norm2, retry_cap=2)
            spy2 = SpyAuthor(lambda n: _draft_response(
                OUT_OF_SCOPE_ITEM_TEXT, "emt:cardiac.arrest",
                citations=auditor.citations_for_objective(
                    norm2, "emt:airway.opa")))
            writer2 = SpyWriter(state2)
            report3 = authoring.run_authoring(
                req2, spy2, bank2_text, writer2,
                {"target_path": bank2_path, "state_dir": state2,
 "full_opt_in": True})
            if report3.get("status") != "failed" or \
                    report3.get("outcome") != "retry_cap_exhausted":
                fail("tracer: out-of-scope exhaustion must fail with the "
                     "retained report, got %r/%r"
                     % (report3.get("status"), report3.get("outcome")))
            if len(writer2.calls) != 0:
                fail("tracer: scope mismatch must make zero writer calls")
            if not report3.get("retained_draft"):
                fail("tracer: exhausted run must retain the final draft")
        finally:
            shutil.rmtree(wd2, ignore_errors=True)

        # --- quality-gate retry: lint-clean but answer-leak draft --------
        wd3 = make_workdir("audit-quality-")
        try:
            norm3 = normalized_source(wd3)
            bank3_path, bank3_text = prepared_bank(wd3)
            state3 = os.path.join(wd3, "state")
            req3 = request_for(norm3, retry_cap=2)
            cits3 = auditor.citations_for_objective(norm3, "emt:airway.opa")
            spy3 = SpyAuthor(lambda n: _draft_response(
                LEAK_ITEM_TEXT, "emt:airway.opa",
                citations=cits3) if n == 1 else _draft_response(
                CLEAN_ITEM_TEXT, "emt:airway.opa", citations=cits3))
            writer3 = SpyWriter(state3)
            report4 = authoring.run_authoring(
                req3, spy3, bank3_text, writer3,
                {"target_path": bank3_path, "state_dir": state3,
 "full_opt_in": True})
            if report4.get("status") != "written":
                fail("tracer: quality-retry run must write after the clean "
                     "second attempt, got %r" % report4.get("status"))
            if len(writer3.calls) != 1:
                fail("tracer: quality-retry run must write exactly once")
            # the leak draft must have been rejected by the named detector
            leaked = None
            for findings in spy3.calls[1]["findings"]:
                if findings.get("kind") == "quality":
                    leaked = findings
            if leaked is None or not any(
                    r.get("code") == "quality.answer_leak"
                    for r in leaked.get("records", [])):
                fail("tracer: leak draft must produce a named answer-leak "
                     "quality finding on retry")
        finally:
            shutil.rmtree(wd3, ignore_errors=True)

        # --- report_only: no writer, identical proposal ------------------
        wd4 = make_workdir("audit-reportonly-")
        try:
            norm4 = normalized_source(wd4)
            bank4_path, bank4_text = prepared_bank(wd4)
            state4 = os.path.join(wd4, "state")
            req4 = request_for(norm4, mode="report_only", retry_cap=1)
            cits4 = auditor.citations_for_objective(norm4, "emt:airway.opa")
            spy4 = SpyAuthor(lambda n: _draft_response(
                CLEAN_ITEM_TEXT, "emt:airway.opa", citations=cits4))
            writer4 = SpyWriter(state4)
            report5 = authoring.run_authoring(
                req4, spy4, bank4_text, writer4,
                {"target_path": bank4_path, "state_dir": state4,
 "full_opt_in": True})
            if report5.get("status") != "proposed" or \
                    report5.get("write_allowed"):
                fail("tracer: report_only must propose and never write")
            if len(writer4.calls) != 0:
                fail("tracer: report_only made a writer call")
            if not report5.get("proposal", {}).get("diff"):
                fail("tracer: proposal must carry a reproducible diff")
            if read_text(bank4_path) != bank4_text:
                fail("tracer: report_only mutated the bank")
        finally:
            shutil.rmtree(wd4, ignore_errors=True)

        print("OK: tracer -- malformed-first/clean-second, both gates, one "
              "shadow write, duplicate idempotency, undo, scope/quality "
              "retry, report_only")
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def _assert_repository_blind(author_spy, bank_text):
    """AUTH-03 allowlist assertions over every payload the callable saw."""
    for payload in author_spy.calls:
        if sorted(payload.keys()) != sorted(
                ["schema_version", "contract", "request", "attempt",
                 "findings"]):
            fail("tracer: callable payload keys drifted from the allowlist: "
                 "%s" % sorted(payload.keys()))
        if not isinstance(payload["contract"], str) or \
                "Qn." not in payload["contract"]:
            fail("tracer: callable must receive the public format contract")
        serialized = json.dumps(payload, ensure_ascii=False)
        # Real leak indicators: repository file/module identifiers,
        # absolute paths, credentials, and fixture names -- never bare words
        # like "authoring" that legitimately appear in the public contract.
        for forbidden in ("model.py", "authoring.py", "audit_writer.py",
                          "auditor.py", "surfaces/", "tests/audit",
                          "audit_roundtrip", "/Users/", "\\Users\\",
                          "C:/Users", "/mnt/", "secret", "token",
                          "password", "BANK_TEMPLATE"):
            if forbidden in serialized:
                fail("tracer: repository context leaked to the author: %r"
                     % forbidden)
        # bank contents and un-cited source prose must never cross
        if bank_text in serialized:
            fail("tracer: bank text leaked to the author")
        if "prioritize airway management in a cardiac arrest" in serialized:
            fail("tracer: un-cited source prose leaked to the author")


def case_schemas():
    """Plan 11-02: the five strict public schemas accept the real Plan 11-01
    runtime payloads, reject extra and missing data, match runtime versions,
    and serialize stably under reordering."""
    import resources
    import schema_validate as sv

    schemas = {
        "request": "schemas/authoring_request.schema.json",
        "normalized": "schemas/normalized_document.schema.json",
        "quality": "schemas/quality_finding.schema.json",
        "report": "schemas/audit_report.schema.json",
        "manifest": "schemas/write_manifest.schema.json",
    }
    loaded = {}
    for name, path in schemas.items():
        doc = json.loads(resources.read_text(path))
        sv.check_schema(doc)  # raises SchemaError on unsupported keywords
        loaded[name] = doc

    workdir = make_workdir("audit-schemas-")
    try:
        normalized = normalized_source(workdir)
        request = request_for(normalized)

        # --- runtime payloads -------------------------------------------
        payloads = {"request": request, "normalized": normalized}

        # quality findings: a bank that triggers all four detectors
        findings = _all_detector_findings()
        codes = {f["code"] for f in findings}
        if codes != {"quality.answer_skew", "quality.near_duplicate_stems",
                     "quality.answer_leak", "quality.distractor_rationale"}:
            fail("schemas: fixture must trigger all four detectors, got %s"
                 % sorted(codes))
        for f in findings:
            errs = sv.validate(f, loaded["quality"])
            if errs:
                fail("schemas: quality finding fails its schema: %s" % errs)

        # report + manifest from a real full run
        bank_path, bank_text = prepared_bank(workdir)
        state_dir = os.path.join(workdir, "state")
        cits = auditor.citations_for_objective(normalized, "emt:airway.opa")
        author_spy = SpyAuthor(lambda n: _draft_response(
            CLEAN_ITEM_TEXT, "emt:airway.opa", citations=cits))
        writer_spy = SpyWriter(state_dir)
        report = authoring.run_authoring(
            request, author_spy, bank_text, writer_spy,
            {"target_path": bank_path, "state_dir": state_dir,
              "full_opt_in": True})
        if report.get("status") != "written":
            fail("schemas: full run did not write: %r" % report.get("status"))
        payloads["report"] = report
        payloads["manifest"] = report["manifest"]

        # a failed report carrying structured scope findings
        wd2 = os.path.join(workdir, "scope-fail")
        os.makedirs(wd2)
        bank2_path, bank2_text = prepared_bank(wd2)
        state2 = os.path.join(wd2, "state")
        req2 = request_for(normalized, retry_cap=1)
        spy2 = SpyAuthor(lambda n: _draft_response(
            OUT_OF_SCOPE_ITEM_TEXT, "emt:cardiac.arrest", citations=cits))
        failed = authoring.run_authoring(
            req2, spy2, bank2_text, SpyWriter(state2),
            {"target_path": bank2_path, "state_dir": state2,
 "full_opt_in": True})
        if failed.get("status") != "failed":
            fail("schemas: scope-fail run did not fail")
        payloads["failed_report"] = failed

        # --- version parity + acceptance ---------------------------------
        for name, payload in payloads.items():
            if name not in loaded:
                continue  # failed_report is validated against the report schema below
            errs = sv.validate(payload, loaded[name])
            if errs:
                fail("schemas: %s payload fails its schema: %s"
                     % (name, errs[:3]))
            if payload.get("schema_version") != loaded[name]["x-itembank-version"]:
                fail("schemas: %s runtime version %r != x-itembank-version %r"
                     % (name, payload.get("schema_version"),
                        loaded[name]["x-itembank-version"]))
        errs = sv.validate(failed, loaded["report"])
        if errs:
            fail("schemas: failed report fails the report schema: %s"
                 % errs[:3])

        # --- strict rejection: extra property -----------------------------
        extra = dict(request)
        extra["sneaky_field"] = True
        if not sv.validate(extra, loaded["request"]):
            fail("schemas: extra request property must fail")

        extra_doc = dict(normalized)
        extra_doc["spans"] = list(normalized["spans"])
        extra_doc["spans"].append({"span_id": "sp-x", "kind": "body",
                                   "locator": {"heading_path": [],
                                               "start_line": 1, "end_line": 1,
                                               "start_char": 0, "end_char": 0},
                                   "verbatim": "x", "stray": 1})
        if not sv.validate(extra_doc, loaded["normalized"]):
            fail("schemas: extra span property must fail")

        extra_finding = dict(findings[0])
        extra_finding["opaque_score"] = 0.9
        if not sv.validate(extra_finding, loaded["quality"]):
            fail("schemas: extra finding property must fail")

        extra_manifest = dict(report["manifest"])
        extra_manifest["restore_anyway"] = True
        if not sv.validate(extra_manifest, loaded["manifest"]):
            fail("schemas: extra manifest property (unsafe restore selector) "
                 "must fail")

        extra_report = dict(report)
        extra_report["caller_backend"] = "shadow"
        if not sv.validate(extra_report, loaded["report"]):
            fail("schemas: extra report property must fail")

        # --- strict rejection: missing required --------------------------
        for key in ("objectives", "count", "citations"):
            missing = dict(request)
            del missing[key]
            if not sv.validate(missing, loaded["request"]):
                fail("schemas: request missing %r must fail" % key)
        for key in ("write_id", "backend", "before_fingerprint",
                    "after_fingerprint"):
            missing = dict(report["manifest"])
            del missing[key]
            if not sv.validate(missing, loaded["manifest"]):
                fail("schemas: manifest missing %r must fail" % key)
        for key in ("schema_version", "status", "request_fingerprint"):
            missing = dict(report)
            del missing[key]
            if not sv.validate(missing, loaded["report"]):
                fail("schemas: report missing %r must fail" % key)

        # --- stable serialization under reordering ------------------------
        cits_a = auditor.citations_for_objective(normalized, "emt:airway.opa")
        cits_b = list(reversed(cits_a))
        canon_a = authoring.canonical_json(sorted(cits_a, key=lambda c: c["span_id"]))
        canon_b = authoring.canonical_json(sorted(cits_b, key=lambda c: c["span_id"]))
        if canon_a != canon_b:
            fail("schemas: reordered citation arrays must serialize "
                 "equivalently")

        print("OK: schemas -- five strict contracts accept runtime payloads, "
              "reject extra/missing data, version parity, stable ordering")
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def _all_detector_findings():
    """A bank that provokes all four quality detectors at once. Items are
    minimal-but-parseable; quality_gate does not lint, so only the named
    detectors decide."""
    items = []
    # skew: 12 mc items, 6 keyed A (50% > 40%)
    for i in range(12):
        correct = "A" if i < 6 else ("B" if i < 9 else "C")
        items.append(_mc_block(
            i + 1,
            "Which finding indicates a patent airway during assessment %d?"
            % (i + 1),
            ["Clear breath sounds", "Snoring respirations", "Stridor",
             "Absent chest rise"],
            correct,
            da={"A": "A is correct because the question asks about patency.",
                "B": "B would be correct if obstruction were present.",
                "C": "C would be correct if upper-airway narrowing were heard.",
                "D": "D would be correct if ventilation were absent."}))
    # near-duplicate pair (Jaccard 11/12 ~= 0.917 >= 0.85, 11+ tokens each)
    items.append(_mc_block(
        13,
        "The first priority in cardiac arrest management includes opening "
        "the airway, maintaining patency, then ventilating gently",
        ["Open the airway", "Start compressions", "Call for help",
         "Check the pulse"],
        "A",
        da={"A": "A is correct because the airway comes first.",
            "B": "B would be correct after the airway is secured.",
            "C": "C would be correct if the arrest were witnessed.",
            "D": "D would be correct after breathing is assessed."}))
    items.append(_mc_block(
        14,
        "The first priority in cardiac arrest management includes opening "
        "the airway, maintaining patency, then ventilating",
        ["Open the airway", "Start compressions", "Call for help",
         "Check the pulse"],
        "A",
        da={"A": "A is correct because the airway comes first.",
            "B": "B would be correct after the airway is secured.",
            "C": "C would be correct if the arrest were witnessed.",
            "D": "D would be correct after breathing is assessed."}))
    # answer leak: correct option run appears contiguously in the stem
    items.append(_mc_block(
        15,
        "When a patient is unresponsive, you must open the airway and "
        "maintain patency as the first action",
        ["Open the airway and maintain patency", "Check the blood pressure",
         "Recheck the pupils", "Count the respirations"],
        "A",
        da={"A": "A is correct because patency is the priority.",
            "B": "B would be correct after the airway is managed.",
            "C": "C would be correct in a neurologic assessment.",
            "D": "D would be correct for a ventilatory assessment."}))
    # distractor rationale missing the would-be condition
    items.append(_mc_block(
        16,
        "Which oxygen device delivers a fixed concentration?",
        ["Venturi mask", "Nasal cannula", "Non-rebreather", "Simple mask"],
        "A",
        da={"A": "A is correct because it entrains a fixed ratio.",
            "B": "B is a common choice for stable patients.",
            "C": "C would be correct for the highest concentration.",
            "D": "D would be correct for moderate oxygen needs."}))
    bank_text = "\n\n".join(items) + "\n"
    questions = model.parse_bank(bank_text)
    if len(questions) != 16:
        fail("schemas: detector fixture must parse into 16 items, got %d"
             % len(questions))
    return authoring.quality_gate(questions)


def _mc_block(num, stem, options, correct, da):
    lines = ["Q%d. %s" % (num, stem),
             "[OBJECTIVE: emt:airway.opa]"]
    for letter, text in zip("ABCD", options):
        lines.append("%s) %s" % (letter, text))
    lines.append("CORRECT: %s" % correct)
    lines.append("WHY BEST: The keyed option matches the stated priority.")
    lines.append("KEY DISCRIMINATOR: The item turns on one distinction.")
    lines.append("SECOND-BEST: The runner-up would need a different scenario.")
    lines.append("DISTRACTOR ANALYSIS:")
    for letter, text in zip("ABCD", options):
        note = da.get(letter)
        if note:
            lines.append("- %s) %s" % (letter, note))
    lines.append("TRAP: Learners confuse the priority order.")
    lines.append("CONFIDENCE: high")
    return "\n".join(lines)


CASES = {
    "tracer": case_tracer,
    "schemas": case_schemas,
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
