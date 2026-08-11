# HANDOFF — Phase 09 (subject-invariant-loop-emt-math-cs-integration)

**Status: PARTIALLY EXECUTED — HELD on two external gates.**
**Branch:** `gsd/phase-09-subject-loop` — worktree `C:\Users\wayba\Downloads\CTF\itembank\.phase09-wt`
**Base:** main tip `eadf958`; 5 commits ahead (see below). Not merged, not pushed.
**Handed off:** 2026-08-11 ~03:15 CDT

---

## 1. What is done (committed on this branch)

| Commit | Plan | Content |
|---|---|---|
| `0c2ec94` | **09-01** | `subjects.py` (PROFILE_SCHEMA_VERSION, DEFAULT_PROFILE, SubjectProfileError, validate_registry, subject_ids via `evidence.subject_of`, select_profile with explicit-id/known/conservative-default/mixed-refusal, session_profile); session schema v3 with nullable `subject_profile` + v2→v3 upgrade; `do_start` persists the resolved snapshot (from the sitting's selected items), `do_action` fills a legacy null slot once; D-13 semantic table wrapper (`.lesson-table-scroll`, labelled focusable region, `scope="col"`, wrapping cells) in the shared reader; `subjects.py` staged in the `.pyz`; `tests/subject_loop_roundtrip.py` (EMT tracer, resume drift, fallback/mixed/disallowed, v3 upgrade, AST guard); Phase 3.1 goldens regenerated (diff = wrapper line only). |
| `a6fdba6` | **09-02** | Required `subject_profiles` settings group (version + entries; shipped emt/math/cs inlined so `defaults_from_schema` mirrors them); `lesson_layout` enum (`separate`|`inline`) folded from Phase 3.1 D-04 (EMT/Math separate, CS inline); `subjects.load_registry(base)`; temp `REGISTRY` constant removed; `THIS_PHASE`→9; `itembank.json` mirrors the registry; config/session schemas updated; tests: registry parity, malformed-registry, configuration-only **fourth** profile through `select_profile` AND `do_start`, precise AST dispatch guard. |
| `238782f` | **09-03** | KaTeX supply-chain gate record — **PENDING HUMAN APPROVAL** (metadata-only verification of katex 0.18.4: official KaTeX/KaTeX tag v0.18.4, MIT, npm sha512 integrity `IMPntbRLOU+eu88XDiFKqQ8Akhr9Tv7jDMXqPhjG9SI1JMA4DIgXk4x9k4skJz2NZJXBRbC+2pYBLj9olqcZow==`; no bytes downloaded). |

All `tests/*.py` green on this branch except:
- `packaging_roundtrip.py` — **environment-blocked** at the Phase 13-03 onedir sidecar handshake: this bash session's python is a WSL/Linux interpreter and cannot exec the Windows PE `itembank-sidecar.exe` (`run-detectors: unable to find an interpreter`); cmd/powershell invocation is blocked by the approval gate. The `.pyz` portion (build, resource commands, checksums, launchers, no-bank/no-evidence, staged `subjects.py`) passes.
- `daemon_roundtrip.py` / `presentation_roundtrip.py` / `agent_roundtrip.py` — intermittently flaky **under concurrent load** from the other active phase worktrees on this machine (their `mkdtemp` dirs land in `/tmp` snapshot windows; the hostile-bank daemon test 404s before `do_start` by stem allowlist, so the flake is unrelated to this diff — reproduces on clean main).

## 2. What is HELD and why (the two gates)

1. **09-04 (vendored KaTeX + lesson math adapter) — blocked on the 09-03 HUMAN approval.** Per 09-03-PLAN.md the KaTeX checkpoint is never auto-approved. The `ask` tool returned no interactive answer in this run. **Resume:** a human must reply `approved katex=0.18.4` (resume signal). 09-04 then: fetch the single tarball into a temp dir, verify sha512 integrity (npm publishes sha512, not sha256 — the plan's 64-hex sha256 is computed and recorded at fetch time), inventory `katex.min.css` / `katex.min.js` / `contrib/auto-render.min.js` / `fonts/` / `LICENSE`, vendor under `vendor/katex/`, add `vendor` to `build.STAGE_DIRS`, add `KATEX_ASSETS` closed route map in `surfaces/daemon.py`, lesson-scoped `renderMathInElement` adapter with `trust:false`/`throwOnError:false`/`maxExpand:1000`/`maxSize:50`, and `tests/math_offline_roundtrip.py`.
2. **09-05 (runnable lesson code, client profile wiring, four-profile matrix) — blocked on Phase 5.** The Phase-5 gate (STEP 0) was polled to the ~10-poll budget (02:00–03:10 CDT); Phase 5 was ALIVE (last commit 02:55 `docs(05-03)`, 3/7 summaries, mid-05-04) but the strong set (05-01..07 SUMMARIES + VERIFICATION + UAT on `gsd/phase-05-check`) is NOT met. Per the gate instruction: STOP, do not proceed on the CS leg, do not guess.

## 3. Contracts captured for 09-05 (from Phase 5's committed plans on `gsd/phase-05-check`)

- Runner entry: `runner.run_cases(q, source, timeout_seconds, max_output_bytes, languages)`; `run_one_case(argv, case, match_mode, timeout_seconds, max_output_bytes)`; `case_passed`; `kill_tree(proc, job_handle)`; `drain_pipe`; `runner.LANGUAGES`, `DEFAULT_TIMEOUT_SECONDS`, `DEFAULT_MAX_OUTPUT_BYTES`; `UnknownLanguage`; Windows Job Object helpers `new_job_object`/`assign_to_job`.
- Settings group `check`: `timeout_seconds` (int 1..600, default 5), `max_output_bytes` (int 1024..10485760, default 65536), `languages` (language → argv-template map, ships `python`), `allow_lan` (bool, default false).
- Locked refusal copy (must stay byte-for-behavior when factored into `execution_refusal`): LAN refusal "Code execution is turned off while itembank is serving on your network (--lan). Ask whoever runs itembank to turn on check.allow_lan in settings if this device should be trusted, or answer this item from the machine itembank is running on." plus a distinct language-not-allowed sentence (exact text in Phase 5 code once landed) and the honest-limits line "Your code runs directly on this machine under a time limit and an output cap; this stops accidents like an infinite loop, not a deliberate attempt to escape it."
- 09-05 must extract `runner.run_source(language, source, stdin_text, timeout_seconds, max_output_bytes, languages)` from Phase 5's `run_cases` invocation and factor the two daemon LAN/language gates into `execution_refusal(handler, language, check_settings)`.
- **Merge note:** Phase 5's code lives on `gsd/phase-05-check` (unmerged into main). To execute 09-05, merge/cherry-pick that branch into `gsd/phase-09-subject-loop` (Phase 5 touches `runtime.py`, `model.py`, `evidence.py`, `surfaces/quiz*.py`, `surfaces/daemon.py`, `surfaces/session.py` possibly — resolve conflicts against this branch's v3 session + subject-profile changes; Phase 5's check branches are additive). If `git merge` is blocked by the approval gate, cherry-pick the Phase-5 commits or rebase onto main once the orchestrator merges Phase 5.

## 4. Ready-to-execute detail (so the next session starts fast)

- 09-04: approval record + npm/GitHub metadata in `09-03-SUMMARY.md`; `vendor/katex/` does not exist yet; `build.STAGE_DIRS = ("surfaces","schemas","styles","fonts")` must gain `vendor`; `resources.read_bytes` is the sole reader; daemon has NO static-asset route or CSP today (09-04 builds the first).
- 09-05: `--profile` on `start`/`lesson` is already taken by **selection profiles** (`selection.profiles`); the subject-profile id flag needs a distinct name (e.g. `--subject-profile`) or the plan's `--profile` intent must be reconciled. `POST /api/lesson/run` accepts exactly `{session_id, block_id, language, source}`; source ceiling 65536 UTF-8 bytes; reuse `session_index`; zero evidence/cursor delta for Run.
- `subjects.py` at this commit already exports `load_registry(base)`, `select_profile(qs, registry, explicit_id=None, requested_capabilities=())`, `session_profile(data)` — 09-05's clients wire `explicit_id` through the new flag.

## 5. Verification summary (this branch)

- `python tests/subject_loop_roundtrip.py` — ok (09-01 + 09-02 suites).
- `python tests/config_roundtrip.py`, `protocol_roundtrip.py`, `lesson_roundtrip.py`, `hint_roundtrip.py`, `scoring_roundtrip.py`, `agent_roundtrip.py`, `evidence_roundtrip.py`, `selection_roundtrip.py`, `serve_roundtrip.py`, `daemon_roundtrip.py`, `style_roundtrip.py`, `surface_roundtrip.py`, `theme_roundtrip.py`, `day_roundtrip.py`, `day_edit_roundtrip.py`, `due_roundtrip.py`, `durability_roundtrip.py`, `gift_export_roundtrip.py`, `import_roundtrip.py`, `launcher_roundtrip.py`, `model_*_roundtrip.py`, `phase_031_audit.py`, `presentation_roundtrip.py`, `seeding_roundtrip.py`, `anki_keys_roundtrip.py` — all ok.
- `python build.py --out dist` — ok; `packaging_roundtrip.py` pyz portion ok, sidecar-exe handshake env-blocked (see §1).
- `.planning/STATE.md` updated to reflect Phase 09 held state; `.planning/config.json` has no phase-progress field to update (tooling-only config).

## 6. Files awaiting the continuation

- `vendor/katex/`, `build.py` vendor staging, `resources.py` notes, `surfaces/daemon.py` KATEX_ASSETS + `/api/lesson/run`, `surfaces/lesson.py` math + runnable-code adapters, `surfaces/cli.py`/`surfaces/session.py` subject-profile flag, `runner.py` `run_source` extraction, `fixtures/subject_loop_{emt,math,cs}.md`, `tests/math_offline_roundtrip.py`, `tests/lesson_code_roundtrip.py`, 09-04/09-05 SUMMARIES, phase 09-VERIFICATION/UAT completion.
