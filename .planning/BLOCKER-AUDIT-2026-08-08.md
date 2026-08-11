# Phase UI Contract Blocker Audit — 2026-08-08

Scope: Phases 06.1, 8, 9, 10, and 11. Each item is assigned exactly one required class.

| Phase | Blocker / apparent blocker | Class | Disposition / clearing action |
|---|---|---:|---|
| 06.1 | Missing `CONTEXT.md` | 1. already resolved by prior context | Research and approved UI authority already fixed all in-scope choices. Captured in `06.1-CONTEXT.md`; execute the vertical tracer first. |
| 06.1 | Learner renderer completion | 5. implementation or verification gate | Execute 06.1-01 -> 06.1-02 -> 06.1-03 and pass visual roundtrip, evidence, accessibility, GIFT, keyboard/touch/SR/reflow checks. |
| 06.1 | Concrete Phase 8 phrasing | 5. implementation or verification gate | 06.1 consumes only typed bounded feedback; phrasing is not required for the deterministic tracer. Phase 8 later proves it. |
| 8 | Missing `08-AI-SPEC.md` | 3. missing AI design contract | Created and completeness-checked in this reconciliation. |
| 8 | Tier/fact seam and leakage detector | 4. missing research or architectural proof | The architecture is locked but no implementation proof exists. Plan Phase 8 around a permitted/reserved fact manifest, strict structured output, whole-candidate drop, and adversarial corpus. |
| 8 | Generated learner support | 5. implementation or verification gate | Remains blocked until Phase 6 entitlement integration and all adversarial/offline/backend-parity suites are green. Adapter/schema work can proceed independently. |
| 9 | KaTeX immutable release/checksum approval | 6. external/human execution checkpoint | Preserve blocking checkpoint in `09-03`; never auto-approve. Execute 09-01 and 09-02 independently first, then human-verify 09-03 before 09-04. |
| 9 | Upstream Phase 3/5/6 contracts and KaTeX bytes | 5. implementation or verification gate | Run upstream phase suites; after 09-03 approval execute 09-04 and 09-05. Unavailable fallbacks are honest but do not satisfy completion. |
| 10 | Derivation/evidence snapshot design | 1. already resolved by prior context | Context/research/UI contract already fix separate itembank/Anki signals, explicit evidence, uncertainty, and rule-based recommendations. Do not re-ask. |
| 10 | Report, pacing, recommendation surfaces | 5. implementation or verification gate | Create Phase 10 plans, execute upstream derivation first, then UI surfaces and global/phase UI validation. |
| 11 | Missing `11-AI-SPEC.md` | 3. missing AI design contract | Created and completeness-checked in this reconciliation. |
| 11 | PDF/DOCX locator fidelity | 4. missing research or architectural proof | Required fixture matrix and evidence are specified in `11-AI-SPEC.md` and `11-03-PLAN.md`. Until proven, Markdown/plain UTF-8 only; PDF/DOCX fail explicitly. |
| 11 | Phase 8 configured adapter | 5. implementation or verification gate | Plans 11-01..11-04 may proceed independently. Plan 11-05-01 waits for Phase 8 artifacts/tests. |
| 11 | Git versus shadow one-way writer contract confirmation | 6. external/human execution checkpoint | Preserve `11-05-02` as the blocking human checkpoint immediately before persisted writer work. |
| 11 | Browser review/write UI | 5. implementation or verification gate | CLI/domain work may proceed; browser preview/diff/approval/publish/revert waits for approved UI fixtures and no-key checks. |

## Genuine Unresolved Human Decisions

None were discovered in the design contracts. The two remaining human stops are execution checkpoints, not preference questions: Phase 9 KaTeX release/checksum approval and Phase 11 writer one-way-door confirmation.

## AI-SPEC Completeness Verdicts

- `08-AI-SPEC.md`: **PASS** — classification, domain rubrics, framework rationale, entry pattern, Pydantic parity example, eval matrix, reference dataset, guardrails, and local tracing override are present.
- `11-AI-SPEC.md`: **PASS** — all required sections are present; source fidelity and deterministic writer/quality contracts remain explicitly outside AI authority; PDF/DOCX fixture proof is specified.

## Recommended Clearing Order

1. `$gsd-execute-phase 06.1` — begins with `06.1-01` vertical tracer; complete all 06.1 verification gates.
2. `$gsd-plan-phase 8` — consume `08-CONTEXT.md`, `08-RESEARCH.md`, `08-UI-SPEC.md`, and `08-AI-SPEC.md`; then `$gsd-execute-phase 8`.
3. `$gsd-plan-phase 10` — upstream deterministic derivation/evidence work can run while Phase 8 is underway; execute before Phase 11 weak-objective refinement.
4. `$gsd-execute-phase 9` — execute 09-01/09-02, stop only at the required 09-03 human release approval, then execute 09-04/09-05.
5. `$gsd-execute-phase 11` — execute 11-01 through 11-04 independently; after Phase 8 is green execute 11-05-01, retain 11-05-02 human confirmation, then 11-05-03.

No production functionality was implemented by this audit.
