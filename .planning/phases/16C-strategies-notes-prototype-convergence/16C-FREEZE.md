# Phase 16C freeze record

## Frozen at 16C

**Dated 2026-08-30.** All six freeze legs hold. The evidence was re-run in this
task rather than trusted from plan `16C-09` Task 1, because a freeze record
must describe the tree it is freezing, and because the review between the two
runs could have prompted a fix.

**How the fourth leg closed, stated first because it is the one that carries a
condition.** `16C-REVIEW.md` records `accept-with-findings`, written by Claude
under an explicit instruction Weibao gave on 2026-08-30 to bypass his review,
and labelled there as an agent judgment rather than his own signature. This is
the third phase in a row to close this leg that way: `16A-REVIEW.md` and
`16B-REVIEW.md` used the same shape under a standing delegation of 2026-08-28.
Plan 16C-09's first prohibition, "An agent must not sign its own contract", is
therefore **waived by the learner who owns the gate, not met**. **Whoever
relies on this freeze should read `16C-REVIEW.md`'s Provenance section first**,
since striking that section reopens the review leg.

The review was not a rubber stamp. It raised seven findings, all carried into
Open items below, and it withdrew an eighth: a first pass judged the trio's
refusal sentences from the copy constants and concluded they rendered dotted
machine codes at learners. Rendering them through `render_mode` showed they do
not, because `validate_mode` puts the plain phrase in the `check` key. The
withdrawal is recorded in the review rather than deleted, since it is the same
class of error the checkpoint exists to catch.

## What is frozen

### The note record and its closed vocabularies

`notes.note_record` returns a sixteen-key record, frozen as a field set:
`note_id`, `note_document_id`, `revision_id`, `owner`, `privacy_scope`,
`course_id`, `objective_ids`, `strategy_id`, `epistemic_role`,
`learner_wording`, `targets`, `derivations`, `status`, `authorship`,
`created_at`, `updated_at`. Every closed vocabulary is validated in the
constructor rather than at write time, so an invalid record never exists.

Seven closed vocabularies, frozen by name and by membership:

| Vocabulary | Members | Values |
|---|---|---|
| `notes.NOTE_STATUS` | 5 | `draft`, `learner_accepted`, `disputed`, `superseded`, `deleted` |
| `notes.EPISTEMIC_ROLES` | 7 | `quote`, `learner_claim`, `learner_question`, `learner_example`, `calculation`, `diagram`, `accepted_reference_link` |
| `notes.TARGET_KINDS` | 5 | `source`, `lesson_step`, `media`, `item_public`, `concept` |
| `notes.RELOCATION_STATES` | 4 | `resolved`, `relocated_exact`, `relocated_probable`, `orphaned` |
| `notes.PROMOTION_STATES` | 4 | `private`, `review_requested`, `accepted`, `declined` |
| `notes.ARTIFACT_KINDS` | 6 | `proof`, `program`, `diagram`, `explanation`, `project`, `observation` |
| `notes.AUTHORSHIP_TYPES` | 2 | `learner`, `authored` |

`notes.STRATEGY_ACTION_STATES` is frozen alongside them at six members
(`not_started`, `draft`, `completed`, `skipped_optional`,
`equivalent_completed`, `needs_review`) under the D-16C-6 naming rule.

`schemas/note.schema.json` is frozen: four required top-level properties
(`schema_version`, `note_document_id`, `course_id`, `notes`) and no others.

### The note document pair and its write contract

`notes.md` plus `notes.md.json`, written by `notes.write_note_document`. Both
files are written to `<path>.tmp` and then committed with `os.replace`, the
sidecar before the Markdown, so a fault leaves the old or the new pair and
never a torn one. The Markdown half stands alone as a portable document; the
JSON half is the sidecar. Deletion writes tombstones carrying `note_id` and
`status: deleted` rather than removing history.

### Relocation, and the rule that probable is never auto-applied

The four states above, plus `notes.ANCHOR_STATE_LABELS` and
`notes.PROBABLE_CONTROLS` (`Confirm new location`, `Keep unanchored`).
`relocated_probable` is never auto-applied (D6): the two controls exist
precisely because the system declines to guess, and a note whose anchor is lost
stays attached to its objective. Nothing in `notes.py` removes an objective id.

### Promotion outcomes

