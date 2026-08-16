---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
current_phase_name: 13.5-reading-teaching-surface-quality-pass
status: Phase 13.5 plans all executed (9 of 9), verification human_needed per 13.5-VERIFICATION.md; Phase 13.9 walking skeleton planned (3 plans), next to execute
stopped_at: Phase 16B UI-SPEC approved
last_updated: "2026-08-15T21:28:29.929Z"
last_activity: 2026-08-14
last_activity_desc: "Quick task 260813-x3g source-to-course contract reframe, slices 1-4a committed and pushed. Applied synthesis section 14 across nine contract/doc files: ROADMAP (nine subphases 14A-17B + governance), SOURCE-TO-COURSE (supersede pointer), REQUIREMENTS (eighteen families GRAPH..MAINT, 47 new requirements, old IDs mapped/superseded), PROJECT (course-first), UI-SPEC (Structured Studio; section 8 gates untouched), PLANNING-DIRECTIVES (finite-strategy + rejection-ledger; section 8 nine-subphase table), AGENTS + .claude/CLAUDE.md (object/authority + operation protocol; non-negotiables intact), README (course-first). Commits: 8b5cab4, e838407, e349c06 (REQUIREMENTS content landed split across the slice-3/4a commits because gsd `query commit` sweeps all modified files while the parallel 13.5 track shared the tree; content verified complete on disk, nothing lost)."
progress:
  total_phases: 26
  completed_phases: 18
  total_plans: 160
  completed_plans: 112
current_phase: 13.5
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-08-07)

**Core value:** One runtime, one scorer, one evidence store — and the runtime, not the model, decides what reaches the learner.
**Current focus:** Phase 13.5 (reading and teaching surface quality), wave 3 next. The source-to-course reframe in `.planning/SOURCE-TO-COURSE.md` opens the next milestone as Phases 14 through 17; v1.0's human-pending verification backlog is below and still open.

## Completed Phases Note

**Milestone complete 2026-08-11.** All 18 roadmap phases are merged into main:
the twelve phase branches of this batch (02.1, 03, 03.2, 04, 05, 08, 09, 10, 11,
999.1, 999.4, 999.5) landed on top of 03.1, 06.1, 06.2, and 09.1, which merged
earlier the same day. The pre-existing 06.2 evidence-index regression flagged in
`HANDOFF-PHASE10.md` / `10-VERIFICATION.md` is **resolved**: the 08 merge restored
the v3 evidence index `context` column (`5b7f397 fix(08-06): restore v3 evidence
index (context column) lost in main's 06.2 merge`, in main via `merge(08)`
`30cf342`; the 05 branch carried the same restore in `14f9a89`). Nothing in the
12-phase merge re-introduced it.

**Phase 6.2 — Executable Textbook Loop (completed 2026-08-11 on branch
`gsd/phase-06.2-textbook-loop`):** the lesson gate is a presentation policy
over existing item types. `[GATE: required|recommended|off]` parses
additively; the gate band activates 3.1's reserved slot with one form and
zero JavaScript; `required` truncates at the server (no DOM leak), a
recorded `gate_skip` event is its own evidence type (never a null-score
response), the check/skip routes score and record through the one
runtime/evidence path with `context="lesson_gate"`, and the gate outcome
split is a derived, stated-denominator report. Twelve UI-SPEC §13 gates are
executable fixtures; one human-verify item (screen-reader announcement) is
recorded in 06.2-GATES.md. Six GATE-01..06 requirements delivered.

## Current Position

Phase: **13.5 — Reading & Teaching Surface Quality Pass**, waves 1-2 executed (3 of 8 plans)
Status: v1.0's 18 phases are shipped. A next milestone opened on 2026-08-13 with the source-to-course reframe (Phases 14 through 17), merged into `main` and not yet pushed.
Last activity: 2026-08-14 - Quick task 260813-x3g source-to-course contract reframe, slices 1-4a committed and pushed. Applied synthesis section 14 across nine contract/doc files: ROADMAP (nine subphases 14A-17B + governance), SOURCE-TO-COURSE (supersede pointer), REQUIREMENTS (eighteen families GRAPH..MAINT, 47 new requirements, old IDs mapped/superseded), PROJECT (course-first), UI-SPEC (Structured Studio; section 8 gates untouched), PLANNING-DIRECTIVES (finite-strategy + rejection-ledger; section 8 nine-subphase table), AGENTS + .claude/CLAUDE.md (object/authority + operation protocol; non-negotiables intact), README (course-first). Commits: 8b5cab4, e838407, e349c06 (REQUIREMENTS content landed split across the slice-3/4a commits because gsd `query commit` sweeps all modified files while the parallel 13.5 track shared the tree; content verified complete on disk, nothing lost).

DONE 2026-08-14 (audit chat): slice 4b and slice 5 are complete; see the
"Slice 4b and slice 5 completion" block below. The paragraph following is the
pre-completion record, kept for history.

PREVIOUSLY OWED before any Phase 14A plan: reframe slice 4b (rewrite build-course/curriculum-design/absorb-book/author-bank skills per synthesis section 10 and mirror .agents/skills <-> .claude/skills; add lesson-authoring/discovery-and-binding/media-intake/legacy-upgrade skills + shared reference. NOTE: rewrite the four EXISTING skills to the section-10 contract now, but only STUB the new skills (intent + placeholders) - do not document surfaces 14A/14B/16 have not shipped yet. The 999.5 rule holds: a skill documents only a shipped command surface. Flesh out discovery-and-binding after 14A/14B, lesson-authoring after 16A, legacy-upgrade after 16C/17) and slice 5 (the synthesis section 16.3 implementation-readiness audit, which gates Phase 14A).

Progress 2026-08-14: slice-5 audit is now SPEC'd as a bounded checklist in `.planning/READINESS-AUDIT-14A.md` (A1-A8 + research bake-in gate); it still needs to be RUN (output = audit report + contract-delta patch). The three gating pre-14A schema decisions from synthesis 12.6 are RESOLVED in `.planning/DECISIONS-PRE-14A-2026-08-14.md`: (1) hybrid graph storage - local edges inline, cross-object edges in a readable sidecar, edge vocab frozen at prerequisite-of/covers-objective/source-supports/treatment-of; (2) object-level opaque IDs + component IDs only for cited/gated/evidence-bearing blocks, whitespace+line-ending normalization first, reflow deferred to the 14A tracer; (3) the `mastered` field becomes a Khan-style per-objective, self-adjustable fill state (not one aggregate score; level vocabulary routed to 16B). Next action: run the slice-5 readiness audit, then slice 4b skills, then plan Phase 14A.

### Slice 4b and slice 5 completion (2026-08-14, audit chat)

**Slice 4b complete.** build-course, curriculum-design, absorb-book, and
author-bank are rewritten to the synthesis section-10 operation contract, all
pointing at a new shared `.agents/skills/OPERATION-CONTRACT.md`; the four new
skills (lesson-authoring, discovery-and-binding, media-intake, legacy-upgrade)
are stubs only per the 999.5 rule; `.agents/skills` and `.claude/skills` are
verified byte-identical (diff -r clean after every edit).

**Slice 5 complete: the readiness audit RAN and PASSED.** Report:
`.planning/AUDIT-REPORT-14A-2026-08-14.md`. Highlights: A1 diffed 221 accepted
clauses, landed all 9 no-landing clauses additively, fixed 6 weaker landings
(including the seven progress dimensions now named in GRAPH-03 and the
uncertain-source-claim guard restored to AGENT-02), and added MAINT-04 plus a
family-alias note; A2's Fail (43/47 requirements without fixtures) is fixed
with a labeled Fixture sentence on all 47; A3's checklist wording was amended
(prototype-before-freeze-commits, tracer plans first within a freezing
subphase); A8 verified the rejection ledger fully intact (11/11 hard rejects
carry all eight fields, zero simplicity-only). The mid-audit A9/A10 additions
were adopted: both pass, with the cold-agent onboarding transcript recorded as
Phase 18's owed fixture. The bake-in gate landed in CAP-01, NOTE-01, GRAPH-03,
and FLOW-02 (worked-example-first default, no compelled highlighting,
retrievability never a percentage, reading scrolls, Socratic refusal as a
locked card).

