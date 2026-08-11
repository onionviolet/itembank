#!/usr/bin/env python3
"""Scope/retry/idempotency/interruption/parallel and autonomy-mode contract
suite for the Phase 11 bounded authoring loop (plan 11-04 Tasks 2-3,
AUTH-01/AUTH-02/AUTH-03, AUDIT-05/AUDIT-06/AUDIT-09).

Run:
    python tests/audit_authoring_roundtrip.py --case retry
    python tests/audit_authoring_roundtrip.py --case stateful
    python tests/audit_authoring_roundtrip.py            (all cases)

Stdlib only. Adversarial draft fixtures live in fixtures/audit/retry_drafts.json;
every writer test uses the real shadow writer or a fake writer that records
and simulates interruption -- never a live model.
"""
import json
import os
import shutil
import sys
import tempfile
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import audit_writer
import authoring
import auditor
import model

FIXTURES = os.path.join(ROOT, "fixtures", "audit")


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


# ---------------------------------------------------------------------------
# shared helpers (standalone per repo test convention)
# ---------------------------------------------------------------------------

def read_text(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def read_bytes(path):
    with open(path, "rb") as fh:
        return fh.read()


SYLLABUS_MD = ("# Unit 1: Airway Management\n\n"
               "- emt:airway.opa: The learner opens and maintains a patent "
               "airway\n")

BANK_TEMPLATE = """# Synthetic EMT bank (phase 11 authoring)

Q1. Which device delivers oxygen at a fixed concentration regardless of flow?
[OBJECTIVE: emt:airway.adjunct]
A) Non-rebreather mask
B) Nasal cannula
C) Venturi mask
D) Simple face mask
CORRECT: C
WHY BEST: A Venturi mask entrains a fixed air-oxygen ratio.
KEY DISCRIMINATOR: Fixed versus variable delivery.
SECOND-BEST: A non-rebreather mask would be correct for the highest concentration.
DISTRACTOR ANALYSIS:
- A) A non-rebreather mask would be correct if the question asked for the highest concentration.
- B) A nasal cannula would be correct for low-flow oxygen.
- D) A simple face mask would be correct for moderate concentrations.
TRAP: Confusing highest with fixed.
CONFIDENCE: high

Q2. What is the first sign of an inadequate airway?
[OBJECTIVE: emt:airway.opa]
A) Snoring respirations
B) Clear breath sounds
C) Normal chest rise
D) Pink mucous membranes
CORRECT: A
WHY BEST: Snoring respirations indicate partial upper-airway obstruction.
KEY DISCRIMINATOR: Recognition of partial obstruction.
SECOND-BEST: Clear breath sounds would be correct for a patent airway.
DISTRACTOR ANALYSIS:
- B) Clear breath sounds would be correct for a patent airway.
- C) Normal chest rise would be correct for adequate ventilation.
- D) Pink mucous membranes would be correct for adequate perfusion.
TRAP: Waiting for cyanosis.
CONFIDENCE: high
"""


def workdir(prefix):
    return tempfile.mkdtemp(prefix=prefix)


def normalized_source(wd):
    path = os.path.join(wd, "syllabus.md")
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(SYLLABUS_MD)
    with open(path, "rb") as fh:
        raw = fh.read()
    return auditor.normalize_source(raw, source_id="syllabus.md",
                                    kind="markdown")


def prepared_bank(wd):
    text, _ = model.assign_ids(BANK_TEMPLATE)
    path = os.path.join(wd, "bank.md")
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    return path, text


def make_request(normalized, count=1, mode="full", retry_cap=3,
                 objectives=None):
    objectives = objectives or ["emt:airway.opa"]
    citations = []
    for obj in objectives:
        citations.extend(auditor.citations_for_objective(normalized, obj))
    if not citations:
        fail("fixture syllabus produced no citations for %s" % objectives)
    return {
        "schema_version": authoring.AUTHORING_SCHEMA_VERSION,
        "objectives": objectives,
        "count": count,
        "item_types": ["mc"],
        "citations": citations,
        "retry_cap": retry_cap,
        "mode": mode,
    }


def draft_response(item_text, objective="emt:airway.opa", citations=None,
                   item_type="mc"):
    return {
        "schema_version": authoring.AUTHORING_SCHEMA_VERSION,
        "items": [{"objective": objective, "type": item_type,
                   "citations": citations or [], "text": item_text}],
    }


class SpyAuthor:
    def __init__(self, drafts):
        self.drafts = drafts  # callable(attempt) -> response
        self.calls = []

    def __call__(self, payload):
        self.calls.append(payload)
        return self.drafts(len(self.calls))


class SpyWriter:
    """Counts calls and delegates to the real shadow writer."""

    def __init__(self, state_dir):
        self.calls = []
        self.state_dir = state_dir

    def __call__(self, proposal, target_path, state_dir,
                 expected_fingerprint=None, **kwargs):
        self.calls.append({"proposal": proposal, "target_path": target_path,
                           "expected_fingerprint": expected_fingerprint})
        return audit_writer.write_units(proposal, target_path, state_dir,
                                        expected_fingerprint)


def load_drafts():
    path = os.path.join(FIXTURES, "retry_drafts.json")
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)["drafts"]


