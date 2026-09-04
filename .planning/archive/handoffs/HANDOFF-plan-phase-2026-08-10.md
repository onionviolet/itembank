# Handoff — `/gsd-plan-phase 3.1 and the rest that needs it`

- **Created:** 2026-08-10
- **Handing off from:** Claude (planning session, stopped on usage limits)
- **Handing off to:** DeepSeek V4
- **Reason for handoff:** Claude usage exhausted mid-run. This is a *planning* handoff, which is a
  departure from `PLANNING-DIRECTIVES.md` §5 ("Claude plans, DeepSeek V4 executes"). Recorded here so
  it is a visible, deliberate exception and not a silent drift.
- **GSD state is shared on disk.** Nothing needs exporting. Pick up from the "Next action" section.

---

## 1. What the run was doing

Five phases have a `CONTEXT.md` and zero `PLAN.md`. They are the complete answer to "3.1 and the
rest that needs it":

| Phase | Name | UI-SPEC | Research | Patterns | Validation | Plans |
|---|---|---|---|---|---|---|
| 03.1 | Lesson Rich Blocks, Glossary & Style | ✅ approved | ✅ | ✅ | ✅ seeded | ❌ |
| 03.2 | Seeding, Import & Provenance | ❌ **gate blocks** | ❌ | ❌ | ❌ | ❌ |
| 06.2 | Executable Textbook Loop | ✅ approved | ✅ | ❌ | ✅ seeded | ❌ |
| 09.1 | Audio Drill Export | ❌ (skip-ui, see §3) | ❌ | ❌ | ❌ | ❌ |
| 13 | Desktop Packaging — Tauri Sidecar | ✅ approved | ❌ | ❌ | ❌ | ❌ |

Phases `999.1` and `999.4` are backlog slots with no CONTEXT.md and are **out of scope** — do not plan them.

## 2. What completed, and what did not

**Committed by this session:**

- `3d84101` — `03.1-RESEARCH.md`
- `712dae8` — `06.2-RESEARCH.md`

**Written but uncommitted at handoff:** `03.1-PATTERNS.md`, `03.1-VALIDATION.md`, `06.2-VALIDATION.md`.

**Interrupted, produced nothing:** research agents for **3.2, 9.1, and 13**, and the pattern mapper
for **6.2**. Their prompts are preserved in §6 below — re-issue them verbatim rather than rewriting.

**Never started:** every `gsd-planner` and `gsd-plan-checker` spawn. No plan has been written for any
of the five phases.

## 3. Decisions already made — do not re-litigate

These were settled under `PLANNING-DIRECTIVES.md` §2 (decide, record, keep going).

1. **9.1 gets `--skip-ui`.** The UI gate reports `frontend: true`, which is a false positive.
   `09.1-CONTEXT.md` D-14 refuses a player, sync service, mobile build, and playback position, and
   the only user-facing text is CLI refusal copy already locked by D-04, D-05, and D-16.
2. **3.2 needs a UI-SPEC before planning.** The gate blocks correctly here. ROADMAP criterion 8 says
   authoring is a batch operation and "the UI must say so", and the human-gated approve-one-at-a-time
   seeding loop is a real surface. Run `/gsd-ui-phase 3.2` before `/gsd-plan-phase 3.2`.
3. **Codebase drift is non-blocking at plan time.** The map is stale against `.claude/`,
   `.gitattributes`, `build.py`, `evidence.py`, `itembank.json`, `launchers/`, `resources.py`,
   `schema_validate.py`, and `schemas/`. Worth a `/gsd-map-codebase` **before execution**, not before
   planning.
4. **Spec-less probe fallback: the deterministic edge probe is skipped, visibly, for all five
   phases.** Its own gate refuses to run without requirement IDs, and all five phases carry
   `Requirements: TBD` (see §4). The prohibition-recall half (`references/specless-probe-fallback.md`
   §B) is an in-prompt planner pass and **still applies** — each planner must run it *after* it
   assigns requirement IDs. Record the skip in each PLAN.md; never let it be silent.
5. **Plan 3.1 before 6.2.** 6.2's research is MEDIUM confidence precisely because it depends on
   3.1's `[!CHECK:]` grammar, which does not exist yet. 6.2's planner should read 3.1's finished
   PLAN.md files.

## 4. The cross-cutting problem you are inheriting

