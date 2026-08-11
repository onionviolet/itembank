# Handoff — Phase 08 (Model Adapter Interface & Tier-Gate Enforcement) closed

- **Created:** 2026-08-11
- **Phase:** 08 — model-adapter-interface-tier-gate-enforcement
- **Status:** CLOSED — 6/6 plans executed, the cross-surface release gate (`tests/model_phase_roundtrip.py`) is green, and the blocking human UAT is recorded PASS in `08-05-UAT-EVIDENCE.md`
- **Handing off to:** the next phase executor (phase 09 is a separate subject-loop stream; the milestone's active phase choice is the orchestrator's)

---

## 1. What phase 08 delivered

A provider-neutral model adapter and a runtime-owned tier gate: the tutoring model may produce error-specific hints and pending rubric suggestions, but the runtime — never the model — decides which tier may be spoken, whether a candidate may render, and whether a mark is accepted.

- `tier_gate.py` (08-01) — the deterministic fail-closed boundary: a bounded `hint_plan`/`rubric_proposal` envelope, the explicit tier fact include map (`TIER_FACTS`), always-protected key/model facts, the conservative protected-fragment ambiguity rule, whole-candidate drops with stable `gate.*` reason codes, and fixed runtime render templates. Proven against the 30+-case adversarial corpus (`fixtures/model_gate_cases.json`, `tests/model_gate_roundtrip.py`).
- `model_adapter.py` (08-02) — one typed `invoke(request, settings)` boundary behind `TRANSPORT_REGISTRY` (`hosted_cli` first per D-18, `openai_compatible` second); every failure family converts to a named `adapter.*` unavailable result and nothing raises; credentials resolve from the environment by name (`secret_env`), never the settings value, and never reach evidence.
- Evidence spine (08-03) — `model_interaction` events (descriptor-only drops: fingerprints, byte counts, reason codes; `pass_payload` only on pass) and `mark_proposal` events (per-point pending suggestions with no score/verdict field), both retrievable by session, both appended through the single `evidence.append_event` writer.
- Runtime orchestration + CLI (08-04) — `runtime.invoke_hint` / `invoke_rubric_review` sequence adapter → gate → evidence → authored fallback; `itembank hint` / `rubric-review` / `mark --proposal`; retry lineage (D-12); the machine-readable `schemas/agent_usage.schema.json` agent contract.
- Daemon routes + AgentAssist surface (08-05) — identifier-safe `/api/hint` and `/api/rubric-review` behind an authority-field 400 wall and one `SURFACE_PARITY` map; the learner assist renders as plain chrome (structural lock, pending-only rubric rows, exact UI-SPEC copy, no auto-accept control anywhere in the browser DOM); blocking human UAT recorded PASS.
- Release gate (08-06) — `tests/model_phase_roundtrip.py`: one cross-surface scenario (hosted/local parity, gate-rendered payload equality, evidence recovery, human-only proposal accept with N-boolean rubric, adversarial drop, replay idempotency), the nine-row offline matrix in stable order, the six authority regressions, the payload-boundary scan, and the contract audit with the ROADMAP criterion 1-14 mapping.

## 2. Verification & UAT

- Release gate: `python tests/model_phase_roundtrip.py` — **green** (`model phase roundtrip: ok`): full scenario, 9-row offline matrix, 6 authority regressions, 22-artifact payload scan, contract audit.
- Full suite: **42/43 green** on branch `gsd/phase-08-06`. The one failure, `packaging_roundtrip.py`, is an environment precondition: it requires the gitignored PyInstaller-frozen Windows sidecar and a working Windows-executable launcher, and the executing session's WSL interop cannot launch any `.exe` (even `python.exe` fails). `packaging_shell_roundtrip.py` passes; nothing in phase 08 touches packaging.
- Blocking human UAT: **PASS** — recorded in `08-05-UAT-EVIDENCE.md` with environment, the 8-item checklist, and revision notes (none required).
- `08-05-UAT-EVIDENCE.md` PASS is a machine-checked precondition of the release gate.

## 3. Requirements delivered

TEACH-04..TEACH-09 and MODEL-01..MODEL-05 (per the phase requirements list and the 08-06 plan `requirements` field) are proven by the plan suites and the release gate. `requirements-completed` is recorded per plan in each SUMMARY.

## 4. Open items carried forward (do not silently drop)

| Item | State | Recommended home |
|------|-------|------------------|
| `itembank bench` still owed (D-19) | Off the critical path; **no invented tok/s or latency figure may appear anywhere** — `elapsed_ms` is the only timing field; the release gate scans for violations | After the 7900 XTX hardware lands; a future bench plan |
| Raw dropped-output retrieval | D-16 ships descriptor-only audit (fingerprint, byte count, reason codes); raw transcript recovery is an OPEN item needing a separate security decision | 08-UI-SPEC "Unresolved and Do Not Build" |
| Deferred human marking / rubric decomposition (D-21) | Registered alternatives behind the one proposal interface; self-assessment ships first | A future tier-3 wave |
| Tier-3 promotability | Constant zero, structurally enforced (mark guard + no auto-accept + no fractional score) — must stay closed | Standing phase-8 boundary; assert in any future grading work |

## 5. Notes for the next executor

- The release gate is the single "is phase 08 done" answer: run `python tests/model_phase_roundtrip.py` from a checkout and read the verdict, then the full suite.
- A provider-connected pass path needs only a configured backend profile; the rendering, disclosure, and lock behaviour are asserted over the rendered template and typed payloads.
- The passing-hint fixtures in the gate use `fixtures/lesson_bank.md` (tier-0 lesson facts): the runtime rebuilds teaching records from live evidence where only SHOWN tiers persist, so tier progression in tests should unlock lesson content, exactly as `tests/model_ui_roundtrip.py` does.
- `python schema_validate.py --all` is not a CLI this repo ships; all-schema validation lives in the suites (`protocol_roundtrip`, `model_gate`, `model_adapter`, `config`, `model_surface`, and the gate's contract audit).