def build_item_response(spec, citations):
    """Turn a fixture draft spec into a response dict. Citations are filled
    from the live request; injection specs add their untrusted fields;
    malformed specs return their raw non-dict response."""
    if "item" not in spec:
        return spec["response"]
    resp = {"schema_version": authoring.AUTHORING_SCHEMA_VERSION,
            "items": [{"objective": spec["item"]["objective"],
                       "type": spec["item"]["type"],
                       "citations": citations,
                       "text": spec["item"]["text"]}]}
    resp.update(spec.get("response_extra") or {})
    return resp


def full_config(bank_path, state_dir, **extra):
    cfg = {"target_path": bank_path, "state_dir": state_dir,
           "full_opt_in": True}
    cfg.update(extra)
    return cfg


# ---------------------------------------------------------------------------
# case: retry (plan 11-04 Task 2, AUTH-01/AUTH-02/AUTH-03/AUDIT-06)
# ---------------------------------------------------------------------------

def case_retry():
    drafts = load_drafts()
    wd = workdir("audit-retry-")
    try:
        normalized = normalized_source(wd)
        cits = auditor.citations_for_objective(normalized, "emt:airway.opa")

        # --- scope-before-lint, structured findings as retry input ---------
        spy = SpyAuthor(lambda n: build_item_response(
            drafts["malformed_not_object"], cits) if n == 1 else
            build_item_response(drafts["clean"], cits))
        bank_path, bank_text = prepared_bank(wd)
        writer = SpyWriter(os.path.join(wd, "state1"))
        report = authoring.run_authoring(
            make_request(normalized, retry_cap=2), spy, bank_text, writer,
            full_config(bank_path, os.path.join(wd, "state1")))
        if report.get("status") != "written":
            fail("retry: malformed-first/clean-second must write, got %r"
                 % report.get("status"))
        if len(spy.calls) != 2:
            fail("retry: expected 2 attempts, got %d" % len(spy.calls))
        first_findings = spy.calls[1]["findings"]
        if not first_findings or first_findings[0].get("kind") != "scope":
            fail("retry: second attempt must receive the structured scope "
                 "finding first")

        # --- out-of-scope draft: scope finding, never lint -----------------
        spy2 = SpyAuthor(lambda n: build_item_response(
            drafts["scope_wrong_objective"], cits))
        bank2_path, bank2_text = prepared_bank(wd)
        w2 = SpyWriter(os.path.join(wd, "state2"))
        report2 = authoring.run_authoring(
            make_request(normalized, retry_cap=2), spy2, bank2_text, w2,
            full_config(bank2_path, os.path.join(wd, "state2")))
        if report2.get("status") != "failed" or len(w2.calls) != 0:
            fail("retry: out-of-scope must fail with zero writer calls")
        for group in spy2.calls[1]["findings"]:
            if group.get("kind") == "lint":
                fail("retry: an out-of-scope draft must never reach lint")

        # --- lint-failing draft: structured lint finding -------------------
        spy3 = SpyAuthor(lambda n: build_item_response(
            drafts["lint_failing_missing_why"], cits) if n == 1 else
            build_item_response(drafts["clean"], cits))
        bank3_path, bank3_text = prepared_bank(wd)
        w3 = SpyWriter(os.path.join(wd, "state3"))
        report3 = authoring.run_authoring(
            make_request(normalized, retry_cap=2), spy3, bank3_text, w3,
            full_config(bank3_path, os.path.join(wd, "state3")))
        if report3.get("status") != "written":
            fail("retry: lint-failing then clean must write, got %r"
                 % report3.get("status"))
        lint_group = None
        for group in spy3.calls[1]["findings"]:
            if group.get("kind") == "lint":
                lint_group = group
        if lint_group is None or not any(
                r.get("code") == "item.missing_why_best"
                for r in lint_group.get("records", [])):
            fail("retry: lint failure must produce item.missing_why_best "
                 "records")

        # --- quality-failing draft: named detector finding -----------------
        spy4 = SpyAuthor(lambda n: build_item_response(
            drafts["quality_failing_answer_leak"], cits) if n == 1 else
            build_item_response(drafts["clean"], cits))
        bank4_path, bank4_text = prepared_bank(wd)
        w4 = SpyWriter(os.path.join(wd, "state4"))
        report4 = authoring.run_authoring(
            make_request(normalized, retry_cap=2), spy4, bank4_text, w4,
            full_config(bank4_path, os.path.join(wd, "state4")))
        if report4.get("status") != "written":
            fail("retry: quality-failing then clean must write, got %r"
                 % report4.get("status"))
        quality_group = None
        for group in spy4.calls[1]["findings"]:
            if group.get("kind") == "quality":
                quality_group = group
        if quality_group is None or not any(
                r.get("code") == "quality.answer_leak"
                for r in quality_group.get("records", [])):
            fail("retry: quality failure must produce quality.answer_leak")

        # --- exact retry cap: exhaustion retains the draft, no writer ------
        spy5 = SpyAuthor(lambda n: build_item_response(
            drafts["scope_wrong_objective"], cits))
        bank5_path, bank5_text = prepared_bank(wd)
        w5 = SpyWriter(os.path.join(wd, "state5"))
        report5 = authoring.run_authoring(
            make_request(normalized, retry_cap=3), spy5, bank5_text, w5,
            full_config(bank5_path, os.path.join(wd, "state5")))
        if len(spy5.calls) != 3:
            fail("retry: retry cap 3 must make exactly 3 calls, got %d"
                 % len(spy5.calls))
        if report5.get("status") != "failed" or \
                report5.get("outcome") != "retry_cap_exhausted":
            fail("retry: exhaustion must fail with the retained report")
        if not report5.get("retained_draft"):
            fail("retry: exhaustion must retain the final draft")
        if len(w5.calls) != 0:
            fail("retry: exhaustion must make zero writer calls")

        # --- last-attempt success: success on the cap proceeds -------------
        spy6 = SpyAuthor(lambda n: build_item_response(
            drafts["scope_wrong_objective"], cits) if n < 3 else
            build_item_response(drafts["clean"], cits))
        bank6_path, bank6_text = prepared_bank(wd)
        w6 = SpyWriter(os.path.join(wd, "state6"))
        report6 = authoring.run_authoring(
            make_request(normalized, retry_cap=3), spy6, bank6_text, w6,
            full_config(bank6_path, os.path.join(wd, "state6")))
        if report6.get("status") != "written" or len(spy6.calls) != 3:
            fail("retry: last-attempt success must write after exactly 3 "
                 "calls")

        # --- no clean prefix in a dirty batch ------------------------------
        spy7 = SpyAuthor(lambda n: {
            "schema_version": authoring.AUTHORING_SCHEMA_VERSION,
            "items": [{"objective": "emt:airway.opa", "type": "mc",
                       "citations": cits, "text": drafts["clean"]["item"]["text"]},
                      {"objective": "emt:airway.opa", "type": "mc",
                       "citations": cits,
                       "text": drafts["quality_failing_answer_leak"]["item"]["text"]}]})
        bank7_path, bank7_text = prepared_bank(wd)
        w7 = SpyWriter(os.path.join(wd, "state7"))
        report7 = authoring.run_authoring(
            make_request(normalized, count=2, retry_cap=1), spy7, bank7_text,
            w7, full_config(bank7_path, os.path.join(wd, "state7")))
        if report7.get("status") != "failed" or len(w7.calls) != 0:
            fail("retry: a dirty batch must never write its clean prefix")
        if len(report7.get("retained_draft", {}).get("items", [])) != 2:
            fail("retry: the retained draft must be the complete batch")

        # --- empty/null/malformed responses are structured retries ---------
        for malformed in ("malformed_empty_items", "malformed_null_items"):
            spy8 = SpyAuthor(lambda n, m=malformed: build_item_response(
                drafts[m], cits) if n == 1 else
                build_item_response(drafts["clean"], cits))
            bank8_path, bank8_text = prepared_bank(wd)
            w8 = SpyWriter(os.path.join(wd, "state8-" + malformed))
            report8 = authoring.run_authoring(
                make_request(normalized, retry_cap=2), spy8, bank8_text, w8,
                full_config(bank8_path, os.path.join(wd, "state8-" + malformed)))
            if report8.get("status") != "written":
                fail("retry: %s must be a structured retry then write"
                     % malformed)

        # --- stable finding order across identical runs --------------------
        spy9a = SpyAuthor(lambda n: build_item_response(
            drafts["scope_wrong_objective"], cits))
        bank9_path, bank9_text = prepared_bank(wd)
        w9a = SpyWriter(os.path.join(wd, "state9"))
        r9a = authoring.run_authoring(
            make_request(normalized, retry_cap=2), spy9a, bank9_text, w9a,
            full_config(bank9_path, os.path.join(wd, "state9")))
        spy9b = SpyAuthor(lambda n: build_item_response(
            drafts["scope_wrong_objective"], cits))
        w9b = SpyWriter(os.path.join(wd, "state9b"))
        r9b = authoring.run_authoring(
            make_request(normalized, retry_cap=2), spy9b, bank9_text, w9b,
            full_config(bank9_path, os.path.join(wd, "state9b")))
        if authoring.canonical_json(r9a["findings"]) != \
                authoring.canonical_json(r9b["findings"]):
            fail("retry: identical runs must produce identical findings")

        # --- prompt injection cannot change authority (11-AI-SPEC 4b) ------
        for injected in ("injected_response_fields",
                         "injected_item_instructions"):
            spy10 = SpyAuthor(lambda n, m=injected: build_item_response(
                drafts[m], cits) if n == 1 else
                build_item_response(drafts["clean"], cits))
            bank10_path, bank10_text = prepared_bank(wd)
            w10 = SpyWriter(os.path.join(wd, "state10-" + injected))
            req10 = make_request(normalized, mode="report_only", retry_cap=2)
            report10 = authoring.run_authoring(
                req10, spy10, bank10_text, w10,
                {"target_path": bank10_path,
                 "state_dir": os.path.join(wd, "state10-" + injected)})
            if report10.get("status") != "proposed":
                fail("retry: %s must not change the run outcome, got %r"
                     % (injected, report10.get("status")))
            if report10.get("write_allowed") or len(w10.calls) != 0:
                fail("retry: %s must not grant writer permission" % injected)
            if report10.get("mode") != "report_only":
                fail("retry: %s changed the mode" % injected)
            for payload in spy10.calls:
                if payload["request"]["mode"] != "report_only":
                    fail("retry: injected fields leaked into the request")
        print("OK: retry -- scope-before-lint, structured lint/quality "
              "findings, exact cap and last-attempt success, no clean "
              "prefix, malformed retries, stable ordering, prompt "
              "injection resistance")
    finally:
        shutil.rmtree(wd, ignore_errors=True)


