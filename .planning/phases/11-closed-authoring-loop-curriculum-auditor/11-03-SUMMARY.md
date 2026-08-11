---
phase: 11-closed-authoring-loop-curriculum-auditor
plan: 03
subsystem: curriculum-auditor
tags: [coverage-engine, citation-first, normalized-document, pdf-docx-gate, weak-objective, material-handoff]

requires:
  - phase: 11-closed-authoring-loop-curriculum-auditor
    provides: plan 11-01 source primitives (auditor.py), plan 11-02 strict schemas (normalized_document/audit_report/authoring_request), 11-AI-SPEC PDF/DOCX gate, 11-VALIDATION T-11-27
provides:
  - auditor.py: coverage_report (citation-first states covered/partial/conflicting/gap/unknown + fail-closed staleness), paragraph-aware body objective candidates, blank-line spans for byte-exact reconstruction, material_request (AUDIT-04 bridge), apply_weak_priority (D-19), typed SourceError with code
  - fixtures/audit/syllabus.md + syllabus.txt: synthetic Markdown/text sources with heading/list/body objectives
  - fixtures/audit/coverage_bank.md: synthetic bank with pre-minted [ID:]/[HASH:] (3 items)
  - fixtures/audit/locator_fidelity_cases.py: 18-case deterministic PDF/DOCX gold matrix (9 PDF + 9 DOCX) with literal sha256, gold structures/reading order/unsupported lists
  - tests/audit_coverage_roundtrip.py: normalize / coverage / material cases
  - surfaces/audit_cli.py: cmd_audit_coverage + cmd_audit_material thin handlers
  - schemas: normalized_document span kind + blank; audit_report tool_version + coverage shape; authoring_request source_fingerprints (additive)
affects: [11-04 quality/retry state machine, 11-05 configured adapter + writer integration]

actuals:
  tokens: 0
  tasks: 3
  commits: 1

tech-stack:
  added: []
  patterns:
    - "Pure transform coverage engine: normalized document + parsed bank questions + optional evidence assertions in, strict audit_report out -- covered requires an exact current source-span citation AND an exact resolvable bank item id; empty/null/mismatched/stale evidence is unknown, never covered (D-02/AUDIT-03)."
    - "Per-line spans with exact char/line locators plus blank-line spans make reconstruction byte-for-byte (join spans with newlines == source text minus its terminator)."
    - "Paragraph-level body sentence detection keeps multi-line learning outcomes as candidates with a documented originating span, so objective extraction never collapses to heading scraping (AUDIT-01)."
    - "The PDF/DOCX architectural gate is immutable data: deterministic builders (hand-assembled PDFs; stdlib zipfile DOCX with fixed entry timestamps), literal gold sha256 per case, and the test asserts repeated explicit unsupported/lossy results with no spans/locators and unchanged bytes/timestamps (T-11-27)."
    - "Material and weak-objective flows structurally cannot reach an author or writer: the domain APIs accept no such argument, and the test proves it by TypeError."

key-files:
  created:
    - tests/audit_coverage_roundtrip.py
    - fixtures/audit/syllabus.md
    - fixtures/audit/syllabus.txt
    - fixtures/audit/coverage_bank.md
    - fixtures/audit/locator_fidelity_cases.py
  modified:
    - auditor.py
    - surfaces/audit_cli.py
    - schemas/normalized_document.schema.json
    - schemas/audit_report.schema.json
    - schemas/authoring_request.schema.json

key-decisions:
  - "Explicit evidence rows are validated, never trusted: an id that does not exist in the parsed bank or does not carry the objective is invalid; an empty cited id list with a valid source side is an explicit gap claim; a valid claim plus a contradictory invalid claim is conflicting; citing a subset of the covering items is partial."
  - "Stale fingerprints never yield covered: an evidence bank_fingerprint mismatch makes the row unknown and marks the report stale=True; the report records both input fingerprints so staleness is recomputable (D-04)."
  - "Blank lines are real spans (kind blank, empty verbatim) so span reconstruction is byte-exact; the split terminator line is not a span."
  - "Body objective detection joins consecutive body lines into paragraphs; the candidate's span is the paragraph's first body span (deterministic and documented)."
  - "material_request returns a new strict authoring request preserving exact citations and the new source fingerprint; it cannot invoke the author or writer, and a request for an objective absent from the material creates nothing (material.no_citations)."

patterns-established:
  - "A one-off mint script assigned [ID:]/[HASH:] into the committed coverage_bank.md; the suite never re-runs it and never mutates the fixture."
  - "The gold sha256 literals were computed once from the pure builders and frozen; a builder change fails the coverage test, which is the immutability guarantee."

requirements-completed: [AUDIT-01, AUDIT-02, AUDIT-03, AUDIT-04]

coverage:
  - id: D1
    description: "Markdown and UTF-8 text normalize deterministically with exact heading/list/body objective candidates, stable locators, verbatim spans, strict-UTF-8 failure, oversize failure, and unchanged source bytes; the complete 18-case PDF/DOCX gold matrix yields deterministic explicit unsupported/lossy results on repeated runs with no fabricated locator (AUDIT-01/T-11-27)."
    requirement: AUDIT-01
    verification:
      - kind: integration
        ref: "tests/audit_coverage_roundtrip.py#case_normalize"
        status: pass
    human_judgment: false
  - id: D2
    description: "Every objective has a deterministic covered/partial/conflicting/gap/unknown result; covered requires both exact current source-span citations and exact stable bank item ids; empty/null/mismatched/stale citations are unknown and confidence never upgrades them; a valid singleton on each side can be covered; reordered input serializes identically (AUDIT-02/AUDIT-03)."
    requirement: AUDIT-02
    verification:
      - kind: integration
        ref: "tests/audit_coverage_roundtrip.py#case_coverage"
        status: pass
    human_judgment: false
  - id: D3
    description: "Candidate materials stay inert report data (no draft/diff/manifest/authority in the coverage report); obtained material creates only a separate cited authoring request; weak-objective signals only reorder existing ids and report unknowns; author/writer are structurally unreachable from audit-only paths (AUDIT-04/D-18/D-19/T-11-08)."
    requirement: AUDIT-04
    verification:
      - kind: integration
        ref: "tests/audit_coverage_roundtrip.py#case_material"
        status: pass
    human_judgment: false

verification:
  - command: "python tests/audit_coverage_roundtrip.py"
    status: pass
  - command: "python tests/audit_roundtrip.py"
    status: pass
  - command: "python -m py_compile auditor.py authoring.py audit_writer.py surfaces/audit_cli.py tests/audit_roundtrip.py tests/audit_coverage_roundtrip.py fixtures/audit/locator_fidelity_cases.py"
    status: pass
  - note: "Original syllabus/text sources and the bank fixture are never modified; PDF/DOCX remain an explicit fixture-backed unsupported/lossy gate, not a support claim (D-03)."