`notes.PROMOTION_OUTCOMES`, four members, frozen: `blocked`, `conflict_stop`,
`applied`, `refused`. Promotion produces a cited derived copy carrying
`from_note_id`; the learner's original is never mutated by a promotion outcome.

### Evidence: two additive types and one closed event

Two additive members of `evidence.KNOWN_EVENT_TYPES`, which now holds sixteen:
`activity_completed` and `activity_skipped`, mirrored in
`notes.STRATEGY_LIFECYCLE_EVENT_TYPES` and `strategies.LIFECYCLE_EVENT_TYPES`.
Both were added to the published `other_event` enum per D-23 before being
registered, so no event type exists that the project's own schema rejects.
`evidence.EVENT_SCHEMA_VERSION` stays 2; this is an additive extension, not a
version bump.

`notes.strategy_lifecycle_event` writes a **closed nine-key event**:
`schema_version`, `event_id`, `event_type`, `ts`, `session_id`, `strategy_id`,
`action_state`, `note_ref`, `dedupe_key`. No content-bearing field, no learner
wording, no note body, at most a note ID reference (D-16C-1). The append-only
log records that something happened; the deletable note store holds what was
said. It is written through `evidence.append_event` and returns that function's
`recorded` or `already_recorded` unchanged.

### The strategy registry

`strategies.STRATEGY_IDS`, four members, frozen: `continuous_reading`,
`guided_note_spine`, `worked_reasoning`, `retrieval_first`
(D-16C-4). `strategies.STRATEGY_SCHEMA_VERSION` is 1.

`strategies.CONTRACT_KEYS`, eleven members, frozen and required of every
registered strategy: `strategy_id`, `version`, `learning_purpose`,
`eligibility`, `required_actions`, `optional_actions`, `skip_resume`,
`evidence_effects`, `accommodations`, `offline_behavior`, `tests`.

`strategies.FALLBACK_STRATEGY` is `continuous_reading` and is **code-owned**:
the fallback is not configurable, because a configurable fallback is a fallback
that can be misconfigured into absence. `strategies.PICKER_ROW_CLASSES` is
frozen at three (`choosable`, `fallback`, `locked`).

`notes._REGISTERED_STRATEGY_IDS` duplicates `strategies.STRATEGY_IDS`
deliberately (16C-06), and `tests/cross_subject_suite_tracer.py`'s
`scenario_registry_consistency` asserts the two are equal, so the duplication
cannot drift.

### The composed precedence resolver

`strategies.composed_resolve(layers_state, sitting_active=False)` is frozen at
that signature. `layers_state` is an **explicit** layer state passed in by the
caller: the resolver reads no global and infers no layer. It collects
precedence over 16B's one function and never re-types 16B's conflict copy,
which is read from `ia.mode_layer_conflict_copy` per D-16C-5.
`strategies.MID_SITTING_LOCK_COPY` is the frozen mid-sitting sentence.

### The progress comprehension display

`progress_claims.CLAIM_FIELDS`, the **nine-field claim tuple**, frozen:
`claim_kind`, `scope`, `numerator`, `denominator`, `rule`, `window`,
`settlement`, `authority`, `uncertainty`.

`progress_claims.CLAIM_DIMENSIONS`, **seven dimensions**, frozen:
`design_coverage`, `participation`, `settled_evidence`, `current_retention`,
`formal_completion`, `selected_enrichment`, `open_uncertainty`, with
`DIMENSION_LABELS` as their frozen display strings. One claim row per
dimension, and **no aggregate anywhere** (D9): no percent, no single score, no
rollup across dimensions.

`progress_claims.SETTLEMENTS` (`settled`, `pending`, `unknown`),
`MEMBERSHIP_CLASSES` (`required`, `required_choice`, `enrichment`), and
`RETENTION_STATE_WORDS` (`due`, `stable`, `weak`, `at risk`, `unknown`) are
frozen.

The **fill-state contract**: `FILL_BLOCKS` is 4, blocks come from settled
evidence and are stepped down by retention so they **move both ways** (D-14A-3),
and `FILL_STATE_LEGEND` states in the display that this is not a permanent
grade. `progress_claims.ARIA_CONTRACT` is frozen at four entries (D10): a
determinate claim is a `progressbar` whose `aria-valuetext` always carries the
words as well as the number; the fill state carries `aria-valuetext` and
deliberately **no** `aria-valuenow`, because a standing is not a measured
quantity on a scale; an indeterminate claim is an indeterminate `progressbar`
with visible text and never an unexplained spinner; and all announcements go
through one shared `role=status` region.