# ---------------------------------------------------------------------------
# case: stateful (plan 11-04 Task 3, AUTH-01/AUTH-02, AUDIT-05/AUDIT-09)
# ---------------------------------------------------------------------------

def _clean_author(normalized, cits, clean_text=None):
    if clean_text is None:
        drafts = load_drafts()
        clean_text = drafts["clean"]["item"]["text"]
    return SpyAuthor(lambda n: draft_response(clean_text, citations=cits))


def case_stateful():
    wd = workdir("audit-stateful-")
    try:
        normalized = normalized_source(wd)
        cits = auditor.citations_for_objective(normalized, "emt:airway.opa")
        drafts = load_drafts()
        # Pre-mint [ID:]/[HASH:] into the clean draft once: assign_ids keeps
        # an existing id/hash verbatim, so every run over this block produces
        # a byte-identical proposal (what the identical-diff assertion needs).
        clean_text, _ = model.assign_ids(drafts["clean"]["item"]["text"])

        # --- duplicate-run idempotency -------------------------------------
        bank_path, bank_text = prepared_bank(wd)
        state1 = os.path.join(wd, "state1")
        spy = _clean_author(normalized, cits, clean_text)
        w1 = SpyWriter(state1)
        req = make_request(normalized, retry_cap=2)
        r1 = authoring.run_authoring(req, spy, bank_text, w1,
                                     full_config(bank_path, state1))
        if r1.get("status") != "written":
            fail("stateful: first run must write, got %r" % r1.get("status"))
        calls_after_first = (len(spy.calls), len(w1.calls))
        r2 = authoring.run_authoring(req, spy, bank_text, w1,
                                     full_config(bank_path, state1))
        if r2.get("status") != "already_completed":
            fail("stateful: duplicate run must be idempotent, got %r"
                 % r2.get("status"))
        if (len(spy.calls), len(w1.calls)) != calls_after_first:
            fail("stateful: duplicate run must not generate or mutate again")
        if r2.get("manifest", {}).get("write_id") != \
                r1["manifest"]["write_id"]:
            fail("stateful: duplicate run must return the same write id")

        # --- interruption: no false completion without a writer result -----
        class InterruptingWriter:
            def __init__(self):
                self.calls = []
                self.error = audit_writer.WriterError(
                    "writer.interrupted",
                    "simulated interruption between prepare and apply")

            def __call__(self, proposal, target_path, state_dir,
                         expected_fingerprint=None, **kw):
                self.calls.append(1)
                raise self.error

        bank2_path, bank2_text = prepared_bank(wd)
        state2 = os.path.join(wd, "state2")
        spy2 = _clean_author(normalized, cits, clean_text)
        iw = InterruptingWriter()
        r3 = authoring.run_authoring(make_request(normalized), spy2, bank2_text,
                                     iw, full_config(bank2_path, state2))
        if r3.get("status") != "failed" or \
                r3.get("outcome") != "writer_writer.interrupted":
            fail("stateful: interruption must surface as an explicit failed "
                 "report, got %r/%r" % (r3.get("status"), r3.get("outcome")))
        if len(iw.calls) != 1:
            fail("stateful: interrupted run must make exactly one writer "
                 "call")
        if len(model.parse_bank(read_text(bank2_path))) != 2:
            fail("stateful: interrupted run must not mutate the bank")

        # --- prepared-state visibility with the real writer -----------------
        class PrepareThenRaise:
            """Persists the prepared manifest (the visible run) then raises,
            proving an interrupted run is never reported complete."""

            def __call__(self, proposal, target_path, state_dir,
                         expected_fingerprint=None, **kw):
                import audit_writer as aw
                from authoring import canonical_json
                manifests = os.path.join(state_dir, aw.MANIFESTS_DIR)
                before = os.path.join(state_dir, aw.BEFORE_DIR)
                os.makedirs(manifests, exist_ok=True)
                os.makedirs(before, exist_ok=True)
                wid = aw.deterministic_write_id(proposal)
                manifest = {
                    "schema_version": 1, "write_id": wid, "run_id": proposal.get("run_id", ""),
                    "backend": "shadow", "state": "prepared",
                    "target_path": os.path.abspath(target_path),
                    "units": proposal.get("units", []),
                    "before_fingerprint": proposal["bank_before_fingerprint"],
                    "before_image": os.path.join(before, "x.bin"),
                    "after_fingerprint": proposal["bank_after_fingerprint"],
                    "request_fingerprint": proposal["request_fingerprint"],
                    "source_fingerprints": proposal.get("source_fingerprints", []),
                    "tool_version": proposal.get("tool_version", ""),
                    "diff": proposal.get("diff", ""),
                    "created_at": "2026-01-01T00:00:00Z", "applied_at": None,
                    "git_commit": None,
                }
                with open(os.path.join(manifests, wid + ".json"), "w",
                          encoding="utf-8") as fh:
                    json.dump(manifest, fh, ensure_ascii=False, indent=2)
                raise audit_writer.WriterError(
                    "writer.interrupted", "simulated crash after prepared")
        bank3_path, bank3_text = prepared_bank(wd)
        state3 = os.path.join(wd, "state3")
        spy3 = _clean_author(normalized, cits, clean_text)
        r4 = authoring.run_authoring(make_request(normalized), spy3, bank3_text,
                                     PrepareThenRaise(), full_config(bank3_path, state3))
        if r4.get("status") != "failed" or r4.get("outcome") != \
                "writer_writer.interrupted":
            fail("stateful: prepared-then-crash must be a failed report")
        manifests = os.path.join(state3, audit_writer.MANIFESTS_DIR)
        if not os.listdir(manifests):
            fail("stateful: a prepared manifest must remain visible")
        if len(model.parse_bank(read_text(bank3_path))) != 2:
            fail("stateful: crash before apply must leave the bank untouched")

        # --- parallel handoffs: at most one mutation -----------------------
        bank4_path, bank4_text = prepared_bank(wd)
        state4 = os.path.join(wd, "state4")
        barrier = threading.Barrier(2)
        results = {}

        def run_thread(tag):
            spy_t = _clean_author(normalized, cits, clean_text)
            w_t = SpyWriter(state4)
            results[tag] = authoring.run_authoring(
                make_request(normalized), spy_t, bank4_text, w_t,
                full_config(bank4_path, state4))
            barrier.wait()

        t1 = threading.Thread(target=run_thread, args=("a",))
        t2 = threading.Thread(target=run_thread, args=("b",))
        t1.start(); t2.start()
        t1.join(); t2.join()
        manifests = os.path.join(state4, audit_writer.MANIFESTS_DIR)
        manifest_files = [f for f in os.listdir(manifests)
                          if f.endswith(".json")]
        if len(manifest_files) != 1:
            fail("stateful: parallel runs must produce exactly one manifest, "
                 "got %d" % len(manifest_files))
        if len(model.parse_bank(read_text(bank4_path))) != 3:
            fail("stateful: parallel runs must apply the item exactly once")
        statuses = sorted(r.get("status") for r in results.values())
        if "written" not in statuses:
            fail("stateful: at least one parallel run must write, got %s"
                 % statuses)

        # --- three modes share byte-equivalent gates and diff --------------
        diffs = {}
        gates = {}
        shared_bank_text, _ = model.assign_ids(BANK_TEMPLATE)
        bank5_path = os.path.join(wd, "bank5.md")
        bank6_path = os.path.join(wd, "bank6.md")
        bank8_path = os.path.join(wd, "bank8.md")
        for p in (bank5_path, bank6_path, bank8_path):
            with open(p, "w", encoding="utf-8", newline="") as fh:
                fh.write(shared_bank_text)
        state5a = os.path.join(wd, "state5a")
        spy_ro = _clean_author(normalized, cits, clean_text)
        r_ro = authoring.run_authoring(
            make_request(normalized, mode="report_only"), spy_ro,
            shared_bank_text, SpyWriter(state5a),
            {"target_path": bank5_path, "state_dir": state5a})
        diffs["report_only"] = r_ro["proposal"]["diff"]
        gates["report_only"] = authoring.canonical_json(
            r_ro["proposal"]["gates"])

        state6 = os.path.join(wd, "state6")
        spy_da = _clean_author(normalized, cits, clean_text)
        r_da = authoring.run_authoring(
            make_request(normalized, mode="draft_and_approve"), spy_da,
            shared_bank_text, SpyWriter(state6),
            {"target_path": bank6_path, "state_dir": state6})
        if r_da.get("status") != "awaiting_approval":
            fail("stateful: draft_and_approve without approval must await")
        pending = r_da["pending_write_ids"]
        approved = authoring.run_authoring(
            make_request(normalized, mode="draft_and_approve"),
            _clean_author(normalized, cits, clean_text), shared_bank_text,
            SpyWriter(state6),
            {"target_path": bank6_path, "state_dir": state6,
             "approved_write_ids": pending})
        if approved.get("status") != "written":
            fail("stateful: exact write-id approval must write, got %r"
                 % approved.get("status"))
        diffs["draft_and_approve"] = approved["proposal"]["diff"]
        gates["draft_and_approve"] = authoring.canonical_json(
            approved["proposal"]["gates"])

        # approval mismatch: refused, no write
        bank7_path, bank7_text = prepared_bank(wd)
        state7 = os.path.join(wd, "state7")
        w7 = SpyWriter(state7)
        r_mismatch = authoring.run_authoring(
            make_request(normalized, mode="draft_and_approve"),
            _clean_author(normalized, cits, clean_text), bank7_text, w7,
            {"target_path": bank7_path, "state_dir": state7,
             "approved_write_ids": ["w-wrong-id"]})
        if r_mismatch.get("status") != "refused" or \
                r_mismatch.get("outcome") != "approval_mismatch" or \
                len(w7.calls) != 0:
            fail("stateful: wrong approval id must refuse with no write")

        bank8_path = os.path.join(wd, "bank8.md")
        state8 = os.path.join(wd, "state8")
        spy_full = _clean_author(normalized, cits, clean_text)
        r_full = authoring.run_authoring(
            make_request(normalized, mode="full"), spy_full, shared_bank_text,
            SpyWriter(state8), full_config(bank8_path, state8))
        if r_full.get("status") != "written":
            fail("stateful: full must write, got %r" % r_full.get("status"))
        diffs["full"] = r_full["proposal"]["diff"]
        gates["full"] = authoring.canonical_json(r_full["proposal"]["gates"])
        if len({diffs["report_only"], diffs["draft_and_approve"],
                diffs["full"]}) != 1:
            fail("stateful: all three modes must share the identical diff")
        if len({gates["report_only"], gates["draft_and_approve"],
                gates["full"]}) != 1:
            fail("stateful: all three modes must share identical gate "
                 "evidence")

        # --- full autonomy: explicit opt-in, caps, volume accounting -------
        bank9_path, bank9_text = prepared_bank(wd)
        state9 = os.path.join(wd, "state9")
        spy_noopt = _clean_author(normalized, cits, clean_text)
        r_noopt = authoring.run_authoring(
            make_request(normalized, mode="full"), spy_noopt, bank9_text,
            SpyWriter(state9), {"target_path": bank9_path, "state_dir": state9})
        if r_noopt.get("status") != "refused" or \
                r_noopt.get("outcome") != "opt_in_required":
            fail("stateful: full without explicit opt-in must refuse before "
                 "generation")
        if len(spy_noopt.calls) != 0:
            fail("stateful: opt-in refusal must not call the model")

        bank10_path, bank10_text = prepared_bank(wd)
        state10 = os.path.join(wd, "state10")
        spy_cap = _clean_author(normalized, cits, clean_text)
        r_cap = authoring.run_authoring(
            make_request(normalized, mode="full", count=3), spy_cap,
            bank10_text, SpyWriter(state10),
            full_config(bank10_path, state10, caps={"per_run": 2}))
        if r_cap.get("status") != "refused" or \
                r_cap.get("outcome") != "cap_exceeded":
            fail("stateful: per-run cap exceeded must refuse before "
                 "generation")
        if len(spy_cap.calls) != 0:
            fail("stateful: cap refusal must not call the model")
        if r_cap["proposed_volume"] != 3:
            fail("stateful: refusal must report the proposed volume")

        # volume on success: proposed/completed/rejected/retried/written
        bank11_path, bank11_text = prepared_bank(wd)
        state11 = os.path.join(wd, "state11")
        spy_vol = SpyAuthor(lambda n: draft_response(
            drafts["scope_wrong_objective"]["item"]["text"],
            objective="emt:cardiac.arrest", citations=cits) if n == 1
            else draft_response(clean_text, citations=cits))
        w11 = SpyWriter(state11)
        r_vol = authoring.run_authoring(
            make_request(normalized, retry_cap=2), spy_vol, bank11_text, w11,
            full_config(bank11_path, state11))
        if r_vol.get("status") != "written":
            fail("stateful: volume run must write")
        if r_vol["proposed_volume"] != 1 or r_vol["written_volume"] != 1 or \
                r_vol["completed_volume"] != 1 or r_vol["retried_volume"] != 1 \
                or r_vol["rejected_volume"] != 0:
            fail("stateful: success volume accounting wrong: %s"
                 % {k: r_vol[k] for k in
                    ("proposed_volume", "written_volume", "completed_volume",
                     "retried_volume", "rejected_volume")})
        po = r_vol["per_objective_volume"]
        if po["emt:airway.opa"]["written"] != 1 or \
                po["emt:airway.opa"]["retried"] != 1:
            fail("stateful: per-objective volume breakdown wrong: %s" % po)

        # volume on exhaustion: rejected and retried visible, zero written
        bank12_path, bank12_text = prepared_bank(wd)
        state12 = os.path.join(wd, "state12")
        spy_ex = SpyAuthor(lambda n: draft_response(
            drafts["scope_wrong_objective"]["item"]["text"],
            objective="emt:cardiac.arrest", citations=cits))
        w12 = SpyWriter(state12)
        r_ex = authoring.run_authoring(
            make_request(normalized, retry_cap=3), spy_ex, bank12_text, w12,
            full_config(bank12_path, state12))
        if r_ex["written_volume"] != 0 or r_ex["retried_volume"] != 2 or \
                r_ex["rejected_volume"] != 1:
            fail("stateful: exhaustion volume accounting wrong: %s"
                 % {k: r_ex[k] for k in ("written_volume", "retried_volume",
                                         "rejected_volume")})

        # no run completes without one matching scope-valid writer result:
        # every writer call received the preflighted expected fingerprint
        for w_call in w11.calls:
            if w_call["expected_fingerprint"] != \
                    authoring.bank_fingerprint(bank11_text):
                fail("stateful: writer must receive the preflighted bank "
                     "fingerprint")

        # --- stale preflight: a changed bank refuses at the writer ---------
        bank13_path, bank13_text = prepared_bank(wd)
        state13 = os.path.join(wd, "state13")

        class MutateThenWrite:
            def __init__(self):
                self.calls = []

            def __call__(self, proposal, target_path, state_dir,
                         expected_fingerprint=None, **kw):
                self.calls.append(1)
                with open(target_path, "a", encoding="utf-8") as fh:
                    fh.write("\n# human edit during the run\n")
                return audit_writer.write_units(proposal, target_path,
                                                state_dir,
                                                expected_fingerprint)

        mw = MutateThenWrite()
        spy13 = _clean_author(normalized, cits, clean_text)
        r_stale = authoring.run_authoring(
            make_request(normalized), spy13, bank13_text, mw,
            full_config(bank13_path, state13))
        if r_stale.get("status") != "failed" or \
                r_stale.get("outcome") != "writer_writer.stale_preflight":
            fail("stateful: stale preflight must fail at the writer, got "
                 "%r/%r" % (r_stale.get("status"), r_stale.get("outcome")))
        if "# human edit during the run" not in read_text(bank13_path):
            fail("stateful: stale refusal must leave the human edit intact")
        if len(model.parse_bank(read_text(bank13_path))) != 2:
            fail("stateful: stale refusal must not write the item")

        print("OK: stateful -- duplicate idempotency, interruption "
              "visibility, parallel single-mutation, identical gates across "
              "modes, exact approval, opt-in/caps, every-exit volume, stale "
              "preflight refusal")
    finally:
        shutil.rmtree(wd, ignore_errors=True)


CASES = {"retry": case_retry, "stateful": case_stateful}


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