**Decisions:** the three gating pre-14A decisions were already resolved; the
eight remaining 12.6 decisions are framed in
`.planning/DECISIONS-12.6-REMAINING-2026-08-14.md`. Four are held for Weibao
(solo self-acceptance by risk tier, notes placement and Evidence prominence,
formal-test pause policy, executable-source trust persistence); four are
technical calibrations confirmed at their owning subphase. Synthesis 12.6 is
annotated CLOSED/FRAMED in place, record preserved.

**New planning artifacts:** `STYLE-DISCIPLINE-16A-2026-08-14.md` (semantic vs
cosmetic rule for every lesson/note style; notebook page, Cornell, and concept
map prototyped from one parsed content before the long tail registers);
`research/phase-16/16-editor-reader-landscape.md` (bounded editor/reader
landscape thread; the Ellipsus branching-drafts pattern mapped as a thin UI
over the 14A revision model via requirements R1-R10);
`.planning/phases/14A-identity-lifecycle-operation/14A-BRIEF.md` (four
plans, file-fault and external-edit tracer as the freeze gate, walking-skeleton
coupling stated, expansion to the PLANNING-DIRECTIVES section-5 executor bar
required before execution).

**Next action:** Weibao decides the four held decisions; execute 13.5 waves 3+
beside Phase 13.9 (walking skeleton); expand and execute the 14A plans. Phase
14A is unblocked.

**Concurrent-edit notice for the audit chat (2026-08-14).** A direction-review
session amended the planning surface WHILE the slice-5 audit run was in flight.
If your audit snapshot predates these, re-read before sign-off and fold the
consequences into the contract-delta patch rather than re-running mechanical
passes:

- `READINESS-AUDIT-14A.md` gained **A9 (walking-skeleton gate)** and **A10
  (external-user v1 bar)**. Both must be checked or waived-with-reason before
  sign-off; A9's Fail condition ("first learner-visible course experience is
  17B") is now cured on paper by Phase 13.9 but must be honored by the 14A/14B
  plan set your step 7 writes.

- `ROADMAP.md` gained **Phase 13.9 (walking skeleton, with a details block
  before the subphase-sequence section)** and **Phase 18 (external-user v1)**,
  plus a 2026-08-14 revision note. Your A7 emitted sequence should read: 13.5
  waves 3+ beside/before 13.9, then 14A, 14B (13.9 walked before any
  14B-or-later freeze commits), then the 15/16 fork, 17A, 17B, 18.

- `.claude/CLAUDE.md` **Users constraint amended** to "one learner per
  installation; external installations supported; no accounts/auth/
  multi-tenancy". A10's constraint-text check is therefore already satisfied
  for CLAUDE.md; AGENTS.md carries no Users line (verified by grep), so record
  that as the reason A10's AGENTS.md half is a no-op.

- `PLANNING-DIRECTIVES.md` section 5 gained the **lesser-model executor bar**
  (six explicit legibility requirements). Every per-subphase plan from step 7
  is written to that bar; treat it as an acceptance check on each plan.

- `USER-VISION-INBOX.md` gained the 2026-08-14 walking-skeleton/external-user
  entry (verbatim, with disposition); `README.md` gained the "Quick start for
  someone brand new" agent-onboarding section, which is A10 check 2's
  artifact (its cold-agent transcript fixture is still owed).

No re-audit of A1 through A8 is required by these edits alone: they add
scope, they do not alter synthesis clauses. The one interaction to check: A3/
A9 overlap on freeze ordering, where A9 is the stricter reading for 14B+.

**Phase 13.9 planned (2026-08-14, direction-review session).** Three
Sonnet-executable plans exist in `.planning/phases/13.9-walking-skeleton/`
(01 bind and map with two checkpoints, 02 author lesson plus bank, 03 the
sitting, calibration corpus, and A9 closure). They are the reference
exemplars for the standing `.planning/PLAN-TEMPLATE.md` (executor bar,
PLANNING-DIRECTIVES section 5); new plans start from that template. 13.9 can
execute immediately; it does not wait on 14A, and no 14B-or-later freeze
commits before 13.9-03 closes A9. A future-phase capability, agent-facing
update and capability disclosure, is registered on the Phase 18 roadmap
entry per the 2026-08-14 vision-inbox entry.

### Correction (2026-08-13): this file claimed "complete" through a live phase

Between 2026-08-12 and 2026-08-13 this file read `current_phase: complete` and
`18/18` while Phase 13.5 was accruing commits on `main` and a second branch was
accruing the source-to-course research. Both branches numbered their new phase

14. The collision was not caught by any tool: `git merge-tree` reports one

content conflict, in `REQUIREMENTS.md`, and `ROADMAP.md` merges clean while
producing two Phase 14 headings.

Resolved by quick task 260813-r5c. The reading and teaching work became Phase
13.5, which is also where it belongs on dependencies: it hardens the reader and
quiz surfaces the source-to-course spine builds on. The number 14 went to Course
Workspace & Source Binding. The twelve RTS requirements keep their content and
are routed to subphases 16A, 16B, 17A and gates G4 and G6 per
`research/phase-16/14-synthesis.md` section 15.

Still owed, and deliberately not done by that quick task: synthesis section 14
and section 15 propose replacing the flat 14-to-17 sequence with nine subphases
(14A, 14B, 15A, 15B, 16A, 16B, 16C, 17A, 17B) and rewriting five contract files.
The roadmap as merged still carries the flat sequence its own research
supersedes.

### Correction (2026-08-12): the v1.0 ship was recorded green against a red trunk

The "shipped" status above was written from the phase-level VERIFICATION
files. Nothing re-ran the suite against merged `main`, so twelve
independently-green branches merged into a trunk whose CI had been failing
since 2026-08-07. The job died 15 seconds in at step 8 of 14 — the schema
step read `['item']['objective']`, a field plan 03.1-03 had deliberately
removed from the public payload — which meant **the test suite, the content
guard and the JS runner did not execute on any commit for five days**.

Three genuine defects were sitting behind that dead step, none of them
caught by any phase's own verification:

- `runner.py` compared captured stdout byte-for-byte, so a Windows child's
  CRLF failed every `check` item — the scorer's verdict depended on the
  learner's OS.

- `itembank guard` refused the repository's own README, because the
  phase-05 grammar widening made README's fenced format sample parse as a
  real item.

- `authoring.py` wrote pending proposals to `sha256:<hex>.json`, a filename
  Windows cannot create, so every stateful authoring run died there.

Four more tests were passing without testing what they claimed (a wall-clock
cutoff that expired, a git identity that fell back to the global config, 20
LTI checks that only re-proved a refusal, and four pacing tests that counted
the wrong local day off-UTC).