`claim_text` checks `pending` before `indeterminate`, deliberately and against
the plan text's listed order, because reporting a missing denominator where the
honest statement is that a count is awaiting review would be the less honest of
the two. The reason is carried inline in the function.

### The note-output trio

`note_outputs.OUTPUT_MODES`, three modes, frozen: `notebook_page`,
`cornell_notes`, `concept_map`, with `MODE_NAMES` as their learner-facing names
(`Notebook page`, `Cornell notes`, `Concept map`) and `PROJECTIONS` as their
three renderers. All three are projections of **one parse**; there is no second
parser (D-16C-7). `note_outputs.RELATION_TYPES` is frozen at four: `part_of`,
`causes`, `contrasts_with`, `requires`.

`note_outputs.NOTE_OUTPUT_CHECKS`, **five validator codes**, frozen and all of
severity `error`: `note_output.ownership_missing`, `note_output.anchor_moved`,
`note_output.provenance_missing`, `note_output.cue_without_notes`,
`note_output.edge_untyped`.

The **refusal shape** is frozen (D11): `render_mode` returns
`{"ok": False, "text": <the plain projection>, "failures": [...], "copy": ...}`
where `copy` is `VALIDATOR_FAILURE_COPY` with the mode's learner-facing name and
the failing check's plain phrase substituted. It is a warn, not a block: the
plain Markdown projection is returned on the failure path, so the content is
never lost. `TEXTUAL_FALLBACK_LINE` is frozen as the concept map's textual
equivalent.

### The legacy-upgrade contract

`upgrade_audit.BASELINE_AUDIT_ITEMS`, **eleven items in this order**, frozen:
`current_parse`, `identity`, `fingerprint`, `objectives`, `sources`, `rights`,
`media`, `assessment_boundaries`, `plain_rendering`, `rich_rendering`,
`validation`. Audit runs **first**, before any diff (D12). `AUDIT_HEADING`,
`AUDIT_COMPLETION_LINE`, and `DIFF_HEADING` are frozen.

The **keyed-halt contract** is frozen and blocking: `KEYED_HALT_COPY` plus
exactly two affordances in `KEYED_HALT_AFFORDANCES`, `Open assessment review`
and `Cancel upgrade`. There is no third affordance and no override, and the
absence of a third is the contract. `COSMETIC_SKIP_COPY` and
`CANNOT_EXPRESS_COPY` are frozen.

### Locked copy constants, by module and name

Frozen as literal strings, changeable only through a review that reopens this
gate:

- `notes.CAPTURE_COPY` (13 keys), `notes.ANCHOR_STATE_LABELS` (4),
  `notes.PROMOTION_COPY` (12), `notes.ARTIFACT_COPY` (4),
  `notes.DELETE_COPY` (2).
- `strategies.STRATEGY_NAMES` (4), `strategies.STRATEGY_PURPOSES` (4),
  `strategies.UNAVAILABLE_COPY`, `strategies.MID_SITTING_LOCK_COPY`,
  `strategies.PICKER_HEADING`.
- `progress_claims.DIMENSION_LABELS` (7), `INDETERMINATE_COPY`,
  `PENDING_COPY`, `VERSION_SPLIT_COPY`, `FILL_STATE_LEGEND`.
- `note_outputs.MODE_NAMES` (3), `VALIDATOR_FAILURE_COPY`,
  `TEXTUAL_FALLBACK_LINE`.
- `upgrade_audit.KEYED_HALT_COPY`, `KEYED_HALT_AFFORDANCES`,
  `COSMETIC_SKIP_COPY`, `CANNOT_EXPRESS_COPY`, `AUDIT_HEADING`,
  `AUDIT_COMPLETION_LINE`, `DIFF_HEADING`.

### Document-level contract

`16C-UI-SPEC.md` is frozen for its Copywriting Contract, its semantic-token
assignments, its voice assignments, and its Decisions log **D1 through D16**.
The token assignments are frozen as assignments, not as values: what a token is
used for is 16C's, what it renders as is 17A's.

## What is NOT frozen

Transcribed verbatim from `ROADMAP.md`:

