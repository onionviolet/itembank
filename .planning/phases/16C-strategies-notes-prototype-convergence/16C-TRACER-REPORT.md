# 16C tracer report

Measured 2026-08-29 on **Darwin 27.0.0 arm64**, **Python 3.14.6**. Every
figure below was produced by the run that this report describes. No budget,
target, or estimate appears anywhere in it: a number among measurements that
was not measured is a fabricated measurement.

The Phase 13.9 A9 closure check ran and passed. Evidence:
`.planning/phases/13.9-walking-skeleton/13.9-03-SUMMARY.md` exists. The
tracer halts by name when it does not, because the 16C freeze is a
14B-or-later freeze and 14B's own freeze is conditional on the walking
skeleton having been walked.

## What was run

| Command | Final line | Exit |
|---|---|---|
| `python3 tests/cross_subject_suite_tracer.py` | `CROSS-SUBJECT SUITE: 9 passed, 0 failed` / `elapsed: 0.261s` | 0 |
| `python3 tests/note_schema_roundtrip.py` | `NOTE SCHEMA: 8 passed, 0 failed` | 0 |
| `python3 tests/strategy_registry_roundtrip.py` | `STRATEGY REGISTRY: 5 passed, 0 failed` | 0 |
| `python3 tests/progress_claim_roundtrip.py` | `PROGRESS CLAIMS: 6 passed, 0 failed` | 0 |
| `python3 tests/strategy_precedence_roundtrip.py` | `STRATEGY PRECEDENCE: 5 passed, 0 failed` | 0 |
| `python3 tests/mode_layer_roundtrip.py` | `MODE LAYERS: 6 passed, 0 failed` | 0 |
| `python3 tests/note_promotion_roundtrip.py` | `NOTE PROMOTION: 8 passed, 0 failed` | 0 |
| `python3 tests/note_trio_roundtrip.py` | `NOTE TRIO: 9 passed, 0 failed` | 0 |
| `python3 tests/legacy_upgrade_roundtrip.py` | `LEGACY UPGRADE: 8 passed, 0 failed` | 0 |
| `python3 tests/evidence_roundtrip.py` | `evidence contract: ok (tracer end-to-end, ... term_lookup)` | 0 |
| `python3 tests/lesson_roundtrip.py` | `ok: lesson roundtrip (slug, parse, fingerprint, ... preamble section boundary)` | 0 |
| `for t in tests/*.py; do python3 "$t" \|\| exit 1; done` | see Full suite below | see below |
| `python3 itembank.py guard .` | `0 offending files` | 0 |
| `git status --porcelain` | no generated bank, note document, or evidence file | 0 |

**Full suite.** 96 test files, 270.2 seconds. Two failed on the first pass and
one of them was this phase's:

1. `tests/agent_operation_roundtrip.py` failed with `FAIL: 'legacy-upgrade'
   is a stub and must not render runnable`. That test names the four stubs
   and 16C-08 shipped one of them. **Caused by this phase, fixed in commit
   `07ad027`**, which also corrected the same stale list in `CLAUDE.md` and
   added a positive runnable assertion so a skill leaving the stub list has a
   check behind it. The suite is green on that file now.
2. `tests/selection_retention_roundtrip.py` failed with `FAIL: the weak
   objective must fill the sitting: ['q3', 'q1']`. **Not this phase's**, and
   not recent: confirmed by stashing every 16C change, and by a worktree
   bisect over about 45 commits which found it failing at every one including
   `66322ff`, the commit that introduced the test. It also fails on Python
   3.13 and from a different working directory. Recorded here as an open
   finding with an owner rather than fixed inside a freeze gate.

   **Diagnosed and closed 2026-08-30**, after this report was written and
   outside the freeze gate. The cause is the calendar, not a regression, and
   the bisect result was the evidence for it rather than against it: a test
   that fails at every commit including its own introducing one is not
   describing a change in the code. The file's other legs pin the snapshot
   cutoff to its `CUTOFF` constant of `2026-08-10T12:00:00.000Z`, so they read
   the fixture's recency exactly as authored. The CLI leg cannot pin anything,
   because `do_start` captures against the wall clock. Every real day moved the
   fixture one day further into the past, and by 2026-08-30 the weak objective
   and the mastered one had both decayed to weight `1.0`. With the weights tied
   there is nothing for the retention context to prefer, Phase 7's own ordering
   settles the sitting, and it returns `['q3', 'q1']`. Measured:
   `emt:airway 1.1905 / emt:math 0.8095` at the pinned cutoff, `1.0 / 1.0` at
   the live one. The fix re-dates the CLI leg's fixture by one identical offset
   through a new `as_of_now` helper, so the leg asserts the invariant (a weak
   objective outranks a mastered one) instead of asserting a date. No runtime
   file changed; `retention.py` and `selection.py` were correct throughout.

## The freeze-gate fixtures

Nine rows, one per ROADMAP fixture, each naming the scenario that covers it.