**All five phases have no requirement traceability.** `ROADMAP.md` records
`**Requirements**: TBD (assign at /gsd-plan-phase <N>)` for each, and `REQUIREMENTS.md`'s Traceability
table has no rows for 3.1, 3.2, 6.2, 9.1, or 13.

Each planner must therefore do three things the normal flow does not ask of it:

1. Assign requirement IDs — either claim existing unmet IDs, or mint new ones in an existing namespace.
2. Update `REQUIREMENTS.md`'s Traceability table with the new rows.
3. Replace the `**Requirements**: TBD (…)` line in that phase's `ROADMAP.md` section.

Recommendations already produced by research:

- **03.1** — mint `LESSON-07` through `LESSON-17` (11 new IDs). Do **not** reuse the Pending
  `LESSON-02` / `LESSON-03` / `LESSON-05`; those describe already-shipped Phase 3 grammar.
- **06.2** — mint a new `GATE-01..06` namespace. No existing ID fits.
- **03.2, 09.1, 13** — no recommendation yet; their research never ran. `DEL-*` looks likely for 13.

## 5. Findings that change the plans — carry these forward

**From `03.1-RESEARCH.md` and `03.1-PATTERNS.md`:**

- Three prerequisites are **uncosted by the phase criteria as written**:
  1. `surfaces/lesson.py:242-308 _render_blocks()` has **zero** blockquote/`[!...]` parsing today.
     `[!KEY]`, `[!EXAMPLE]`, and `[!CHECK:]` need one new callout container built from scratch,
     inserted as a new branch in the existing heading/list/table dispatch chain, with the current
     fall-through-to-paragraph behavior preserved as explicit unknown-kind degradation.
  2. `LESSON_TEMPLATE` (`surfaces/lesson.py:39-82`) ships a fully private, un-tokenized `<style>`
     block — hardcoded `21px`/`19px`/`16px/1.55`, no `var(--space-*)` or `--font-*` beyond
     `__THEME__`. It must be migrated onto tokens before the heading ramp, `text-lesson`, or any
     vendored font can render. The migration target is `surfaces/study.py`'s
     `presentation.surface_shell(...)` composition, layering `theme_css + SHARED_CSS + LESSON_CSS`.
  3. `surfaces/anki.py` (47 lines) has **no** `#guid` column mechanism and iterates items, not lesson
     blocks. `[!KEY]` export is new code, not a patch.