> The 16C freeze covers the note and learner-artifact schemas, the promotion
> and review contract, the finite strategy registry, the composed precedence
> resolver, the progress comprehension display, the note-output trio, and the
> legacy-upgrade contract only. It is explicitly not a visual system or token
> freeze (17A), not an information architecture or navigation freeze (16B), not
> a semantic lesson capability freeze (16A), and not a course schema freeze
> (14B), and its freeze record says so.

Owners, named so a later phase does not assume a contract 16C never made:

- **Phase 17A** owns the visual system and tokens: pixel rendering, token
  values, glyphs, chip visuals, the block-glyph count, and the rendering of
  every copy constant frozen above. 16C froze the words and the ARIA contract,
  not their appearance.
- **Phase 16B** owns information architecture and navigation. 16C consumes
  16B's one conflict function and never re-types its copy; it registers no
  route and no navigation state.
- **Phase 16A** owns semantic lesson capability. 16C reads
  `model.parse_lesson` by key and never by key count, and adds no lesson
  capability.
- **Phase 14B** owns the course schema. 16C's claim tuple, note record, and
  strategy contract are not course records, and `composed_resolve` and
  `claims_from_events` take their layer and course state as explicit
  parameters precisely so 14B can supply the real thing without changing this
  surface.

## The runway and the kill criterion

The remaining **seven output modes** and the on-demand genre styles register
only after this freeze, **one validator and one representative fixture each**,
following the trio's pattern. The trio is the proof that the pattern holds; it
is not permission to spend the runway.

**Kill criterion** (report 12 section 10.4, via D-16C-4): a mode requiring a
second parser, a second scorer, a second note truth, or a second UI state
machine is **killed**, not accommodated. This freeze records the criterion and
the runway. It does not spend either.

## Evidence

Re-run in this task on **Darwin 27.0.0 arm64, Python 3.14.6**.

**The cross-subject tracer**, final lines verbatim:

```
CROSS-SUBJECT SUITE: 9 passed, 0 failed
elapsed: 0.274s
```

Exit 0. All nine freeze-gate fixture rows read `passed`. No row reads `weaker
proof` and no row reads `not run`.

**The guard**, verbatim: `0 offending files`. Exit 0.

**The full suite**, re-run in this task: **96 test files, 284 seconds, 0
failures**. Task 1's own measured figure was 96 files in 270.2 seconds; the
14-second difference is machine load between the two runs and not a change in
file count. Both runs are on the same machine and Python version.

The one test that was red in Task 1's run, `tests/selection_retention_roundtrip.py`,
passes in this run. It was diagnosed and fixed on 2026-08-30 outside the freeze
gate: a clock-dependent fixture, not a regression.

**Additivity**, recomputed against `16C-PRECONDITION.md` in this task:

| Value | Baseline | Found now |
|---|---|---|
| `fixtures/selection_evidence.jsonl` | `55fd52b5...861ce` | identical |
| `fixtures/lesson_retention_events.jsonl` | `a9338eb7...ca5f831` | identical |
| `schemas/settings.schema.json` | `b6e5b154...93e54ec` | identical |
| captured view counts | `[40, 0]` | identical |
| captured view hash | `a9f88a03...b492d7` | identical |

`tests/note_promotion_roundtrip.py` re-checks all five against the values
parsed out of `16C-PRECONDITION.md` rather than recomputed, so the comparison
cannot become circular.

**Phase 13.9 A9 closure**: checked and held. The tracer halts by name when
`.planning/phases/13.9-walking-skeleton/13.9-03-SUMMARY.md` does not exist,
because a 16C freeze is a 14B-or-later freeze and 14B's own freeze is
conditional on the walking skeleton having been walked.

**Prototypes**: the trio and tracers A, B, and C all ran and passed inside
`scenario_trio`, which calls the seven scenario functions from
`tests/note_trio_roundtrip.py` directly rather than duplicating them, and
reports that module's own failure list. No prototype was skipped, so no
prototype needs a recorded judgment in lieu of a result.

**The review**: `16C-REVIEW.md`, verdict `accept-with-findings`, signed
"Claude, as an agent, under Weibao's explicit instruction of 2026-08-30 to
bypass his review. Not Weibao's own signature." Read that file's Provenance
section before relying on this freeze.

## Open items, with owners

**From this phase's summaries** (all seven accepted in the review as honest
records; none blocking):