| Fixture | Scenario | Result |
|---|---|---|
| Every registered strategy runs, and one unavailable falls back | `scenario_strategy_fallback` | passed |
| The STRATEGY-02 conflict matrix, with 16B's own fixture beside it | `scenario_conflict_matrix` | passed |
| A note whose anchor is invalidated by a lesson revision | `scenario_note_anchor` | passed |
| The promotion pair: one promoted, one unreviewed and inert | `scenario_promotion_pair` | passed |
| The pending learner artifact and its human-only settlement | `scenario_pending_artifact` | passed |
| The GRAPH-03 progress tuple set over real lifecycle events | `scenario_progress_tuple` | passed |
| The trio, its three broken fixtures, and prototypes A, B, C | `scenario_trio` | passed |
| The two upgrade scenarios: bounded diff and keyed halt | `scenario_upgrade` | passed |
| Registry consistency across the deliberate duplications | `scenario_registry_consistency` | passed |

Every row reads `passed`. No row is `weaker proof` and none is `not run`.

Two notes on what `passed` means here, so the rows are not read as more than
they are:

- `scenario_trio` calls the seven scenario functions from
  `tests/note_trio_roundtrip.py` directly rather than duplicating them, and
  reports that module's own failure list. The plan allowed a subprocess
  fallback if they were not importable; they were, so this is the stronger
  form.
- `scenario_progress_tuple` appends four REAL lifecycle events through
  `notes.strategy_lifecycle_event` and captures them through
  `evidence.capture_events`, so the participation row is computed from
  events that were actually written, not from a synthetic dict.

## Measured figures

**Tracer scenarios**, one process, four subjects:

| Scenario | Seconds |
|---|---|
| `scenario_strategy_fallback` | 0.000 |
| `scenario_conflict_matrix` | 0.237 |
| `scenario_note_anchor` | 0.003 |
| `scenario_promotion_pair` | 0.002 |
| `scenario_pending_artifact` | 0.000 |
| `scenario_progress_tuple` | 0.000 |
| `scenario_trio` | 0.011 |
| `scenario_upgrade` | 0.001 |
| `scenario_registry_consistency` | 0.000 |
| **whole pass** | **0.261** |

`scenario_conflict_matrix` accounts for 91 percent of the tracer's wall clock
and all of it is the subprocess run of `tests/mode_layer_roundtrip.py`, which
is the point of that leg: 16B's own fixture runs beside 16C's.

**Per-suite wall clock**, measured separately:

| Suite | Seconds |
|---|---|
| `cross_subject_suite_tracer` | 0.31 |
| `note_schema_roundtrip` | 0.79 |
| `strategy_registry_roundtrip` | 0.05 |
| `progress_claim_roundtrip` | 0.04 |
| `strategy_precedence_roundtrip` | 0.05 |
| `mode_layer_roundtrip` | 0.23 |
| `note_promotion_roundtrip` | 0.08 |
| `note_trio_roundtrip` | 0.07 |
| `legacy_upgrade_roundtrip` | 0.40 |
| `evidence_roundtrip` | 13.38 |
| `lesson_roundtrip` | 3.14 |
| **full suite, 96 files** | **270.2** |

The nine 16C suites together cost 2.02 seconds of that 270.2.

**The corpus**, per subject, measured by parsing what the builder wrote:

| Subject | Items | Headings | Terms | Typed relations |
|---|---|---|---|---|
| `emt_respiratory` | 2 | 4 | 4 | 4 |
| `math_linear_system` | 2 | 4 | 4 | 4 |
| `cs_loop_invariant` | 2 | 4 | 4 | 4 |
| `history_conflicting_accounts` | 2 | 4 | 4 | 4 |

**Counts:** `evidence.KNOWN_EVENT_TYPES` holds 16 members.
`evidence.EVENT_SCHEMA_VERSION` is 2. The progress scenario appended 4
lifecycle events. `note_outputs.NOTE_OUTPUT_CHECKS` holds 5 codes.
`strategies.STRATEGY_IDS` holds 4. `notes` publishes 7 closed vocabularies.
`upgrade_audit.BASELINE_AUDIT_ITEMS` holds 11.

## Additivity evidence

| Value | Baseline in `16C-PRECONDITION.md` | Found now |
|---|---|---|
| `fixtures/selection_evidence.jsonl` | `55fd52b56d66438778d8ea0d6c94929c7a65c39763e0acf12c8ad12b876861ce` | identical |
| `fixtures/lesson_retention_events.jsonl` | `a9338eb7d0a5f2603501163e4bb60e972063f86b843291cdf7d576217ca5f831` | identical |
| `schemas/settings.schema.json` | `b6e5b15484ce247f96b69f18df73da45e109a38e0c29aa0d6ad63093e54edc2a` | identical |
| captured view counts | `[40, 0]` | identical |
| captured view hash | `a9f88a0388669ae89a49b5d16d54c684e3d6d325af960a1c37d0521e29b492d7` | identical |

`tests/note_promotion_roundtrip.py` re-checks all five against the values
parsed out of `16C-PRECONDITION.md` rather than recomputed, so the comparison
cannot become circular.

