#!/usr/bin/env python3
"""The thin command adapter over the Phase 11 domain APIs (plan 11-01; full
`itembank audit ...` registration in the composition root arrives in plan
11-05).

Mirrors the surfaces/evidence_cli.py controller pattern: receive parsed
arguments, call domain functions, emit deterministic UTF-8 JSON plus a
concise human summary, return an exit code. It never reimplements source
normalization, scope validation, lint, quality, retries, or writing
(11-PATTERNS.md). The author callable is injected here -- this surface stays
provider-neutral and repository-blind until plan 11-05 binds the configured
Phase 8 adapter in surfaces/cli.py::main.
"""
import json
import sys

import auditor
import authoring
import audit_writer
import model


def _print_payload(payload, summary):
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print(summary)
    return 0


def _read_source_bytes(path):
    with open(path, "rb") as fh:
        return fh.read()


def cmd_audit_source(a):
    """Normalize one source file into the versioned normalized-document
    record (AUDIT-01/D-01). Read-only: the source file is never modified."""
    try:
        raw = _read_source_bytes(a.source)
        kind = getattr(a, "kind", None) or \
            ("markdown" if a.source.lower().endswith((".md", ".markdown"))
             else "text")
        normalized = auditor.normalize_source(
            raw, source_id=a.source_id or a.source, kind=kind)
    except auditor.SourceError as exc:
        print(json.dumps({"schema_version": 1,
                          "error": {"code": exc.code, "message": str(exc)}},
                         ensure_ascii=False, indent=2))
        return 1
    except OSError as exc:
        print(json.dumps({"schema_version": 1,
                          "error": {"code": "source.unreadable",
                                    "message": str(exc)}},
                         ensure_ascii=False, indent=2))
        return 1
    return _print_payload(
        normalized,
        "%d spans, %d objective candidates from %s"
        % (len(normalized["spans"]),
           len(normalized["objective_candidates"]), a.source))


def cmd_audit_author(a, author_callable=None):
    """The bounded authoring command: build the bounded request from parsed
    arguments and the cited source, then run the closed loop. `writer`
    defaults to the production audit_writer.write_units when --state-dir and
    --write are given; the author callable remains injected until plan 11-05
    binds the configured adapter in the composition root."""
    raw = _read_source_bytes(a.source)
    kind = ("markdown" if a.source.lower().endswith((".md", ".markdown"))
            else "text")
    try:
        normalized = auditor.normalize_source(
            raw, source_id=a.source_id or a.source, kind=kind)
    except auditor.SourceError as exc:
        print(json.dumps({"schema_version": 1,
                          "error": {"code": exc.code, "message": str(exc)}},
                         ensure_ascii=False, indent=2))
        return 1

    citations = []
    for key in a.objectives:
        citations.extend(auditor.citations_for_objective(normalized, key))
    if not citations:
        print(json.dumps({"schema_version": 1,
                          "error": {"code": "request.no_citations",
                                    "message": "no cited span found for "
                                               "objectives %s in %s"
                                    % (a.objectives, a.source)}},
                         ensure_ascii=False, indent=2))
        return 1

    request = {
        "schema_version": authoring.AUTHORING_SCHEMA_VERSION,
        "objectives": a.objectives,
        "count": a.count,
        "item_types": [a.item_type],
        "citations": citations,
        "retry_cap": a.retry_cap,
        "mode": a.mode,
    }
    bank_text = open(a.bank, encoding="utf-8", newline="").read()
    config = {
        "target_path": a.bank,
        "state_dir": a.state_dir,
        "blocking_warnings": [],
        # full autonomy is an explicit CLI opt-in (--mode full), never
        # inferred from model output or a prior run (D-13, T-11-21).
        "full_opt_in": a.mode == "full",
        "approved_write_ids": list(getattr(a, "approve", []) or []),
        "caps": {"per_run": getattr(a, "cap_run", 0) or 0,
                 "per_objective": getattr(a, "cap_objective", 0) or 0},
    }
    writer = audit_writer.write_units if a.write else None

    try:
        report = authoring.run_authoring(
            request,
            author_callable if author_callable is not None
            else _no_callable(),
            bank_text, writer, config)
    except authoring.AuthoringError as exc:
        print(json.dumps({"schema_version": 1,
                          "error": {"code": "authoring.contract",
                                    "message": str(exc)}},
                         ensure_ascii=False, indent=2))
        return 1

    status = report.get("status")
    summary = "authoring %s (%d attempts, %s)" % (
        status,
        report.get("attempts", 1),
        report.get("outcome", "proposed" if status == "proposed" else "ok"))
    return _print_payload(report, summary)


