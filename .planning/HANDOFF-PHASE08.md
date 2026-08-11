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

## 6. Post-merge finalization (2026-08-11, branch `gsd/phase-08-06`)

Phase 08 executed on main (08-01..05) and this branch carried only 08-06; this branch was **behind main and never merged**, so it was finalized for merge:

- **Merge:** `git merge main` brought main's later phases (06.2 executable-textbook-loop, 09.1 audio-drill-export, and their closeouts) into the branch — 16 commits, one merge commit. The branch is now even with main (no divergence; a later merge into main is a fast-forward).
- **Merge conflict resolved:** `.planning/STATE.md` (the `last_activity_desc` line) conflicted. Resolved to **main's canonical version wholesale** — per the workspace rule, STATE/ROADMAP/config are reconciled centrally by the orchestrator after all phase branches merge; the branch's own phase-08 closure wording lives in this HANDOFF and 08-06-SUMMARY.md. `.planning/ROADMAP.md` auto-merged cleanly (no hand edit).
- **Regression found and fixed by the merge (`fix(08-06)`):** main's 06.2 merge (`d35bd15`) had silently dropped 06.2's **v3 evidence index** (the `context` column, `INDEX_VERSION=3`, context in INSERT/SELECT/row-map/fallback) while keeping 06.2's tests — so `tests/evidence_roundtrip.py` and `tests/gate_roundtrip.py` were **red on merged main** (and the release gate's authority regression failed on `evidence_roundtrip`). The fix ports 06.2's v3 index exactly (keeps both phases' behavior: phase 7's `bank` column + 06.2's `context` column); both tests and the gate's six authority regressions are green again. This is a genuine main-side defect that this branch now carries the fix for.
- **Post-merge verification (live in the worktree):**
  - Phase 8 release gate `tests/model_phase_roundtrip.py` — green section by section (the whole file exceeds the session's 2-minute command cap on this host, so the five sections were driven in-process via a scratch runner): full scenario (hosted pass, local parity, proposal + human mark, adversarial drop), 9-row offline matrix in stable order, 6 authority regressions, payload scan (22 learner-facing artifacts clean), contract audit (no auto-accept, suggestion_reveal default, human-only guard, no fractional score, no invented figures, agent_usage/COVERAGE/D-18, ROADMAP criterion 1-14 mapping all green).
  - Full suite `tests/*.py`: **45/46 files exit 0**. The single failure is `packaging_roundtrip.py`'s `test_onedir_sidecar_runs_and_is_sized` — the Windows PyInstaller sidecar build (`powershell -File scripts/build_shell.ps1`) cannot run on this WSL2-Linux host (no Windows python/interop; `dist/` is gitignored). All 14 other packaging checks pass; this is the same environment precondition already recorded in §2, not a merge regression. `packaging_shell_roundtrip.py` self-skips (`itembank-shell.exe` not built — `cargo build` on Windows). `phase_062_audit.py` was run with `--quick` (its embedded full-suite re-run is deferred to the explicit loop, which is green).
  - `python itembank.py lint fixtures/sample_bank.md` — 0 errors (6 pre-existing advisory warnings).
  - Schema validation — `itembank schema --all` emits cleanly; the CI instance flow (session/item/response/report/lint_error against live CLI output via `schema_validate.py`) conforms.
- **Human-pending (carried forward):**
  - Merge this branch into main (orchestrator action — this branch was **not** merged and **not** pushed); orchestrator reconciles `.planning/STATE.md` / `ROADMAP.md` / `config.json` centrally after all phase branches merge.
  - Build the Windows sidecar (`powershell -File scripts/build_shell.ps1` on a Windows host) whenever `packaging_roundtrip.py` must report 46/46 — recorded as an environment precondition, and it also affects upstream main/ubuntu CI today.
  - §4's open items (bench owed, descriptor-only drop audit, tier-3 stays a peer of the human marker) remain unchanged.