## A rendered progress block, for the review to read as prose

Produced by `scenario_progress_tuple` over four real lifecycle events, one
version-split objective, one choice group with no fixed denominator, and one
unmarked response:

```
Design coverage
  3 of 4 required objectives with a cited source
  Indeterminate: required choice has no fixed denominator.
  Unknown for this version of emt.obj.4. Earlier evidence stays with the earlier version.

Participation
  2 of 4 activities completed rather than skipped

Settled evidence
  1 of 2 responses with a settled mark

Current retention
  1 of 4 objectives stable
  1 of 4 objectives weak
  2 of 4 objectives unknown

Formal completion
  1 of 1 required objectives formally complete
  0 of 1 required choice objectives formally complete
  0 of 1 enrichment objectives formally complete

Selected enrichment
  2 of 5 enrichment objectives with a cited source

Open uncertainty
  1 pending review
  Unknown: not enough settled attempts yet

Objectives
  emt.obj.1  ###.  (3 of 4 blocks, retention stable)
  emt.obj.2  ###.  (3 of 4 blocks, retention due)
  Filled blocks show current standing for this objective. They move up and down as evidence and retention change. This is not a permanent grade.
```

## Open findings

**Carried from this phase's own summaries**, quoted:

1. **16C-02.** "The first `_terms_block` wrote a Markdown header row and a
   separator row ... the header parsed as a glossary entry named Term and
   every subject reported five terms instead of four." Fixed in that plan;
   recorded because the count assertion would have passed either way.
2. **16C-04.** "`claim_text` checks pending before indeterminate. The plan
   lists the branches determinate, indeterminate, pending, unknown, which as
   written makes a pending claim with no denominator render the indeterminate
   sentence."
3. **16C-05.** "Plan 16C-03's acceptance criteria say `strategies.py` imports
   nothing from `surfaces` ... Plan 16C-05 then requires `from surfaces import
   ia` at module level. The two plans disagree." Resolved by narrowing the
   assertion to permit `surfaces.ia` by name and nothing else.
4. **16C-06.** "The two new event types failed the project's own published
   event schema ... Registering the tuple alone would have shipped an event
   type the project's own published contract rejects, into an append-only
   log." Fixed by extending the `other_event` enum per D-23.
5. **16C-07.** "`_edges` calls `model._term_refs`" against the no-underscore
   convention, deliberately, because a local regex would be a second grammar.
6. **16C-08.** The `.agents` and `.claude` skill mirrors had been divergent
   since `2c34a65` and `d2804f0`, so CI's mirror step was red on main. Fixed
   in `55379fb`.
7. **16C-09.** `tests/agent_operation_roundtrip.py` and `CLAUDE.md` both still
   listed `legacy-upgrade` as a stub after 16C-08 shipped it. Fixed in
   `07ad027`.

**Carried from `16C-PRECONDITION.md`'s Deviations found**, each with its
recorded resolution:

| Deviation | Resolution |
|---|---|
| `model.parse_lesson` returns a 16-key superset, not the 6 the plan asserts | Weibao chose reconcile-and-proceed on 2026-08-29; 16C reads `parse_lesson` by key, never by key count |
| The 16B conflict copy carries `for this course`; 16C-01 step 4's expected line does not | The landed string matches D-16C-5's own template; plans read the copy from `ia.mode_layer_conflict_copy` and never re-type it |
| `python3`, not `python` | Every command was run with `python3` substituted and nothing else changed |

**Deferrals, each with a named owner:**

| Deferral | Owner |
|---|---|
| Pixel rendering, tokens, glyphs, chip visuals, block-glyph count | Phase 17A |
| Component-ID anchors replacing heading slugs (D-14A-2 seam per D-16C-7) | Phase 14A wiring |
| Real course-record and blueprint layer states feeding `composed_resolve` | Phase 14B / 15B wiring |
| Real course records feeding `claims_from_events` (Assumption A4) | Phase 14B wiring |
| The `sources`, `rights`, and `media` audit rows, which read `plan-text stand-in` | whichever phase ships those records |
| The remaining seven output modes and the on-demand genre styles | post-trio runway, one validator and one fixture each |
| Cross-course global Notes destination and route | backburner, synthesis 12.2 |
| A consent-gated combined save-and-submit control | unassigned future phase |
| `tests/selection_retention_roundtrip.py`, red on main since its own introducing commit | **Closed 2026-08-30.** Clock-dependent fixture, not a regression; diagnosis and fix recorded above |

**Closed during this phase**, recorded so a reader does not go looking:

- 16C-03's empty-copy locked-row interim state, closed by 16C-05's
  `locked_picker_copy` and asserted closed in
  `tests/strategy_precedence_roundtrip.py`.
- D-12.6-5. The 16C-01 Task 2 checkpoint answer WAS the recommended default
  (`option-c` and `primary`), so nothing is carried into the freeze record's
  open items for it. The answer additionally corrected a stale plan-text
  claim: the decision had been resolved by delegation on 2026-08-16 and was
  never pending.