def _no_callable():
    """A fail-closed placeholder: without an injected or configured author
    callable the command cannot generate; the report records the refusal and
    no writer is reached."""
    def _refuse(payload):
        return {"schema_version": 1, "items": []}
    return _refuse


def cmd_audit_undo(a):
    """The sole public undo operation (AUDIT-08/D-15): route by manifest
    backend; the caller never chooses a restore mechanism."""
    try:
        result = audit_writer.undo(a.write_id, a.bank, a.state_dir)
    except audit_writer.WriterError as exc:
        print(json.dumps({"schema_version": 1,
                          "write_id": a.write_id,
                          "error": {"code": exc.code, "message": str(exc)}},
                         ensure_ascii=False, indent=2))
        return 1
    return _print_payload(result, "write %s %s" % (a.write_id,
                                                   result["status"]))


def cmd_audit_coverage(a):
    """The citation-first coverage audit (plan 11-03): normalize the source,
    parse the exact bank, and produce the strict coverage report. Pure
    transform -- the source and bank are never modified (D-04), and a gap
    never authorizes generation (AUDIT-04)."""
    try:
        raw = _read_source_bytes(a.source)
        kind = getattr(a, "kind", None) or \
            ("markdown" if a.source.lower().endswith((".md", ".markdown"))
             else "text")
        normalized = auditor.normalize_source(
            raw, source_id=a.source_id or a.source, kind=kind)
    except auditor.SourceError as exc:
        print(json.dumps({"schema_version": 1,
                          "error": {"code": exc.code, "message": str(exc)}},
                         ensure_ascii=False, indent=2))
        return 1
    try:
        bank_text = open(a.bank, encoding="utf-8", newline="").read()
    except OSError as exc:
        print(json.dumps({"schema_version": 1,
                          "error": {"code": "bank.unreadable",
                                    "message": str(exc)}},
                         ensure_ascii=False, indent=2))
        return 1
    questions = model.parse_bank(bank_text)
    report = auditor.coverage_report(
        normalized, questions, bank_fingerprint=authoring.bank_fingerprint(
            bank_text))
    return _print_payload(
        report,
        "%d objectives, %s"
        % (len(report["coverage"]),
           ", ".join("%s=%s" % (r["objective_key"], r["state"])
                     for r in report["coverage"])))


def cmd_audit_material(a):
    """The explicit obtained-material handoff (plan 11-03 AUDIT-04/D-18):
    normalize newly supplied bytes and return a NEW bounded authoring request
    preserving exact citations. This command never calls the author or the
    writer; a gap or material pointer cannot authorize generation."""
    try:
        raw = _read_source_bytes(a.material)
        kind = ("markdown" if a.material.lower().endswith((".md", ".markdown"))
                else "text")
        request = auditor.material_request(
            raw, source_id=a.source_id or a.material, kind=kind,
            objectives=a.objectives, count=a.count,
            item_types=[a.item_type], retry_cap=a.retry_cap, mode=a.mode)
    except auditor.SourceError as exc:
        print(json.dumps({"schema_version": 1,
                          "error": {"code": exc.code, "message": str(exc)}},
                         ensure_ascii=False, indent=2))
        return 1
    except OSError as exc:
        print(json.dumps({"schema_version": 1,
                          "error": {"code": "material.unreadable",
                                    "message": str(exc)}},
                         ensure_ascii=False, indent=2))
        return 1
    return _print_payload(
        request,
        "bounded request created from %s (%d citations); no author or "
        "writer was invoked" % (a.material, len(request["citations"])))


def cmd_audit(a, author_callable=None):
    """The `itembank audit <sub>` dispatcher (registered in the composition
    root by plan 11-05). Thin argument forwarding only."""
    sub = getattr(a, "audit_command", None) or getattr(a, "sub", None)
    if sub == "source":
        return cmd_audit_source(a)
    if sub == "author":
        return cmd_audit_author(a, author_callable)
    if sub == "coverage":
        return cmd_audit_coverage(a)
    if sub == "material":
        return cmd_audit_material(a)
    if sub == "undo":
        return cmd_audit_undo(a)
    print(json.dumps({"schema_version": 1,
                      "error": {"code": "audit.unknown_subcommand",
                                "message": "audit subcommand %r unknown"
                                % sub}}, ensure_ascii=False, indent=2))
    return 2


if __name__ == "__main__":
    sys.exit(2)  # never run standalone; the composition root owns argparse
