# HANDOFF — Phase 09 (subject-invariant-loop-emt-math-cs-integration)

**Status: EXECUTED — all five plans done; one HUMAN gate open (KaTeX approval).**
**Branch:** `gsd/phase-09-subject-loop` — worktree `C:\Users\wayba\Downloads\CTF\itembank\.phase09-wt`
**Branched from:** main (merge `0ce8a2c`) and Phase 5 (merge `8c9ddf3`); 3 phase-09 commits on top (`fbd4f82`, `941c907`, `0ed3783`). Not merged into main, not pushed — the orchestrator reconciles merges centrally.
**Handed off:** 2026-08-11 (close)

---

## 1. What is done (committed on this branch)

| Commit | Plan | Content |
|---|---|---|
| `0c2ec94` | 09-01 | `subjects.py` (selector/registry/snapshot), session schema v3, do_start snapshot persistence, EMT semantic table wrapper, EMT tracer tests, AST dispatch guard |
| `a6fdba6` | 09-02 | `subject_profiles` settings registry (emt/math/cs shipped), `lesson_layout` enum, configuration-only fourth profile, registry-parity tests |
| `238782f` | 09-03 | KaTeX supply-chain gate record — **PENDING HUMAN APPROVAL** (metadata-only verification; no bytes at that point) |
| `cee3d18` | 09-04 | Vendored KaTeX 0.18.4 (browser distribution + 60 fonts + LICENSE), closed `/assets/katex` route map, lesson-scoped math adapter, `tests/math_offline_roundtrip.py` |
| `0ce8a2c` | merge(main) | Brought main's 3.1/6.1/6.2/8-05/9.1/10 into the branch; 8 conflicts resolved keeping both phases' behavior (session carries `subject_profile` + `retention`; daemon merges KATEX + gate helpers + `/api/export_audio`; lesson_page(profile, gate, focus, announce); settings schema union; THIS_PHASE 10) |
| `8c9ddf3` | merge(phase-05) | The handoff-mandated merge of `gsd/phase-05-check` (its 2 human checkpoints remain PENDING on that branch). Conflicts + latent fixes: `visual_interaction_result` rename (main's visual normalizer) so Phase 5's `interaction_result` keeps the shared name; `check` settings group + `subject_profiles` coexist; `visual` added to profile allowlists; `_log_unreachable` no longer creates `_evidence/` on lesson GET (D-08); evidence index `context` column (main-side latent 06.2 gap, INDEX_VERSION 3); T-R4-01 hash re-pinned to the merged visual-capable scorer; keydown no-leak scan scoped for Phase 5's public per-case reason |
| `fbd4f82` | 09-05 T1 | `runner.run_source()` (one process primitive, stderr + exit_code, None on deadline-kill); `execution_refusal()` + `/api/lesson/run` (exactly {session_id, block_id, language, source}, profile/settings/LAN/source gates before one run, observation-only response); runnable-code UI (data-code-block ids, Run control, exact 09-UI-SPEC copy, static/disabled/LAN states); `tests/lesson_code_roundtrip.py`; route pins 10→11 |
| `941c907` | 09-05 T2 | `--subject-profile` on start/lesson, `/api/start` `profile` id, `/lesson?profile=`, `do_start(profile_id=None)`; only the id crosses a client boundary; unknown/mixed fail before writes path-free; resume uses the stored snapshot |
| `0ed3783` | 09-05 T3 | `fixtures/subject_loop_{emt,math,cs}.md`; one table-driven `run_subject_case()` over the real start/action/hint APIs for EMT/Math/CS/fourth; identical transitions (hold → reveal_tier → complete), cursor progression, tier-0 hint, evidence spine, outcome; check-item hints unblocked (check-source branch runs only for submit actions) |

## 2. What remains OPEN (human)

1. **09-03 KaTeX supply-chain approval — PENDING HUMAN APPROVAL.** Recorded in
   `09-03-SUMMARY.md` (`approved: false`; resume signal `approved katex=0.18.4`)
   and `09-VERIFICATION.md`. 09-04 was executed with the vendored bytes'
   integrity machine-verified (npm sha512
   `IMPntbRLOU+eu88XDiFKqQ8Akhr9Tv7jDMXqPhjG9SI1JMA4DIgXk4x9k4skJz2NZJXBRbC+2pYBLj9olqcZow==`,
   sha256 computed at fetch `0090b1ebccc77d1402ec95e85ee539e1da514d6cd6934156c00baf39dcb0e3aa`);
   the HUMAN approval itself is NOT recorded as given. A human must reply
   `approved katex=0.18.4` (or refuse) for the phase to be fully approved.
2. **Manual accessibility/responsive matrix** (09-VALIDATION.md): 320 CSS px /
   200% zoom, keyboard-only flow, assistive table/MathML, light/dark,
   reduced-motion, network-unplugged packaged page, one wrong → hint → retry
   flow per shipped subject. The automated hooks/copy are asserted; the
   human observation pass is owed.

## 3. Verification summary (this branch)

- Phase-gate commands all exit 0: `tests/subject_loop_roundtrip.py`,
  `tests/math_offline_roundtrip.py`, `tests/lesson_code_roundtrip.py`,
  `tests/check_roundtrip.py`, `tests/hint_roundtrip.py`,
  `tests/scoring_roundtrip.py`, `tests/daemon_roundtrip.py`,
  `tests/lesson_roundtrip.py`, `tests/config_roundtrip.py`,
  `tests/evidence_roundtrip.py`, `tests/gate_roundtrip.py`,
  `tests/model_ui_roundtrip.py`, `tests/visual_roundtrip.py`,
  `tests/visual_authoring_roundtrip.py`, `tests/retention_roundtrip.py`,
  `tests/pacing_roundtrip.py`, `tests/day_roundtrip.py`,
  `tests/serve_roundtrip.py`, `tests/agent_roundtrip.py`,
  `tests/protocol_roundtrip.py`, `tests/phase10_uat.py`,
  `tests/lesson_retention_roundtrip.py` (full list in 09-VERIFICATION.md).
- `python itembank.py lint fixtures/sample_bank.md` — 0 errors.
- `python schema_validate.py` — contract self-contained and stable.
- `packaging_roundtrip.py` — `.pyz` portion passes; the Phase 13-03 frozen
  sidecar-exe handshake is **environment-blocked** in this WSL bash (cannot
  exec the Windows PE sidecar); unrelated to this diff.

## 4. Merge notes for the orchestrator

- The branch is behind main only by whatever landed after `2b5678c`; it is
  currently up to date with that main tip and carries Phase 5's runner. When
  Phase 5 is itself merged to main, git reconciles (identical content).
- `subjects.py` and `vendor/katex/` are branch-only files (main lacks them);
  the merge to main must keep them.
- `.planning/STATE.md` on this branch is main's version (orchestrator-owned —
  this branch did not edit it); ROADMAP/REQUIREMENTS/config.json untouched.
- Session schema v3 carries both `subject_profile` (phase 09) and
  `retention` (phase 10) — both auto-merged cleanly.

## 5. Files awaiting nothing

- All plan outputs are committed. The only follow-ups are the two human
  items in §2 (KaTeX approval + manual accessibility/responsive matrix).
