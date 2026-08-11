---
phase: 11-closed-authoring-loop-curriculum-auditor
plan: 02
subsystem: closed-authoring-loop
tags: [json-schema, strict-contracts, version-parity, quality-finding, write-manifest]

requires:
  - phase: 11-closed-authoring-loop-curriculum-auditor
    provides: plan 11-01 tracer runtime payloads (11-01-SUMMARY.md), 11-PATTERNS schema analog (lint_error/report/update_manifest), schema_validate SUPPORTED keyword subset
provides:
  - schemas/authoring_request.schema.json: strict bounded-request contract (objectives, count, item_types, exact citations, retry_cap, mode, per_objective_cap)
  - schemas/normalized_document.schema.json: strict locator-faithful source record (spans with heading path / line+char locators / verbatim, objective candidates)
  - schemas/quality_finding.schema.json: strict named-detector finding contract (four detectors, per-detector evidence oneOf, no aggregate score)
  - schemas/audit_report.schema.json: strict run/coverage report contract (proposal, findings groups, manifest, coverage rows, volume records, staleness)
  - schemas/write_manifest.schema.json: strict write provenance/recovery/undo contract (deterministic write id, backend, state, units, before/after fingerprints, provenance)
  - tests/audit_roundtrip.py --case schemas: runtime-version parity, accepted/rejected payload cases, stable ordering
  - authoring.py: answer-leak evidence run serialized as a JSON array (tuple -> list) so the strict evidence oneOf validates
affects: [11-03 coverage engine consumes normalized_document/audit_report, 11-04 quality profile consumes quality_finding, 11-05 writer consumes write_manifest]

actuals:
  tokens: 0
  tasks: 2
  commits: 1

tech-stack:
  added: []
  patterns:
    - "Every Phase 11 public payload declares schema_version equal to the schema's x-itembank-version, enforced by the parity test (T-11-22)."
    - "Strict documents use only the schema_validate SUPPORTED keyword subset ($defs/$ref local, oneOf, enum, const, min/max); check_schema refuses any unsupported keyword before an instance is examined."
    - "Detector-specific evidence is a oneOf over four strict evidence shapes with additionalProperties false, so measured values are required per detector and an opaque aggregate score cannot be smuggled in (D-10)."
    - "The audit report is the strict union of run states (proposed/written/failed/already_completed) plus the coverage-audit fields (covered/partial/conflicting/gap/unknown/stale rows, volumes, staleness) -- unknown keys fail everywhere."

key-files:
  created:
    - schemas/authoring_request.schema.json
    - schemas/normalized_document.schema.json
    - schemas/quality_finding.schema.json
    - schemas/audit_report.schema.json
    - schemas/write_manifest.schema.json
  modified:
    - tests/audit_roundtrip.py
    - authoring.py

key-decisions:
  - "One strict union schema for audit_report rather than separate run/coverage schemas: every report shares the top-level provenance keys, and the coverage/volume/staleness fields are declared from the start so plans 11-03/11-04 consume a stable contract without reinterpreting D-02/D-04/D-13."
  - "The findings.records union shape (record $def) accepts scope/lint/quality records with the shared code/field/item/message/detector/evidence keys; quality records embedded in reports keep their schema_version and full finding shape."
  - "The manifest schema declares backend enum [shadow, git], state [prepared, applied, reverted], before_exists for newly created report artifacts, and git_commit for the Git backend, with no caller-selected backend or restore bypass (T-11-24)."
  - "The quality_finding evidence oneOf forced the answer-leak detector to serialize its run as a JSON array (tuples are not JSON), aligning the runtime payload with the strict contract."

patterns-established:
  - "resources.read_text loads the schemas in tests, matching the model_adapter resource seam so the suite also works from a .pyz."
  - "sv.check_schema runs first in the test, so an unsupported keyword fails loudly before payload validation (schema_validate's own contract)."

requirements-completed: [AUTH-01, AUTH-02, AUTH-03, AUDIT-06, AUDIT-07, AUDIT-08]

coverage:
  - id: D1
    description: "All five public payload families are strict, schema-versioned, machine-readable, and validated with the existing stdlib validator; unknown and missing required fields fail (T-11-22)."
    requirement: AUTH-01
    verification:
      - kind: integration
        ref: "tests/audit_roundtrip.py#case_schemas (accept + reject cases)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The repository-blind spy author still receives only the public format contract, bounded request, attempt number, and structured findings after schema publication; the tracer case remains green with the AUTH-03 allowlist assertions intact (T-11-23)."
    requirement: AUTH-03
    verification:
      - kind: integration
        ref: "tests/audit_roundtrip.py#case_tracer"
        status: pass
    human_judgment: false
  - id: D3
    description: "The report and manifest schemas require gate/volume/unit/backend/diff/fingerprint/provenance data with no unsafe restore selector; missing or extra report/manifest fields fail (T-11-24, D-15/D-16/D-17)."
    requirement: AUDIT-08
    verification:
      - kind: integration
        ref: "tests/audit_roundtrip.py#case_schemas (extra_manifest restore_anyway rejection)"
        status: pass
    human_judgment: false

verification:
  - command: "python tests/audit_roundtrip.py --case schemas"
    status: pass
  - command: "python tests/audit_roundtrip.py --case tracer"
    status: pass
  - note: "No package, ORM migration, PDF/DOCX adapter, daemon route, frontend asset, or live model introduced (plan 11-02 verification)."