Fixed on `fix/ci-green-post-v1.0` (PR #19): CI green across all 14 steps
(run 31565997898), 63/63 on Linux and Windows, node 7/7. **The milestone is
not honestly complete until that merges.**

Three gaps stay open and are deliberately not closed by that branch:

1. The pacing counter's local day defaults to UTC, so the daily cap rolls at
   19:00 Central rather than local midnight. The tests were matched to the
   documented default rather than flipping it, because changing the zone
   moves every snapshot id.

2. Three tests depend on Windows build artifacts CI cannot produce, so the
   packaging contract now passes by skipping rather than by verifying.
   Closing it honestly needs a Windows runner in the matrix.

3. Nothing gates a merge on CI. A required status check on `main` is what
   stops this recurring; a ship step that reads VERIFICATION files cannot.

> **Branch note (gsd/phase-03.1-finish):** Phase 03.1
> (lesson-rich-blocks-glossary-style) is CLOSED — plans 01-07 complete with
> SUMMARYs, `03.1-VERIFICATION.md` (status `human_needed`, 7/7 truths
> statically verified) and `03.1-UAT.md` recorded. Live automated-suite runs
> and the three perceptual/browser human-verify items remain open; see
> `03.1-GATES.md` and the Deferred Verification table. The milestone's
> active phase stays 08 (main).

Progress: [██████████] 100%

## Performance Metrics

**Velocity:**

- Total plans completed: 24
- Average duration: - min
- Total execution time: 0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 01 | 11 | - | - |
| 02 | 6 | - | - |
| 13 | 5 | - | - |
| 06 | 2 | - | - |

**Recent Trend:**

- Last 5 plans: -
- Trend: -

*Updated after each plan completion*
**Per-Plan Metrics:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 01 P01 | 15min | 3 tasks | 5 files |
| Phase 01 P02 | 18min | 3 tasks | 8 files |
| Phase 01 P03 | 20min | 2 tasks | 5 files |
| Phase 01 P04 | 18min | 3 tasks | 6 files |
| Phase 01 P05 | 25min | 3 tasks | 9 files |
| Phase 01 P06 | 35min | 3 tasks | 6 files |
| Phase 01 P07 | 40min | 3 tasks | 9 files |
| Phase 01 P08 | 21min | 3 tasks | 6 files |
| Phase 01 P09 | 12min | 3 tasks | 7 files |
| Phase 01 P10 | ~21min | 3 tasks | 9 files |
| Phase 01 P11 | ~30min | 3 tasks | 10 files |
| Phase 02 P01 | 55min | 2 tasks | 5 files |
| Phase 02 P02 | 26min | 2 tasks | 8 files |
| Phase 02 P03 | 65min | 3 tasks | 6 files |
| Phase 02 P04 | 16min | 2 tasks | 4 files |
| Phase 02 P05 | 16min | 2 tasks | 2 files |
| Phase 02 P06 | 25min | 2 tasks | 3 files |
| Phase 02.1 P01 | 20min | 3 tasks | 9 files |
| Phase 02.1 P02 | 9min | 2 tasks | 6 files |
| Phase 02.1 P03 | 25min | 3 tasks | 7 files |
| Phase 02.1 P04 | 25min | 3 tasks | 5 files |
| Phase 02.1 P06 | 20min | 2 tasks | 3 files |
| Phase 02.1 P05 | 35min | 2 tasks | 3 files |
| Phase 02.1 P07 | 20min | 3 tasks | 5 files |
| Phase 02.1 P08 | ~15min | 2 tasks | 2 files |
| Phase 02.1 P09 | ~25min | 3 tasks | 6 files |
| Phase 03 P03-02 | 313 | 2 tasks | 5 files |
| Phase 03 P03 | 17min | 3 tasks | 12 files |
| Phase 03 P04 | 313 | 2 tasks | 4 files |
| Phase 03 P03-05 | 8 | 2 tasks | 4 files |
| Phase 04 P02 | 21 | 2 tasks | 4 files |
| Phase 04 P04-03 | 10 | 3 tasks | 8 files |
| Phase 04 P04 | 15 min | 2 tasks | 6 files |
| Phase 04 P05 | 10min | 2 tasks | 2 files |
| Phase 04 P06 | 30min | 2 tasks | 4 files |
| Phase 03.1 P01 | 35 | 3 tasks | 6 files |
| Phase 03.1 P02 | 140 | 3 tasks | 15 files |
| Phase 03.1 P03 | 190 | 3 tasks | 18 files |
| Phase 13 P01 | 16min | 3 tasks | 3 files |
| Phase 07 P01 | 50min | 3 tasks | 8 files |
| Phase 07 P02 | 25min | 3 tasks | 6 files |
| Phase 06 P01 | 95 min | 3 tasks | 9 files |
| Phase 07 P03 | 30min | 3 tasks | 5 files |
| Phase 13 P02 | 105min | 3 tasks | 28 files |
| Phase 13 P03 | 65min | 3 tasks | 7 files |
| Phase 13 P04 | 55min | 3 tasks | 12 files |
| Phase 07 P04 | 40min | 4 tasks | 11 files |
| Phase 13 P05 | 40min | 2 tasks | 2 files |
| Phase 07 P05 | 45min | 3 tasks | 7 files |
| Phase 07 P06 | 45min | 3 tasks | 11 files |
| Phase 06 P02 | 150 min | 3 tasks | 11 files |
| Phase 08-model-adapter-interface-tier-gate-enforcement P08-03 | 22min | 3 tasks | 3 files |
| Phase 08-model-adapter-interface-tier-gate-enforcement P08-04 | 55 | 3 tasks | 9 files |
| Phase 08-model-adapter-interface-tier-gate-enforcement P08-05 | ~35min | 3 tasks | 7 files |
| Phase 09.1-audio-drill-export 09.1-01 | ~50min | 3 tasks | 6 files |
| Phase 09.1-audio-drill-export 09.1-02 | ~45min | 3 tasks | 5 files |
| Phase 09.1-audio-drill-export 09.1-03 | ~50min | 3 tasks | 6 files |
| Phase 09.1-audio-drill-export 09.1-04 | ~40min | 3 tasks | 2 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Phase 3] 03-01: D-04 resolved option-a (user delegation) -- `lesson_ref`/`lesson_slug` stay EXCLUDED from `model.content_fingerprint()` and are locked by a regression assertion (fingerprint of a tagged item equals the byte-identical untagged item); tagging an item never raises `item.content_drift`.
- [Roadmap]: Evidence spine (Phase 1) and daemon/settings/lesson/surfaces/check foundations (Phases 2-5) run as parallel-eligible tracks per `Depends on: Nothing`; the teaching loop, selection, model adapter, subject-loop integration, retention/trends, and the auditor form the dependent chain (Phases 6-11); packaging closes the milestone (Phase 12).
- [Roadmap]: Three phases carry unresolved design questions flagged for their own research at plan time â€” Phase 1 (item identity scheme, Windows event-log durability), Phase 8 (tier-gate enforcement mechanism, no prior art), Phase 11 (second quality gate algorithm, syllabus input formats, auditor reversibility mechanism).
- [Roadmap]: The auditor (Phase 11) is deliberately last among new subsystems; its pitfall guard rails (citation-per-claim, second quality gate, one-item-per-commit reversibility, graduated autonomy) are written as phase acceptance criteria, not follow-on hardening.
- [Phase ?]: 01-01: evidence.py built as a peer module to runtime.py, never imported by model.py; advisory-locked single-write()-per-event append confirmed durable on this Windows machine via a real-OS-process spike that also reproduced the unlocked-O_APPEND corruption bpo-42606 predicts
- [Phase ?]: 01-02: Task 1 checkpoint resolved as option-a â€” response_time_ms and confidence captured with real values (served_ts, --confidence flag); error_category and hint_tier recorded as explicit null with the reason stated in code, since no error taxonomy or hint ladder exists before Phase 6/8
- [Phase ?]: 01-02: evidence.py's response_event()/append_event()/events()/attempt_number()/objective_history() built as the first real writer and reader over the evidence log; surfaces/session.py is the first caller, and model.py additively parses [ID:]/[HASH:] into item_id/content_hash (empty until plan 01-04 assigns them)
- [Phase ?]: 01-03: LINT_CODES built from sorted(set(...)) rather than a hand-ordered tuple, so sortedness/no-duplicates is structural rather than maintained by eye
- [Phase ?]: 01-04: content_fingerprint() hashes only tested-content fields (never rationale); assign_ids() is a pure text transform, cmd_id_assign is the only bank writer, checking D-05 cross-bank id-uniqueness in a read-only first pass before any write
- [Phase ?]: 01-05: SESSION_UPGRADES registry + upgrade_session() closes CONCERNS.md's version-evolution gap; response.schema.json's required array follows the live 23-key response_event() (not the plan's stated 22), matching the same discrepancy 01-02 already resolved
- [Phase ?]: 01-06: schema_validate.py implements exactly the SUPPORTED keyword subset schemas/*.json use; check_schema() raises SchemaError on any keyword outside SUPPORTED/ANNOTATIONS before any instance is examined, so a green validation always means the whole document was checked
- [Phase ?]: 01-06: itembank schema --all is PROTO-05's delivery mechanism -- one sort_keys JSON object carrying model.SPEC, all five schemas/*.json documents in sorted order, and the exact command sequence to run a session, mirroring cmd_spec's no-processing precedent
- [Phase ?]: 01-07: response_event()'s canonical field now stores idempotency_canon()'s output (never null) instead of runtime.canonical_response()'s raw output, so a short item's canonical value matches what dedupe_key is built from -- schemas/response.schema.json updated in the same commit
- [Phase ?]: 01-07: D-10 implemented as a read-side filter -- live_events(log) is the only function views (attempt_number, objective_history) may use for counting; retracted_ids(log) collects over the whole log before anything is emitted, so a retraction physically preceding its target still suppresses it; events(log) stays the raw reader for audit
- [Phase ?]: 01-08: objective_history() is the ONE call site that invokes ensure_index(); cmd_evidence deliberately does not duplicate the call, inferring used/fallback status afterward via a read-only index_stale() check so a regression skipping ensure_index() stays observable rather than being masked by a redundant refresh
- [Phase ?]: 01-08: prefix objective matching implemented as two escaped LIKE clauses (x.% / x:%), never a bare LIKE 'x%', so emt:airway can never also match emt:airwaymanagement
- [Phase ?]: 01-08: index_stale() catches an unopenable/corrupted index internally and treats it as a full-rebuild trigger rather than letting the exception escape -- fixed while confirming test_index_is_disposable goes red per the plan's own acceptance criteria
- [Phase ?]: [Phase 1] 01-09: session_events()/marks_by_event() read exclusively through live_events(), extending D-10's read-side-filter discipline to renders -- a retracted response or a retracted mark vanishes from a view exactly as it vanishes from a count
- [Phase ?]: [Phase 1] 01-09: render_attempt_md/render_session_json take only (log, session_id, qs, bank_path), never the session JSON file itself -- the session file cannot be an input to its own render (D-11), so neither render can claim a sitting is finished, only report what the log itself proves happened
- [Phase ?]: [Phase 1] 01-09: mark_event() rejects any marker other than 'human' (T-1-24); a model verdict is not accepted evidence until Phase 8/TEACH-09 teaches the runtime to hold one as pending review
- [Phase ?]: [Phase 1] 01-09: fixed _tail_dedupe_keys() to track the dedupe key of any event carrying one (response or mark), not just event_type=='response' -- found while confirming a replayed mark batch reports already_recorded per D-12
- [Phase ?]: [Phase 1] 01-09: cmd_mark validates and resolves every batch entry before appending any of them, so an unresolved item_ref anywhere in the batch appends nothing at all, not a partial prefix
- [Phase ?]: 01-10: the day surface's evidence directory is derived from daily_log.md's own resolved location (--log override), not the plan file's directory, so evidence lives beside wherever the tick history itself lives
- [Phase ?]: 01-10: tests/serve_roundtrip.py's attempt-file assertions updated to match render_attempt_md()'s established 01-09 vocabulary (MARK: pending, no finished claim) and the evidence log's append-only attempt semantics (re-answering opens a new live attempt rather than overwriting)
- [Phase ?]: 01-10: cmd_serve prints session_id in its startup banner so a marker can pass it to itembank mark / itembank render attempt after the sitting ends
- [Phase ?]: 01-11: source_key(kind, basename, ref) becomes a migrated response event's dedupe_key, deliberately separate from the live path's session+item+attempt+canonical scheme (D-17), so two unrelated unresolved legacy records can never collide into one event
- [Phase ?]: 01-11: mark and day_tick events reuse mark_event()/day_tick_event()'s own already-idempotent dedupe keys during migration rather than a source_key override -- a day_tick imported by migration and one recorded live via itembank day since 01-10 naturally reconcile
- [Phase ?]: 01-11: no resolution by default (D-14) -- item_id is empty and item_ref carries the original positional reference unless --resolve-by-position is explicitly given, which records source_ref.resolution on every event it touches; no similarity-matching path exists
- [Phase ?]: [Phase 2] 02-01: surfaces/daemon.py's cmd_daemon opens one session (session_id/log/attempt-file) per bank at startup, stored on DaemonHandler.sessions[stem]; isolation between banks sharing one evidence log is by the event's bank field, matching the existing evidence design, not by a separate log file per bank
- [Phase ?]: [Phase 2] 02-01: quiz.record_answer() factored out of cmd_serve's record() closure so the CLI serve path and the new daemon path score through runtime.score_response() and write through evidence.append_event() via exactly the same function (D-08 continued)
- [Phase ?]: [Phase 2] 02-01: scan_dir() sorts candidates by (stem.lower(), full_path) rather than stem alone, so a stem-collision winner is deterministic across restarts even where directory-enumeration order is not guaranteed stable
- [Phase ?]: 02-02: day_state()/day_render()/apply_day_post() take an explicit iso threaded through serve_scoped's day_extra rather than computing 'today' internally, so itembank day --date backfilling still works once day became a daemon launch
- [Phase ?]: 02-02: handle_quiz_answer reads reveal/progress off the bank's session dict (default off) rather than at the route-table level, so a general itembank daemon launch is unaffected while itembank serve's scoped launch keeps --reveal and its progress line
- [Phase ?]: 02-03: Task 1 checkpoint resolved as option-a -- itembank config mirrors itembank schema exactly (no-args table, config schema verbatim, config set validate-then-write); SETTINGS_CODES built as a sorted dotted tuple following the LINT_CODES precedent
- [Phase ?]: 02-03: added required arrays to the nested daemon/selection_weights/model_backend object schemas so settings.missing_key has a reachable input path via config set, rather than a published code nothing can trigger
- [Phase ?]: 02-04: do_submit(session_file, answer, confidence) calls normalize_answer(answer) itself, so the same function serves a raw CLI string and an already-JSON-native /api/submit value without a second call site
- [Phase ?]: 02-04: every /api/* handler wraps its session.do_* call in except SystemExit (400) then except Exception (500), in that order -- SystemExit derives from BaseException so the existing except-Exception-only pattern would not catch it and would kill the daemon
- [Phase ?]: 02-04: session_index(root) rebuilds from _attempts/ on every API request rather than caching at startup, so a concurrently created session is addressable immediately; a client-supplied session/bank_path/out field is refused with 400 rather than accepted
- [Phase ?]: 02-05: handle_report_get calls session.do_report for the summary and a direct read_session for cursor/len(items) in the in-progress branch, keeping do_report's own return shape untouched per the plan's files_modified scope
- [Phase ?]: 02-05: the empty-state report branch is decided purely on auto_attempts==0 and pending_manual==0, independent of session status -- the three report states are branches of one template chosen on data, not a flag
- [Phase ?]: 02-05: REPORT_TEMPLATE's data-field="<name>" markers give tests a stable regex hook against every numeric figure instead of scraping prose
- [Phase ?]: 02-06: probe()/start_server() implement D-02's three-case detect-and-attach startup; fixed a Windows-only bug where Daemon's allow_reuse_address=True silently defeated it (SO_REUSEADDR lets a second process bind an already-listening port on Windows, unlike POSIX)
- [Phase ?]: 02-06: cmd_daemon reads daemon.port/daemon.lan from itembank.json via settings.load_settings(), with --port/--lan overriding; --lan has no CLI off-switch, so 'explicitly given' collapses to a.lan is True
- [Phase ?]: 02.1-01: resources.py is the one bundled-resource reader (checkout and .pyz alike); build.py's STAGE_FILES/STAGE_DIRS are explicit allowlists, never a working-tree walk, keeping evidence and real banks out of the artifact
- [Phase ?]: 02.1-01: itembank.__version__ = "0.3.0" is the first release ever cut from this repo, deliberately pre-1.0; surfaces/cli.py's --version flag imports itembank lazily inside main() to avoid circling back through the .pyz's __main__.py
- [Phase ?]: 02.1-02: build.LAUNCHER_DIR (renamed from LAUNCHERS_DIR) is the one launcher-directory constant; copy_launchers() preserves the source file mode on POSIX so the shipped .command keeps its executable bit
- [Phase ?]: 02.1-02: added .gitattributes (text eol=lf) for launchers/itembank.command and launchers/itembank.desktop -- core.autocrlf on a Windows checkout would otherwise silently corrupt the bash shebang / desktop Exec= line build.py copies verbatim into the release directory
- [Phase ?]: 02.1-03: start_server() (not _bind(), which has no browser-opening code) is where the already-running webbrowser.open() call site lives; wired the real two call sites in daemon.py instead of adding a dead window param -- CONTEXT.md's own line-number caveat anticipated this
- [Phase ?]: 02.1-03: cmd_daemon's effective no-open is a.no_open or not cfg['daemon']['open_browser'] -- open_browser's first-ever reader in the codebase
- [Phase ?]: 02.1-04: gift_item's build (and any unrecognized type) branch is one generic fallback -- not a build-specific case -- per the important_note reserving the tailored refusal contract (locked wording, --strict promotion, unescapable-field detection) for plan 02.1-06
- [Phase ?]: 02.1-04: export_gift() returns exit code 1 when anything was skipped, 0 otherwise -- the plan's own resolution of an unspecified exit-code gap, matching cmd_lint's precedent
- [Phase ?]: 02.1-06: GIFT_CODES carries exactly three refusal codes (gift.type_unsupported, gift.field_unescapable, gift.strict_divergence); the pre-existing default-mode multi warning from 02.1-04 stays uncoded per the plan's own instruction to leave that behaviour unchanged
- [Phase ?]: 02.1-06: the real Moodle sandbox import (D-04's manual layer) could not be attempted -- this executor's tool set has no browser/computer-use capability -- recorded PARTIAL per D-05 and tracked as an open item in .planning/WINDOWS.md
- [Phase ?]: 02.1-05: check_latest reads ITEMBANK_GITHUB_TOKEN from the environment itself (D-09) when no explicit token is passed; found and fixed while writing the token-secrecy test, committed separately from Task 2's own commit
- [Phase ?]: 02.1-05: should_check()'s rate-limit clock is the manifest's own checked_at field, not a second sibling file -- write_manifest's four parameters double as both what's currently trusted and when that was last verified
- [Phase ?]: 02.1-07: install()'s SHA256SUMS.txt fallback is resolved by cmd_update (a new _checksum_fallback helper), not inside install() itself -- install()'s locked 5-argument signature has no url to fetch from, keeping it network-free
- [Phase ?]: 02.1-07: background_check(root, cfg) treats root as the literal base directory (like read_manifest/write_manifest/should_check), not update_root() internally -- lets a test isolate it from the real per-user data directory
- [Phase ?]: [Phase 02.1] 02.1-08: AuthStrippingRedirectHandler overrides redirect_request only and calls super() first -- stdlib decides whether a redirect is legal, the subclass only strips; the origin comparison resolves a missing port to the scheme's default (https->443, http->80) so a url that spells its default port out does not read as a different origin, and the stripped state is sticky because each hop's Request is built from the previous hop's headers
- [Phase ?]: [Phase 02.1] 02.1-08: _github_token_for fails closed -- the token comes only from ITEMBANK_GITHUB_TOKEN (D-09 unchanged) and is returned only for github.com, api.github.com, or a .github.com subdomain, refusing even an explicitly-passed token for any other host, because a release document naming a foreign download url is API-supplied data, not a trustworthy source for the decision to hand it a credential (T-02.1-38)
- [Phase ?]: [Phase 02.1] 02.1-08: the plan's Task 2 test-helper rename (patched_urlopen -> patched_transport on the _open_request seam) collided with Task 1's already-implemented opener-injection helper which had taken the same name; resolved by renaming the Task 1 helper to patched_opener_transport (it injects a transport into the real opener) and giving the seam helper the plan's intended name -- both names now describe what they patch (Rule 3 auto-fix)
- [Phase ?]: [Phase 02.1] 02.1-09: the throttle clock moves into updates/check_state.json (CHECK_STATE_REL/read_check_state/write_check_state), written after every check that reached GitHub whether or not anything was installed -- so should_check throttles from the first check rather than the first install (CR-02), and no placeholder manifest is ever written because handoff() must only trust a real pointer
- [Phase ?]: [Phase 02.1] 02.1-09: status['reached'] on check_latest is the throttle's reachability distinction -- rate-limited (any error status) counts as reached because GitHub charges the 60-per-hour budget for a request that arrived; offline/DNS/timeout does not, so a machine that comes back online checks at its next launch instead of waiting out an interval no request earned
- [Phase ?]: [Phase 02.1] 02.1-09: the disclosure gate writes notified_at alone (never checked_at), so the next launch finds consent satisfied and the clock unstarted and checks immediately rather than a full interval later -- disclosure costs one launch, not one interval; the gate sits after the policy gate so a directory with no itembank.json (opt_in from the schema default) prints nothing and asks nothing
- [Phase ?]: [Phase 02.1] 02.1-09: D-13 stands unrevised and is now documented in three places -- the schema's update_policy description, README's Install section, and CLAUDE.md's Constraints list -- stating the default is opt_in, that this repo's own itembank.json intentionally sets check_on_launch to dogfood the updater, and that the two values are meant to differ; the verifier's alternative (raising the schema default) would make every fresh install phone home by default and was rejected
- [Phase 03]: 03-02: an external [LESSON-SRC:] source wins over an inline ## LESSON section when a bank carries both; the precedence is documented in parse_lesson()'s docstring.
- [Phase 03]: 03-02: the degraded lesson page echoes the bank-author-written directive path (grabbed from the bank text), never the resolved absolute path or the raw OS error text (T-3-07); the reason detail stays with itembank lint because the reader is not a diagnostic surface.
- [Phase 03]: 03-02: warn CSS is template-substituted (__WARN_CSS__) into the lesson page only for the degraded branch, so the plain empty state carries no var(--warn) styling and the two states stay visually distinguishable.
- [Phase ?]: [Phase 3] 03-03: lint(questions, lesson=LESSON_UNCHECKED) uses a sentinel default so 'no lesson data supplied' (skip every lesson check, pre-03-03 callers byte-identical) stays distinct from 'lesson data supplied and there is no ## LESSON section' (every LESSON-REF is unknown, never a skip)
- [Phase ?]: [Phase 3] 03-03: all four lesson lint messages reproduce 03-UI-SPEC.md's Copywriting Contract verbatim (item.lesson_ref_unknown by Qn, lesson.duplicate_heading naming both headings and the slug, lesson.orphan_heading, lesson.src_unreadable), so CI substring greps and authoring agents read the same strings
- [Phase ?]: [Phase 3] 03-03: lesson.src_unreadable echoes the bank-author-written basename, never a resolved absolute path (T-3-09), while the raw OS-error detail stays as the reason -- lint is the diagnostic surface the 03-02 reader defers the detail to
- [Phase ?]: [Phase 3] 03-03: lesson.duplicate_heading is the first BANK-tagged error; bank-level findings trail per-item findings like bank.answer_position_skew, and tests/evidence_roundtrip.py's ordering assertion was extended to admit BANK errors last
- [Phase ?]: [Phase 3] 03-03: accepted lint namespace prefixes live in tests/protocol_roundtrip.py's LINT_PREFIXES and are read (never restated) by the coupling tests, so the tuple, the schema enum and the accepted prefixes cannot drift apart
- [Phase 03]: D-11 executed: --ref filters output to one heading plus its backlinks because the CLI has no anchor to jump to â€” A second matching rule or a render-then-scroll approach would disagree with the slug the tag and anchor already share
- [Phase 03]: lesson_page returns None on a --ref miss so the route, CLI and tests share one render without inheriting an exit path â€” cmd_lesson owns the sys.exit hard stop, keeping the render function exit-free
- [Phase 03]: Resolved the deferred 03-04 backlink-placement quirk: each heading's section renders from its own text/body with its backlinks directly beneath â€” Correct --ref filtering requires per-heading association; the old </section>-re-split nested sections and detached both backlink lists
- [Phase 04]: [Phase 4] 04-02: the day-document adapter was built as one coherent D-08..D-11 implementation, so Task 2's conflict/force assertions passed on first run (no RED); the Task 2 feat commit added the genuinely missing immediately-before-replace revision re-check (TOCTOU closure, T-04-05)
- [Phase 04]: [Phase 4] 04-02: force is a CLI-level second confirmation (--force + --confirm-force OVERWRITE + the conflict's current revision), never a byte-gate bypass -- save(force=True) still requires SHA-256 equality with the fresh bytes and still fails on a third concurrent version
- [Phase 04]: [Phase 4] 04-02: escaped pipes display as literal | and submitted pipes are stored as \| with backslashes escaped first, so _display(_encode(value)) == value; unchanged cells keep their raw bytes because only submitted cells are patched
- [Phase 04]: [Phase 4] 04-02: tests prove exact-byte preservation with a common-prefix/suffix single_replacement helper because difflib SequenceMatcher opcodes are alignment-dependent and non-minimal
- [Phase ?]: 04-03: Accent hex format enforced by theme.py normalization plus schema minLength 7 -- schema_validate.py supports no pattern keyword, and extending the shared validator was outside the plan's file scope.
- [Phase ?]: 04-03: The derived dark accent-soft for the default teal lands exactly on the card color because that is the nearest blend meeting both 4.5:1 pairings -- soft derivation is contrast-first and honestly reported.
- [Phase ?]: 04-03: THEME_CSS is now a computed constant from theme_css(system default); the light warn token moves from #b5760a to the binding #8a5900.
- [Phase ?]: 04-03: The picker fallback reason string is the single source of the exact human copy in both structured and human output.
- [Phase ?]: 04-03: D-07 resolves in favor of one source plus deterministic enforced derivation -- no manual per-mode override path exists in the persisted contract.
- [Phase ?]: 04-04: /api/theme reads only action/source/confirm; any css/path/tokens/config authority field is refused with 400 before any helper runs (T-04-16)
- [Phase ?]: 04-04: same-origin validation applies only when an Origin header is present; netloc comparison normalizes default ports
- [Phase ?]: 04-04: primary actions use the contrast-guaranteed accent-soft/accent pairing instead of white-on-accent, which is not guaranteed in dark mode
- [Phase ?]: 04-04: report empty/partial copy follows 04-UI-SPEC exactly (Nothing has been answered yet. / Some responses still need review. Auto-graded totals exclude them.), superseding the 04-02-era heading
- [Phase ?]: 04-05: study_item composes the runtime's two canonical builders wholesale under an explain member; there is no second explanation allowlist in the surface, so D-12 is enforced structurally rather than maintained by hand.
- [Phase ?]: 04-05: study cards are server-rendered through presentation.surface_shell/state_panel/details primitives with the one theme_css(load_settings(bank_dir)) palette; the client wires only reveal/queue/rating state, never scoring, submission, or a second palette (D-04, D-14).
- [Phase ?]: 04-05: after reveal the Reveal explanation control becomes a quiet 'Explanation revealed' control that keeps focus per UI-SPEC while the revealed/rating groups supply the single primary next action.
- [Phase ?]: 04-05: the embedded CARDS payload legitimately carries explain.correct (study is the deliberate reveal surface, T-04-19 accepted); the no-verdict rule is enforced on client behavior, not on the canonical payload.
- [Phase ?]: 04-05: the locked empty copy 'No study cards match this bank.' comes from the plan's must-haves; the render-error state uses the UI-SPEC study matrix recovery copy 'This card could not be shown. Move to the next card or reload.' with Reload/Choose-another-bank actions.
- [Phase ?]: The force request re-submits against the conflict's current revision (the revision the token is bound to), not the page-load revision; day_document.save's fresh-read gate then catches a third concurrent version.
- [Phase ?]: Day editor conflict/force markup ships server-side with the page; the client only toggles state and wires behavior, so recovery semantics survive no-JS and mid-fetch states.
- [Phase ?]: Token refusals use the same 200 + {status: invalid, reason} shape as every other day edit refusal -- one client error path, no HTTP-status branching.
- [Phase ?]: DAY_CSS migrated onto semantic tokens: --ok/--ok-bg for full/floor states, --bad/--bad-bg for chips/badges, --warn for amber, --accent for interaction only.
- [Phase ?]: 03.1-01: lesson page keeps its own LESSON_TEMPLATE document but composes theme_css + SHARED_CSS + LESSON_CSS in the locked order (surface_shell appends SHARED_CSS last); the composition is imported, never duplicated
- [Phase ?]: 03.1-01: LESSON_CSS uses only the locked project scale sizes (12/16/18/20/32) and 400/600 weights; fonts resolve only via --font-paper/--font-ledger tokens
- [Phase ?]: 03.1-01: --r-2/--r-3 radius tokens landed in SHARED_CSS per UI-SPEC Â§2 ownership (callout contract requires --r-3; Task 1 enumerated voice/measure/leading only)
- [Phase ?]: 03.1-01: [!CHECK: <id>] renders the inert reserved slot and drops the id entirely - no key, no form, no scoring path (D-18)
- [Phase ?]: 03.1-01: Phase 3 warn-note assertions moved from raw var(--warn) grep to the rendered-element contract because SHARED_CSS legitimately carries the token
- [Phase 03.1]: 03.1-02: term_lookup carries an explicit source field ('reader'|'session') -- the append-only provenance UI-SPEC 8.5 owed at first write; the route records source='session'
- [Phase 03.1]: 03.1-02: glossable() includes canonical_key() fragments per the plan's locked set; on any ambiguity it returns False (deliberately conservative)
- [Phase 03.1]: 03.1-02: The /gloss route returns a bare 404 (no event) for suppressed terms, indistinguishable from an unknown slug -- the 8.4-safe branch of the plan's allowed pair
- [Phase 03.1]: 03.1-02: print_gloss:inline ships as one @media print block un-hiding each term's single panel; note count equals distinct-term count by construction (UI-SPEC 16 backstop)
- [Phase 03.1]: 03.1-02: The 8.3 enhancement hook is a vendored inline script carrying the locked unavailable copy, inert on the reader (definitions ship with the page); the sitting fetch-on-open variant is 6.2's fill
- [Phase 03.1]: 03.1-02: model.parse_terms reuses surfaces.lesson's cell splitter via a function-local import -- the plan-mandated reuse without a top-level import cycle
- [Phase 03.1]: 03.1-03: key ids mint through the exact new_item_id()/taken set items use -- no separate key id namespace (research Pitfall 5)
- [Phase 03.1]: 03.1-03: authored cloze grammar is any {{text}} marker -- {{text}} compiles to {{c1::text}} sequentially, {{n::text}} keeps n; on screen the enclosed text renders
- [Phase 03.1]: 03.1-03: C7 closure -- public_item() drops the syllabus [OBJECTIVE:]; study's pre-answer objective chip removed; both render only in explain_payload() behind the verdict
- [Phase 03.1]: 03.1-03: the /key/<id>/review route and `itembank key-review` share record_key_review(); key_review events carry no score and are replayed by Phase 10
- [Phase 03.1]: 03.1-05: style enforcement ships as three cost classes over a closed catalogue (STYLE_CHECK_CATALOGUE) — error severity is earned by construction (structural counts or literal lists) and a style may never raise a check above its catalogue rating (D-13); suppression counts are the report that retires bad checks and locked ids cannot be suppressed (style.ignore_locked fires before the ignore table, T-031-19)
- [Phase 03.1]: 03.1-05: warning calibration is a seam, not a number — STYLE_WARNING_FP_RATES + WARNING_FP_THRESHOLD 0.20 are consumed by Phase 3.2's `itembank calibrate`; StylePrompt.prompt_context emits capped imperatives (default 7, a setting) + exactly one exemplar, placed last, never the ## Voice zone (D-17)
- [Phase 03.1]: 03.1-06: the two OFL-1.1 faces are vendored per the KaTeX precedent (pinned tag/commit, recorded SHA-256 + git-blob SHA-1, license + reserved-names notes beside each file, files shipped unmodified); @font-face lives only in presentation.py's SHARED_CSS token layer with the Georgia/ui-monospace fallback; lesson_layout ("separate" | "inline") is folded into 09-02-PLAN.md before Phase 9 executes with no registry version bump (D-04)
- [Phase 03.1]: 03.1-07: the eight UI-SPEC section-17 gates map to fixtures in 03.1-GATES.md with recorded gaps + human-verify items (cross-browser Popover behavior, ClearType 18px render, 1280/768/375px snapshots); the full-suite green run is recorded as a required action in a python-capable environment, never claimed from this session (approval gate declines python — 03.2-05-SUMMARY precedent)
- [Phase ?]: 13-01: 'itembank sidecar' is the single shell entry point; the --sidecar flag on daemon was removed (plan wording resolved to the command).
- [Phase ?]: 13-01: token gate covers every route except /__itembank__ (401); page navigations are gated because the shell injects the header on every request (13-02).
- [Phase ?]: 13-01: attach failure exits 1 with the 3.3(e) copy, name filled and pid deferred to the shell; attach exits 0 with the already-running line.
- [Phase ?]: select() raises SystemExit on any spec key outside SPEC_FIELDS; each later plan appends its field in the same commit that wires it
- [Phase ?]: D-09 focus pin rides inside the spec dict and is consumed by do_start before select(), keeping the 5-parameter signature
- [Phase ?]: order_shuffled() reproduces the old inline rng.shuffle byte-identically; plan 07-05 owns any seed-literal churn
- [Phase ?]: pair/prereq are pedagogy metadata: excluded from content_fingerprint (D-12), verified with zero hash churn when the fixture was tagged
- [Phase ?]: A pair request serves the whole set adjacently in ascending bank order and raises count to hold it; an unknown pair names the known pair list
- [Phase 6] 06-01: v2 evidence contract confirmed at the Task 1 gate -- response events record integer-or-null hint_tier (null means no tier shown, 0 means tier 0 shown), hint events link session/item/attempt/response with fixed tier index/name, availability, source authored, and unlock path; readers keep accepting v1 events while writers emit v2 (D-15/D-16).
- [Phase 6] 06-01: a genuine wrong practice response unlocks (never shows) the next tier; hint/stumped reveal exactly one fixed tier and append a hint event only when shown -- tier 0 is the lesson pointer and only becomes a hint event at the moment it is actually shown (D-04/D-05/D-07).
- [Phase 6] 06-01: after the authored reveal (tier 5) is shown, the next submit action advances even on a repeat of the last canonical response -- D-06 forbids manufacturing further attempts, and holding the card after full disclosure would do exactly that.
- [Phase 6] 06-01: teaching_outcomes omits a fully-retracted item entirely (D-10 read-side suppression) and never counts stumped as a wrong response; correct-after-tier is only labeled when at least one hint was shown, so two identical correct responses at tier 1 and tier 4 produce different rows (TEACH-03).
- [Phase 6] 06-02: every sitting action goes through session.do_action -- the CLI, /api/*, and the served browser share one adapter, one runtime transition, and one evidence writer; handle_quiz_answer is a compatibility wrapper over the API session, no direct scoring path remains.
- [Phase 6] 06-02: renderer_meta is the ONLY Phase 6 renderer handoff -- one opaque UTF-8 string capped at 256 bytes, discarded before policy/persistence/evidence/response/logs; observation/canvas state belongs to Phase 06.1 and is refused by name on both action envelope and legacy answer form.
- [Phase 6] 06-02: the served browser advances only on runtime-returned advance/complete; a practice hold keeps the card interactive for a materially different retry, the stumped control reveals exactly one fixed tier, and diagnostic/exam responses carry no verdict (score stripped) until their release gates.
- [Phase ?]: INDEX_VERSION 1->2: the disposable index gained a bank column (D-13); the bump alone forces one rebuild and the index stays a cache (delete-and-requery and stale-version rebuild are test-asserted)
- [Phase ?]: 13-02: the shell spawns the externalBin sidecar directly (not Command::sidecar) so the process handle is available for the job object; dev fallback is python itembank.py sidecar.
- [Phase ?]: 13-02: token injection is a shell-local loopback HTTP proxy (WebView2 cannot set navigation headers) - one HTTP transport, proxy adds X-Itembank-Token and strips Origin.
- [Phase ?]: 13-02: POST /cli-twin + 'itembank cli-twin' give the menu its daemon-owned route->CLI mapping; API_ROUTES stays locked at four.
- [Phase ?]: 13-03: the frozen exe is the full CLI entry (sidecar is a CLI mode); the bundled shell passes 'sidecar <dir>'; PyInstaller --add-data carries schemas/styles/fonts because resources.py resolves relative to the frozen root.
- [Phase ?]: 13-03: install-notice values are compile-time defines with !error fail-closed; uninstaller deletes only \ (fixture-proven); NSIS bundling degrades honestly while makensis is absent.
- [Phase ?]: 13-04: one release channel, two manifest formats from the same tag (SHA256SUMS.txt + latest.json/minisign); the shell reads the daemon-owned notified_at record and injects the StatusNotice once into the first HTML page - no second consent store.
- [Phase ?]: User confirmed option-a on both 07-04 gates: distinct selection_mode field (D-11) and a selection event once per sitting plus selection_mode on every response event (D-03)
- [Phase ?]: 13-05: AV/signing decision recorded as the honest unsigned branch (D-11) with real SHA-256; Authenticode/VirusTotal/submission rows are explicit pending, never executed.
- [Phase ?]: D-15 resolved: selection_weights.recency_decay IS the soft penalty (read by phase 7); objective_miss_rate/difficulty_spread retagged to phase 10 and inert
- [Phase 8] 08-01: the tier gate is the five-step algorithm from RESEARCH Pattern 1 — manifest build, strict schema, span, fact, move — fail-closed at every layer; a leaking candidate is dropped whole, never rewritten into a sanitized version (D-06)
- [Phase 8] 08-01: learner_payload is the single constructor surfaces may call; pass -> status+generated, drop/unavailable -> status + null generated, never a reason/tier/fact/provider/detector detail (D-08)
- [Phase 8] 08-01: protected-fragment overlap detection normalizes with casefold + whitespace collapse and a MIN_FRAGMENT_LEN=4 floor so the conservative ambiguity rule stays useful
- [Phase 8] 08-01: the authored-fallback seam reuses the Phase 6 runtime.authored_hint(q, tier, canonical) — not the plan's stated (q, tier) — and keeps the ladder usable at the unlocked tier on drop/unavailable (MODEL-03)
- [Phase 8] 08-02: model_backend became a named profile registry {active, profiles} of fixed records (name, transport hosted_cli|openai_compatible, command|endpoint, model, timeout_seconds, max_output_bytes, context_window, secret_env) plus the top-level suggestion_reveal enum defaulting to after-self-mark (D-22); the shipped default is disabled (active "" + empty profiles), so a fresh install never phones a provider
- [Phase 8] 08-02: the shared profile resolver (surfaces/settings.resolve_profile, re-exported by model_adapter) validates unique names and the two known transports' required fields at read time — settings.invalid_value for a bad registry, adapter.profile_unknown for a missing active name — and DEFERS unrecognized transport names to TRANSPORT_REGISTRY, so a third backend is a registry entry plus a config entry with zero resolver edits (D-27), and an unregistered transport resolves to typed adapter.transport_unknown
- [Phase 8] 08-02: credentials are resolved from os.environ[profile.secret_env] by name at invoke time only; the settings file stores the env-var name, never the value, and the value never enters requests, results, logs, or evidence (D-03/D-15) — enforced structurally by the schema's additionalProperties false and asserted by a flatten() scan over request/result bodies
- [Phase 8] 08-02: the two shipped transports (hosted_cli subprocess, openai_compatible urllib) produce the same normalized request/result shape under a config-only switch, preserving backend class (hosted|local) in private audit metadata (D-17/D-18); every failure family is one typed unavailable result with a named adapter.* code (D-04)
- [Phase 08]: model_interaction and mark_proposal events are registered in KNOWN_EVENT_TYPES and the schema enum in the same commit as each builder (D-23); dedupe is one-generation-per-interaction with retries linked via parent_interaction_id (D-12)
- [Phase 08]: mark_event(proposal_ref=None) folds the reference into the dedupe raw string so accepting two different proposals for the same response records two distinct human marks; the marker != 'human' guard stays byte-for-byte unchanged (D-14/D-23)
- [Phase 08] 08-03: requirements TEACH-07/08/09, MODEL-03, MODEL-05 NOT yet marked complete -- the shared-ID gate (#2388) blocks them because 08-04/05/06 still declare them without SUMMARYs; requirements.mark-complete re-evaluates when the last declaring plan finishes
- [Phase 09.1] 09.1-01..04: audio drill export complete on branch gsd/phase-09.1-audio-export -- one TTSEngine interface + registry (model-backend shape), transcript-only engine, edge-tts (LGPL-3.0 pin) + piper (bundled-binary sidecar decision; the wheel-bearing piper-tts is GPL-3.0-or-later and is NOT imported), assemble_pack one-writer with per-pack/per-item split, /api/export_audio daemon route, digest-stable atomic writes, no evidence write (D-01..D-16 all covered; AUDIO-01..07 marked complete in REQUIREMENTS.md)

## Deferred Verification

| Phase | State | Resume |
|-------|-------|--------|
| 2.1 | verification_deferred_human | $gsd-verify-work 2.1 — 4 human items: real-OS double-click per OS; Gatekeeper quarantine on a real macOS machine; Linux desktop-file-manager launch; real LMS import acceptance (SC5 manual half) |
| 3 | verification_deferred_human | $gsd-verify-work 3 — 1 human item: interactive browser click-through of lesson ↔ question round trip (fresh-model, no-source process claim verified by artifact; scroll feel is a human judgment) |
| 03.1 | verification_deferred_human | $gsd-verify-work 03.1 — live full-suite + schema_validate run; cross-browser Popover; ClearType 18px render at 375/1280px; 1280/768/375px snapshots (see 03.1-GATES.md + 03.1-UAT.md) |
| 4 | verification_deferred_human | $gsd-verify-work 4 — 7 human items: perceptual hierarchy / real-browser 320px/200% rendering, live native color-picker behavior, assistive-tech announcement timing, and the remaining 04-VALIDATION manual-matrix checks |
| 5 | verification_deferred_human | $gsd-verify-work 5 — 2 human items: Windows process-tree kill on a real Windows host and the manual end-of-phase pass (see 05-VERIFICATION.md human_verification) |
| 09 | verification_deferred_human | $gsd-verify-work 09 — KaTeX release approval before vendoring (09-03: approve one immutable KaTeX release) |
| 10 | verification_deferred_human | $gsd-verify-work 10 — 1 UI gate (10-06 Task 3, DEFERRED, blocking, human-pending; see 10-VERIFICATION.md) |
| 11 | verification_deferred_human | $gsd-verify-work 11 — 4 human items (see 11-VERIFICATION.md human_verification / UAT) |
| 999.4 | verification_deferred_human | Manual Canvas checklist (R-01 fake-platform default; the real-Course consumer question stays open) |
| 999.5 | verification_deferred_human | WINDOWS.md windows 2–3: LAN cross-device phone reachability (02) and real Moodle GIFT import (02.1) — human verify/waive before /gsd-ship |

## Quick Tasks Completed

| ID | Task | Date | Status |
|----|------|------|--------|
| 260812-e2m | Four reader defects: leaked print CSS killing the glossary popover, `## TERMS` overrunning into lesson tables, relative `@font-face` urls 404ing on nested routes, authored-hint fallback printing a slug | 2026-08-12 | complete ✓ |
| 260813-r5c | Merge the source-to-course reframe from `origin/main` and renumber the reading/teaching phase from 14 to 13.5, resolving the two-phases-one-number collision | 2026-08-13 | complete ✓ |
| 260813-x3g | Reframe slice 1: replace the flat Phase 14-17 sequence in ROADMAP.md with the nine subphases (14A-17B) plus four governance clauses per synthesis section 15/16.3, and point SOURCE-TO-COURSE.md at them; originals preserved as historical rationale | 2026-08-13 | complete ✓ |

Found by driving the running daemon in a browser, not by the test suite — the
suite was green throughout. Fixes verified the same way after execution:
popover renders at 435x80 (`display:block`, previously 0x0 / `display:none`),
4/4 fonts return 200 from `/assets/fonts/` (previously 0/4), `## TERMS` above
`## LESSON` mints only authored terms, and the authored hint shows the section
title rather than its slug. New guard: `tests/stylesheet_roundtrip.py`.

## Phase 14 progress (paused 2026-08-13, waves 1-2 of 7 complete)

3 of 8 plans executed. Stopped at the wave boundary on request; waves 3-7
are planned, checker-passed and unstarted.

| Wave | Plan | State |
|------|------|-------|
| 1 | 14-01 tracer — the token layer end to end | done |
| 2 | 14-02 reader type, rhythm, measure | done |
| 2 | 14-03 `POST /api/teach`, `itembank teach`, the payload boundary | done |
| 3 | 14-04 quiz voice repair, twelve sizes to five, `--edge` | not started |
| 4 | 14-05 the gloss: placement, bottom sheet, hover intent | not started |
| 5 | 14-06 scroll contract and reader section nav | not started |
| 6 | 14-07 the wrong-answer surface, ladder rendered | not started |
| 7 | 14-08 live regions, byte-identity floor, 13.5-GATES.md roll-up | not started |

**D-A and the D-B include are closed and proven on served bytes**, not
inferred: all seven `--space-*` tokens resolve on both the lesson and quiz
documents, which carry four `@font-face` rules each. At base commit the quiz
carried zero of either. **D-D's backend exists**: the six-tier ladder now has
a route and a CLI, walked end to end through all six tiers, and every attempt
to address a tier from a client is refused 400 with the field named.
**D-C is untouched** — the gloss still opens viewport-centred; 14-05 owns it.

Two runtime defects were found and fixed while building the teach route,
both of which would have made 14-07 render a payload that misstated what the
runtime would do:

1. `entitled` could never be true. `_record_from_evidence` derived
   `highest_tier_unlocked` only from tiers already shown, so a tier unlocked
   by a wrong attempt but not yet opened was invisible and `unlock_path`
   always said `stumped`. The `Open the next hint` control was unreachable.

2. `teaching_transition` let a client decide its own entitlement — `hint` and
   `stumped` differed only in the recorded `unlock_path`.

### Owed before Phase 14 closes

- **`/day/sample_plan` declares zero of four fonts.** `surfaces/day.py:1449`
  builds its document from `theme_css(cfg) + DAY_CSS` instead of
  `presentation.surface_shell`, so it never joined the token layer — D-B on a
  third surface. Found by the tracer, deliberately not fixed inside it, not
  waived: it prints above every green build via `REPORTED_FONT_ROUTES`. **It
  needs an owning plan.**

- `surfaces/settings.THIS_PHASE` is stale at 10, so both new teaching settings
  print as `inert -- read from phase 14`. Pre-existing pattern; see
  `.planning/phases/13.5-reading-teaching-surface-quality-pass/deferred-items.md`.

- Gates 4, 5, 10, 11 need a driven browser or a human — jsdom does no layout.
  `13.5-GATES.md` is created by 14-05 and completed by 14-08.

## Session Continuity

Last session: 2026-08-15T20:32:35.981Z
Stopped at: Phase 16B UI-SPEC approved
Resume file: .planning/phases/16B-ia-modes-recovery-contract/16B-UI-SPEC.md
Deferred human verification: 02.1 (4), 03 (1), 03.1, 04 (7), 05 (2), 09 (KaTeX approval), 10 (1 UI gate), 11 (4), 999.4 (manual Canvas checklist), 999.5 (WINDOWS.md windows 2-3) — see the Deferred Verification table above; 09.1 manual audio-quality checks (see 09.1-UAT.md)