- All eight open rulings are settled in the research; six verified against source with line numbers.
  Ruling 13's "locked house rows as code constants" has a direct precedent to copy: `model.py:578-590
  LINT_CODES`, a hardcoded sorted deduplicated tuple, never data read from markdown at runtime.
  Ruling 7 (folding `lesson_layout` into `09-02-PLAN.md`) is **free today** — that plan is unexecuted
  and `subject_profiles` is not yet in the shipped schema. Do it before Phase 9 is planned.
- The Runestone Parsons-to-`build` mapping was **confirmed, not falsified**, with one named gap: no
  distractor or indentation support.
- **Two MEDIUM-confidence items — do not launder these into certainty.** The 50ms style-pass budget is
  reasoned, not benchmarked (verify with a `time.perf_counter()` test). The Popover API baseline claim
  is WebSearch-sourced, not primary-doc-verified (re-check if planning lands >7 days out).

**From `06.2-RESEARCH.md`:**

- **`06.2-CONTEXT.md` D-08 is wrong.** It names a `selection_mode`/context field that does not exist
  and will not exist when 6.2 runs: `schemas/response.schema.json` sets `additionalProperties: false`
  with no such key, and Phase 7 — which runs *after* 6.2 — reserves `selection_mode` for a different
  axis entirely (selector composition mode, not which surface embedded the attempt). Research proposes
  minting a new additive `context` field (`"quiz"` / `"lesson_gate"`) on `response_event()` in this
  phase. **This is a format decision and must be explicit in the plan.** Flag the eventual
  `context`-vs-`selection_mode` reconciliation for the Phase 7 planner.
- **`[GATE:]` is not Phase 3.1's grammar.** 3.1 owns only `[!CHECK: <id>]`. 6.2 must add `[GATE:]`
  itself, following `model.py`'s existing `[LESSON-SRC:]` single-line-directive pattern. The ROADMAP
  reads as though 3.1 supplies both; it does not.
- **`gate_skip` is cleanly additive** — one new string in `KNOWN_EVENT_TYPES`. Every existing reader
  (`live_events`, `attempt_number`, `objective_history`, `session_events`, `retracted_ids`) uses
  explicit type-equality checks, so none need changes. The proposed `gate_skip_event()` builder
  carries **no `score` key at all**, not even `None`, which makes ROADMAP criterion 8's "explicitly
  not a `response` carrying a null score" structural rather than conventional.
- Open, with a stated default: the same check skipped and later cleared risks double-counting in
  criterion 9's outcome split. Proposed resolution is pair-level aggregation resolving to "cleared".
- `06.2-UI-SPEC.md` itself names `gate_skip`'s exact field set as an open stop-condition owed at plan
  time. It is not closed.

## 6. Next action

Run these in order. Each is a top-level command; do not nest them.

```
/gsd-plan-phase 3.1 --skip-research
```

3.1 has RESEARCH.md, PATTERNS.md, VALIDATION.md, CONTEXT.md, and an approved UI-SPEC.md. It is ready
to plan right now. `--skip-research` is correct — the research exists and is committed.

Then, in order:

1. `/gsd-plan-phase 6.2 --skip-research` — after 3.1's plans exist, so 6.2 plans against 3.1's written
   `[!CHECK:]` contract instead of a guess. Its pattern mapper never ran; let plan-phase re-spawn it.
2. `/gsd-plan-phase 13` — research needed; it never ran.
3. `/gsd-ui-phase 3.2` then `/gsd-plan-phase 3.2` — research needed; UI gate blocks until the spec exists.
4. `/gsd-plan-phase 9.1 --skip-ui` — research needed.

**The research prompts for 3.2, 9.1, and 13 were long and specific.** They are recorded verbatim in
the session transcript for this date. The load-bearing instructions, if they must be reconstructed:

- **3.2 — settle ruling 12 empirically, first, before writing anything else.** ROADMAP criterion 1
  claims a `.apkg` imports "through stdlib ZIP+SQLite reads alone". This may be unmeetable: Anki
  2.1.50+ exports ship `collection.anki21b` **zstd-compressed**, and the stdlib has no zstd decoder.
  Inspect a real modern `.apkg` and report the actual member listing. The load-bearing requirement is
  the *second* clause — lossless import with a per-note account, no note silently dropped. Default if
  a dependency is needed: take one, pin it, checksum it, license-review it under Directive §4a, and
  say so plainly.
- **9.1 — get real numbers on `edge-tts` and Piper** (license, wheel availability on Windows/Py3.11+,
  model sizes, whether edge-tts still reaches the Microsoft endpoint), and resolve whether an MP3
  encoder is needed at all. Phase 8's registry idiom is the shape D-01 copies; note the ordering risk
  (9.1 depends on Phase 9, which follows 8, and neither is executed).
- **13 — the hardest requirement is criterion 3**, no orphaned sidecar and no held port when the shell
  is force-killed via Task Manager. Determine the real Windows mechanism (Job Objects vs Tauri cleanup
  vs parent-PID watchdog) and compose it with the **existing** `probe()`/`start_server()` three-case
  startup in `surfaces/daemon.py` rather than adding a second mechanism. Also resolve the genuine
  two-updater conflict: `tauri-plugin-updater`'s `latest.json`+signature versus the Phase 2.1 Python
  updater's SHA256SUMS.txt/manifest, both against the same GitHub Releases. Do **not** propose porting
  the runtime — a port would temporarily create two scorers, which Directive §4.2 forbids outright.

## 7. Binding reading for whoever picks this up

- `.planning/PLANNING-DIRECTIVES.md` — §2 autonomy, §3 build-both, §4 the five non-negotiables,
  §4a citation discipline and the supply-chain rule. **§4a is the one most often violated:** a
  rejection that names a Directive section must quote the sentence it relies on, and "it needs a
  dependency" is not an argument.
- `.claude/CLAUDE.md` — Constraints, **as amended 2026-08-09**. Stdlib-only, no-build-step,
  Python-only, and offline-first are now *preferences*. The Technology Stack section below it is
  marked historical and does not bind.
- `.planning/UI-SPEC.md` §8 — the nine accessibility gates. Exactly nine; not a general instinct.
