# Phase 11 — Closed Authoring Loop & Curriculum Auditor — UAT

**Phase:** 11-closed-authoring-loop-curriculum-auditor
**Branch:** gsd/phase-11-auditor
**Status:** EXECUTED — every requirement has executable proof; human verification items below are the only supplementals

## User Stories (REQUIREMENTS.md) — Evidence

| Req | Acceptance criterion | Executable proof | Status |
|---|---|---|---|
| AUTH-01 | One command runs the whole authoring cycle — spec, draft, lint, feed errors back, repeat to clean or to a retry cap, write the bank — with no human relaying errors | `tests/audit_roundtrip.py --case tracer`; `tests/audit_authoring_roundtrip.py --case retry`; `tests/audit_cli_roundtrip.py --case configured-adapter` (real `python itembank.py audit author` subprocess, no DI) | ✅ |
| AUTH-02 | The loop cannot invent content beyond what it was asked to write; the model authors, the tool validates | scope-before-lint on every attempt + writer recheck (AUTH-02/T-11-01); out-of-scope/count/type/citation drafts rejected with zero writer calls; `tests/audit_authoring_roundtrip.py --case retry` | ✅ |
| AUTH-03 | A model with no repository context can complete the loop from the contract alone | repository-blind allowlist asserted over every payload (`_assert_repository_blind`); configured-adapter subprocess completes from contract+findings alone (`tests/audit_cli_roundtrip.py`) | ✅ |
| AUDIT-01 | Syllabus ingested; objectives extracted including subtleties, not only headings | `tests/audit_coverage_roundtrip.py --case normalize` (heading/list/body candidates, paragraph-level body sentences, byte-exact spans) | ✅ |
| AUDIT-02 | Objectives mapped against bank coverage; gaps reported by objective | `tests/audit_coverage_roundtrip.py --case coverage` (covered/gap rows per objective, deterministic ordering) | ✅ |
| AUDIT-03 | Every coverage claim cites its evidence; an unciteable claim is unknown, not covered | fail-closed dual-citation engine; empty/null/stale/wrong-fingerprint evidence → unknown; confidence never upgrades; `--case coverage` | ✅ |
| AUDIT-04 | Auditor points at materials that fill a gap, and absorbs them once obtained | inert candidate materials; `material_request` creates only a separate cited request; author/writer structurally unreachable; `--case material` | ✅ |
| AUDIT-05 | Autonomy is a configured range: report-only → draft-and-approve → audit-draft-lint-fix-commit (full) | three-mode domain decision (`audit_authoring_roundtrip --case stateful`) + registered CLI modes (`audit_cli_roundtrip --case modes`); identical gates/diff across modes | ✅ |
| AUDIT-06 | Every generated item passes `lint` before reaching a bank | lint gate before quality gate and before writer; lint findings as structured retry input; zero writer calls on lint failure | ✅ |
| AUDIT-07 | Second quality gate beyond lint: answer-position skew, near-duplicate stems, stem-option key leak, distractors that never say when they would be correct | exactly four named detectors with measured evidence and boundary fixtures (`tests/audit_quality_roundtrip.py`); no aggregate score | ✅ |
| AUDIT-08 | Every auditor write is reversible in one step; the tool shows what it changed before acceptance | diff in every proposal; deterministic write id; manifest-routed one-step undo (shadow restore + git revert); stale/conflict refusal; `tests/audit_writer_roundtrip.py` + `audit_cli_roundtrip.py` undo | ✅ |
| AUDIT-09 | At the highest autonomy setting the tool reports its own volume | proposed/completed/rejected/retried/written + per-objective volume on every exit; `--case stateful` and `--case modes` | ✅ |

## Supplemental Human Verification (per 11-VALIDATION.md)

These are experiential checks that remain for the repository operator; the automated authority for each behavior is listed beside it.

| Behavior | Test instructions | Automated authority |
|---|---|---|
| Approval flow communicates the exact proposed diff | Run `itembank audit author --mode draft_and_approve` against a temp synthetic bank; reject once and approve once; confirm only the exact approved write id changes the copy | `tests/audit_cli_roundtrip.py --case modes` |
| Citation and locator fidelity understandable | Inspect one Markdown body-level objective and one table-like source span against original bytes; inspect representative PDF/DOCX results (explicit unsupported, no invented locator) | `tests/audit_coverage_roundtrip.py --case normalize` |
| Model-unavailable report-only flow remains usable | Unconfigure the Phase 8 profile (empty active), run report-only authoring, confirm request/findings/source/report/diff remain readable and no write/approval is offered | `audit_cli_roundtrip.py` (malformed → structured retry → retained report, zero writes) |
| Writer and one-step undo communicate backend and conflict | On temp tracked-clean and shadow fixtures, review exact diff/write id/backend/manifest, apply once, undo once, then create a stale/conflicting edit and confirm undo refuses without changing human bytes | `tests/audit_writer_roundtrip.py` |

## PDF/DOCX Architectural Gate

- 9 PDF + 9 DOCX deterministic gold fixtures in `fixtures/audit/locator_fidelity_cases.py` (literal sha256, gold structures/reading order/unsupported lists).
- Current registry returns the same explicit `source.adapter_unregistered` result on repeated runs, with no spans/locators, no AI call, and unchanged bytes/timestamps.
- PDF/DOCX remain unsupported until a future adapter proves exact round-trips for every claimed structure; no confidence or AI-SPEC waiver exists.

## Acceptance

- All twelve plan tasks have a passing automated gate; the two preconditions for 11-05-01 are recorded as satisfied.
- The D-15 one-way checkpoint (11-05-02) resolved to **proceed**.
- No UI/daemon route was introduced (UI-BLOCKED per 11-UI-SPEC); the CLI is the sole Phase 11 surface.
