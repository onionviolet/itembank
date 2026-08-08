# Phase 11: Closed Authoring Loop & Curriculum Auditor - Discussion Log

> **Audit trail only.** Decisions are in CONTEXT.md.

**Date:** 2026-08-08
**Areas discussed:** Source ingestion, citations, authoring retry loop, second quality gate, autonomy, reversibility, coverage-to-draft flow

| Area | Alternatives considered | Selected |
|------|--------------------------|----------|
| Source formats | Promise all formats vs stable adapter contract with guaranteed text/Markdown | Adapter contract; fidelity-gated extras |
| Coverage | Confidence-only vs citation-per-claim with unknown state | Citations and unknown |
| Authoring | Human relays lint vs closed machine-readable retry loop | Closed loop |
| Quality | Lint only vs separate explainable detectors | Separate multi-detector gate |
| Autonomy | Separate pipelines vs one pipeline with permission levels | One pipeline, three levels |
| Undo | Git only vs shadow only vs one abstraction over both | Backend chosen by bank tracking |

**User's choice:** Delegated with instruction to preserve compatible choices, avoid unnecessary human stoppage, and reserve important UI/design work for stronger pre-implementation planning.

## Codex's Discretion

Similarity algorithms, thresholds, PDF/DOCX scope, and audit UI are assigned to research and planning. Full autonomy remains explicitly opt-in because it is the only materially risky mode.

## Deferred Ideas

Lossy document ingestion, unbounded curriculum invention, and hosted storage are excluded.