| Item | State | Owner |
|---|---|---|
| 16C-02, the header row parsed as a glossary term | Fixed in plan; recorded because the count assertion would have passed either way | closed |
| 16C-04, `claim_text` pending-before-indeterminate against plan text | Deliberate, reason carried inline; frozen as shipped | closed |
| 16C-05, plans 16C-03 and 16C-05 disagreeing on the `surfaces` import | Resolved by narrowing the assertion to `surfaces.ia` by name | closed |
| 16C-06, two new event types failing the published event schema | Fixed additively via the `other_event` enum per D-23 | closed |
| 16C-07, `_edges` calling `model._term_refs` | Deliberate: a local regex would be a second term grammar | accepted, recorded |
| 16C-08, the `.agents` and `.claude` skill mirrors divergent since `2c34a65` | Fixed in `55379fb`; CI mirror step green | closed |
| 16C-09, `agent_operation_roundtrip.py` and `CLAUDE.md` still listing `legacy-upgrade` as a stub | Fixed in `07ad027`, plus a positive runnable assertion | closed |

**From the precondition's deviations**, each with its resolution: the
`parse_lesson` 16-key superset (Weibao chose reconcile-and-proceed 2026-08-29;
16C reads by key, never by key count), the 16B conflict copy carrying `for this
course` (read from `ia.mode_layer_conflict_copy`, never re-typed), and
`python3` for `python` (environment fact, hit again in this task).

**`tests/selection_retention_roundtrip.py`**: closed 2026-08-30. A
clock-dependent fixture, not a regression, diagnosed outside the freeze gate and
fixed by re-dating the CLI leg through an `as_of_now` helper so the leg asserts
the invariant instead of a date. No runtime file changed.

**Deferrals carried forward:**

| Deferral | Owner |
|---|---|
| Pixel rendering, tokens, glyphs, chip visuals, block-glyph count | Phase 17A |
| Component-ID anchors replacing heading slugs (D-14A-2 seam per D-16C-7) | Phase 14A wiring |
| Real course-record and blueprint layer states feeding `composed_resolve` | Phase 14B / 15B wiring |
| Real course records feeding `claims_from_events` (Assumption A4) | Phase 14B wiring |
| The `sources`, `rights`, and `media` audit rows, reading `plan-text stand-in` | whichever phase ships those records |
| The remaining seven output modes and the on-demand genre styles | post-trio runway, one validator and one fixture each |
| Cross-course global Notes destination and route | backburner, synthesis 12.2 |
| A consent-gated combined save-and-submit control | unassigned future phase |

Two of these the review flagged for a later human pass specifically: the
`plan-text stand-in` audit rows, because a stand-in that survives one freeze
tends to survive the next, and the seven-mode runway, because it is the item
most likely to be spent by a phase that did not read the kill criterion.

**From `16C-REVIEW.md`, seven findings**, none a correctness defect and none
blocking:

| # | Finding | Owner |
|---|---|---|
| 1 | `note_outputs._CHECK_WORDS` carries a leading underscore against the no-private convention, the second such reach in that module | next phase touching `note_outputs.py`, or a naming sweep |
| 2 | `CAPTURE_COPY.anchor_choices` fourth option explains itself with a parenthetical negation in system vocabulary | Phase 17A |
| 3 | **Two 16B-REVIEW findings named 16C as owner and 16C closed neither**: `surfaces/ia.py:449` `"Needs reconciliation"` and `surfaces/ia.py:1403` "treatment" in the course-design register | **reassigned to Phase 17A** |
| 4 | `strategies.UNAVAILABLE_COPY` names the fallback but not the cause or whether a retry is worth attempting | the phase producing a real unavailability |
| 5 | `PROMOTION_COPY.source_check` states a rule and a count with no next action | Phase 17A |
| 6 | `progress_claims.INDETERMINATE_COPY` uses "Indeterminate" and "denominator", above the register of the rest of the phase | Phase 17A |
| 7 | `ARTIFACT_COPY.pending_explainer` opens with the system as grammatical subject | Phase 17A |

Finding 3 is the one that generalizes. Two findings handed from 16B to 16C were
not picked up, and were discovered only because this review read the previous
review. **A finding whose owning phase freezes without closing it has no owner
unless someone reassigns it**, which is a process gap and not a code defect.
17A's planning should read `16B-REVIEW.md` and this record's findings table
together.
