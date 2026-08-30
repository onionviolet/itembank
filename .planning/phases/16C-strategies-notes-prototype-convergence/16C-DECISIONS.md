# 16C decisions

This file is the single source of truth for every Phase 16C event,
note-format, module-name, registry, copy, naming, and vocabulary decision.
Every later 16C plan reads it before its first task. Sixteen of the decisions
below, D1 through D16, were settled by the checker-approved `16C-UI-SPEC.md`
(all six checker dimensions PASS on 2026-08-15) and are transcribed here
verbatim, never re-litigated; their Decision and Reasoning cells are
reproduced, and the fourth column of that table, "What would overturn it",
stays in the UI-SPEC and is read there. Eight more, D-16C-1 through D-16C-8,
are locked by plan 16C-01 because they are choices an executor would otherwise
make. Task 2 of that plan appends the `## D-12.6-5` heading below
`## Prohibition`.

Written 2026-08-29 by plan 16C-01. Read
`16C-PRECONDITION.md`'s Deviations found section beside this file: two of its
three items change how a later plan reads a shipped surface.

## Transcribed from 16C-UI-SPEC.md (checker-approved 2026-08-15)

## D1. Notes capture in Learn, review in Evidence

*Transcribed verbatim 2026-08-29 from `16C-UI-SPEC.md`.*

**Decision.** Adopt D-12.6-5 recommendation C (margin capture, course review) as the **reversible default**, held for Weibao: note capture happens in place at the anchor inside Learn; the review home and durable listing is the Notes panel inside Evidence; the cross-course global destination stays backburner.

**Reasoning.** The run instruction holds D-12.6-5 for Weibao and directs recommendation C as the reversible default; 16C-RESEARCH Assumption A8 records the same posture, composed with 16B D4 (contextual Notes inside Learn and Evidence, no dedicated route). The note schema is placement-agnostic (anchors plus objective relation), so this is a presentation decision only.

## D2. Save and submit are always two separate controls

*Transcribed verbatim 2026-08-29 from `16C-UI-SPEC.md`.*

**Decision.** "Save to my notes" and "Submit activity" are always two separate controls; no combined save-and-submit control ships in 16C, even though report 12 section 11.2 permits one "after clear consent".

**Reasoning.** The separation is the load-bearing privacy rule; the combined control needs a consent flow this phase has no fixture for, and shipping the strict form first is additive (a combined control can be added later without breaking the separated one).

## D3. Private by default, no capture-time privacy picker

*Transcribed verbatim 2026-08-29 from `16C-UI-SPEC.md`.*

**Decision.** Privacy defaults to private with **no privacy picker at capture time**; scope changes happen per note from the Notes panel in Evidence.

**Reasoning.** Report 12 section 11.2: notes are private and local by default, and sharing needs per-note scope "not a global surprise". Removing the picker from capture minimizes capture friction and keeps the restrictive default structural (unknown rights stay restrictive).

## D4. Epistemic role is a required choice, My claim preselected

*Transcribed verbatim 2026-08-29 from `16C-UI-SPEC.md`.*

**Decision.** Epistemic role is a required single choice at capture with "My claim" preselected, using the seven-role vocabulary verbatim in storage and learner-facing words in the UI.

**Reasoning.** Report 12 section 7.2 item 1 requires every note block to carry an `epistemic_role`; preselecting the most common role (`learner_claim`) keeps required metadata from becoming friction, and a wrong default is learner-correctable at capture or later.

## D5. Learner wording in Paper voice inside role-labeled containers

*Transcribed verbatim 2026-08-29 from `16C-UI-SPEC.md`.*

**Decision.** Learner wording renders in Paper voice inside containers labeled with the note's epistemic role; the four content classes (quotation, learner words, accepted reference, generated suggestion) are distinguished by structural labels, never by typography or color alone, and no fifth voice token is invented.

**Reasoning.** Voice is assigned by "who authored the string" (project `UI-SPEC.md` section 7.3), and learner-authored content is content, not chrome or runtime assertion. Prototype A's success gate requires the four classes be distinguishable; labels satisfy it without expanding the frozen four-voice system, which is 17A's to change if ever.

## D6. Relocation chips, probable never auto-applied

*Transcribed verbatim 2026-08-29 from `16C-UI-SPEC.md`.*

**Decision.** The four relocation states render as labeled chips per the Color table; `relocated_probable` carries explicit "Confirm new location" / "Keep unanchored" affordances and is never auto-applied; `orphaned` keeps its objective attachment visible in the same row.

**Reasoning.** NOTE-01's degraded contract (stale anchor stays attached to its objective with the broken selector flagged), report 12 section 8.2 ("Probable relocation needs review"), and Do-Not-Re-Open row 5 (no automatic ambiguous merge) all state this outcome; the chips are a direct transcription, not an invention.

## D7. Promotion review reuses the reviewer-acceptance vocabulary

*Transcribed verbatim 2026-08-29 from `16C-UI-SPEC.md`.*

**Decision.** The promotion review flow reuses the reviewer-acceptance vocabulary (accept / decline mapping to Loop F's applied / refused outcomes) and the bounded-diff presentation shape; acceptance creates a cited derived copy with a derivation edge, never an in-place mutation of the learner's note; a decline records its reason and leaves the note unchanged.

**Reasoning.** NOTE-02 requires explicit source-backed review with reviewer acceptance as the authority; report 12 section 7.2 item 2 requires derivation edges that never replace the origin; reusing Loop F's vocabulary avoids a second review grammar (the same one-contract rule 16B applied to precedence).

## D8. The strategy picker renders three row classes

*Transcribed verbatim 2026-08-29 from `16C-UI-SPEC.md`.*

**Decision.** The strategy picker renders three row classes: choosable, fallback (unavailable, continuous reading preselected with the stated copy), and locked-by-layer (read-only row carrying the 16B conflict copy verbatim); disallowed strategies are shown and explained, not hidden.

**Reasoning.** STRATEGY-01's degraded path names the fallback; STRATEGY-02's degraded path requires a conflicting preference to yield "with a stated reason", and 16B's settings principle ("so a learner can see why a control is absent rather than wondering if it is missing") extends naturally to the picker. Rendering the locked row IS the stated reason.

## D9. One claim row per dimension, no aggregate anywhere

*Transcribed verbatim 2026-08-29 from `16C-UI-SPEC.md`.*

**Decision.** The progress display renders one claim row per dimension with numerator and denominator always in text, separate denominators for required / required-choice / enrichment, the D-14A-3 discrete-block fill state with its fixed legend, indeterminate copy for missing denominators, retention as state words with a snapshot window, and **no aggregate number anywhere**, with Retrievability never shown as a percentage.

**Reasoning.** Direct transcription of GRAPH-03, report 08 sections 6.1-6.3 (honest-bar rules, items 6 and 7), and D-14A-3's resolved display; the no-aggregate rule is a hard-reject ledger row (Do-Not-Re-Open row 1), not a choice.

## D10. ARIA contract for claims and the fill state

*Transcribed verbatim 2026-08-29 from `16C-UI-SPEC.md`.*

**Decision.** ARIA contract: determinate claims use `role=progressbar` with `aria-valuenow` plus `aria-valuetext` carrying the full "{n} of {N} {metric name}" text; the fill state uses `aria-valuetext` only; indeterminate claims use an indeterminate progressbar with visible text, never an unexplained spinner; announcements go once through the single `role=status` region.

**Reasoning.** Report 08 section 6.3's UI recommendation states exactly this (`aria-valuenow` for determinate ranges, `aria-valuetext` when the number alone is not meaningful, indeterminate permitted when the value is unknown, no unexplained spinner); the single status region is project `UI-SPEC.md` section 8 gate 7.

## D11. Trio validator failure renders a warn refusal plus plain Markdown

*Transcribed verbatim 2026-08-29 from `16C-UI-SPEC.md`.*

**Decision.** Trio validator failure renders as a `--warn` refusal naming the failing check in the validator's own words, followed by the plain-Markdown degradation of the same content, following the shipped `RENDER_REFUSAL_COPY` precedent.

**Reasoning.** The content is not lost or blocked (plain Markdown always renders, per STYLE-DISCIPLINE's degradation requirement and Do-Not-Re-Open row 6), so `--bad` would overstate the state; `--unknown` would understate that a named content fault needs fixing. `--warn` matches 16B's use for recoverable states needing attention.

## D12. Upgrade audit-first ordering and the blocking keyed-meaning halt

*Transcribed verbatim 2026-08-29 from `16C-UI-SPEC.md`.*

**Decision.** The legacy-upgrade surface enforces audit-first ordering (the eleven-item checklist renders before any diff), reuses the DiffApproval contract for the bounded diff, renders unexecuted-module audit rows as "plan-text stand-in", and makes the keyed-meaning halt a blocking state whose only affordances are "Open assessment review" and "Cancel upgrade", with no override control.

**Reasoning.** UPGRADE-01 mandates the baseline audit before editing and a bounded diff; UPGRADE-02's degraded contract IS the halt ("an upgrade touching keyed meaning halts for explicit assessment review"); an override control would convert the halt into a warning, which is a different and weaker contract. "Plan-text stand-in" follows 16C-RESEARCH Assumption A11's honest-audit posture.

## D13. Three equivalent anchor capture paths

*Transcribed verbatim 2026-08-29 from `16C-UI-SPEC.md`.*

**Decision.** Anchor selection ships three equivalent capture paths (pointer selection, keyboard block-and-range picker, structured block-choice list) producing the identical multi-selector target record; drag-only highlighting is forbidden; touch uses the structured list with 44px targets.

**Reasoning.** Report 12 section 11.1's first rule verbatim ("Text selection must have keyboard and structured-choice equivalents. Never require drag-only highlighting"), composed with project `UI-SPEC.md` section 8's touch-target and no-hover-only gates; identical target records keep the interaction path out of the note's provenance, matching gate 5's "scored through the same canonical response" pattern.

## D14. Authored pre-highlighting is orientation, zero events, zero ownership

*Transcribed verbatim 2026-08-29 from `16C-UI-SPEC.md`.*

**Decision.** Authored pre-highlighting renders as sparse orientation with one concise screen-reader label per emphasized region, produces zero evidence events and zero note ownership, and is never visually confusable with a learner highlight.

**Reasoning.** Clause C107 (NOTE-01) states authored pre-highlighting is orientation and never learner evidence; report 12 section 11.1 requires semantic, non-color-only emphasis with a concise label rather than per-word announcements; the zero-event rule is 16C-RESEARCH Pitfall 11's fixture.

## D15. Strategy-action states naming rule

*Transcribed verbatim 2026-08-29 from `16C-UI-SPEC.md`.*

**Decision.** This document carries 16B's naming rule forward and extends it: "Activity view" (capitalized) is the IA jobs area, "activity" (lowercase) is a learner task, and this phase's per-action note states are called **strategy-action states** in every string, fixture, and module docstring.

**Reasoning.** 16C-RESEARCH Pitfall 6 names the three-way collision (16B Activity area, `ACTIVITY-*` requirements, report 12 section 8.1 action states) as a real fixture-readability risk; naming the third vocabulary distinctly closes it before any 16C fixture exists, the same hygiene 16B D6 applied.

## D16. The delete confirmation states the evidence boundary honestly

*Transcribed verbatim 2026-08-29 from `16C-UI-SPEC.md`.*

**Decision.** The Notes panel's delete confirmation states honestly that evidence the runtime is required to keep is not affected, rather than implying total erasure.

**Reasoning.** Report 12 section 11.2 scopes deletion to "the note, its private index, and queued model inputs, while preserving only explicitly required assessment evidence"; the append-only evidence store cannot claw back lifecycle facts (16C-RESEARCH Open Question 2's split), and copy that promised otherwise would be dishonest.

## Locked by plan 16C-01

## D-16C-1. The evidence and note-state split

*Locked 2026-08-29 by plan 16C-01, transcribed verbatim from its objective decision table.*

**Open question.** Which strategy events are evidence and which are private note state (16C-RESEARCH Open Question 2)

**Locked answer.** The evidence store gains exactly two additive `KNOWN_EVENT_TYPES` members, `"activity_completed"` and `"activity_skipped"`. Each such event carries exactly the keys `schema_version`, `event_id`, `event_type`, `ts`, `session_id`, `strategy_id`, `action_state`, `note_ref`, `dedupe_key`, where `note_ref` is a note ID string or the empty string, and no other key. Never note text, never learner wording, never selected content. The content-bearing strategy events (`target_selected`, `content_composed`, `relation_added`, `representation_attached`, `note_revised`, and `source_checked`'s compared content) stay in the learner-owned note store as note revisions and sidecar records, deletable. Learner-artifact pending and settled evidence uses the shipped `mark` / `mark_proposal` machinery unchanged. `EVENT_SCHEMA_VERSION` stays 2 because no existing event's shape changes.

**Rationale.** Deletable learner content inside an append-only store is a contradiction (report 12 section 11.2 versus the one evidence writer); lifecycle facts without content are the only evidence-safe projection of note activity, and `events()`'s skip-and-warn on unknown types (evidence.py:765) is the proven additive route.

## D-16C-2. Where note files live and in what format

*Locked 2026-08-29 by plan 16C-01, transcribed verbatim from its objective decision table.*

**Open question.** Where do note files live and in what format (16C-RESEARCH Open Question 1)

**Locked answer.** One note document per course per learner surface: a coherent Markdown file `notes.md` plus a JSON sidecar `notes.md.json` carrying the report 12 section 9.1 machine record (targets, fingerprints, hashes, states). Stored in a learner note root declared through 16B's `approved_roots` settings key, defaulting to a `_notes/` directory beside the private bank, mirroring `_evidence/` (`evidence.EVIDENCE_DIRNAME` precedent). The sidecar is the machine truth for anchors; the Markdown is the human and export truth for wording. Both are written with the compare-and-swap discipline: write to `<path>.tmp`, then `os.replace`, the `runtime.write_session` shape. Reversible: a path and format choice behind one reader, `notes.read_note_document`.

**Rationale.** FILE-01 names note directories as an approved-root class; evidence-beside-the-private-bank is the shipped residency precedent; report 12 section 9.1 permits Markdown plus sidecar and requires one canonical parser. D-12.6-5's IA-placement half stays held for Weibao at Task 2.

## D-16C-3. Module and file names

*Locked 2026-08-29 by plan 16C-01, transcribed verbatim from its objective decision table.*

**Open question.** Module and file names

**Locked answer.** Five new root-level modules, runtime-tier peers per the evidence.py:12-16 placement rule: `notes.py`, `strategies.py`, `note_outputs.py`, `progress_claims.py`, `upgrade_audit.py`. New tests: `tests/note_schema_roundtrip.py`, `tests/note_promotion_roundtrip.py`, `tests/strategy_registry_roundtrip.py`, `tests/strategy_precedence_roundtrip.py`, `tests/progress_claim_roundtrip.py`, `tests/note_trio_roundtrip.py`, `tests/legacy_upgrade_roundtrip.py`, `tests/cross_subject_suite_tracer.py`. New fixture builder: `fixtures/note_strategy_corpus.py`. New schema: `schemas/note.schema.json`. None collides with the reserved-names table in `16C-PATTERNS.md` (`identity.py`, `journal.py`, `discovery.py`, `graph.py`, `course.py`, `course_package.py`, `sample_course.py`, `capabilities.py`, `surfaces/ia.py`, and the reserved 14A/14B/16B test and fixture names).

**Rationale.** The 16A `capabilities.py` and 16B `surfaces/ia.py` precedents both put new pure vocabularies in their own module rather than growing `model.py`; a name collision with unexecuted plan frontmatter would make two phases claim one file.

## D-16C-4. The four-strategy registry contents

*Locked 2026-08-29 by plan 16C-01, transcribed verbatim from its objective decision table.*

**Open question.** The four-strategy registry contents (16C-RESEARCH Assumption A9)

**Locked answer.** `STRATEGY_IDS = ("continuous_reading", "guided_note_spine", "worked_reasoning", "retrieval_first")` and `FALLBACK_STRATEGY = "continuous_reading"`, code-owned and never replaced by settings data, the `subjects.DEFAULT_PROFILE` D-03 precedent. Report 12 section 10.2's remaining modes stay the catalog runway: Minimal lesson folds into continuous reading; Close reading stays deferred until provenance relocation works. No fifth strategy registers in 16C.

**Rationale.** STRATEGY-01 names exactly this set; report 12 section 10.4's kill criterion (a mode requiring a second parser, scorer, note truth, or UI state machine is killed) is written into the freeze record by plan 16C-09.

## D-16C-5. The 16B conflict-copy transcription and the resolver boundary

*Locked 2026-08-29 by plan 16C-01, transcribed verbatim from its objective decision table.*

**Open question.** The 16B conflict-copy transcription and the resolver boundary

**Locked answer.** The locked conflict copy is, verbatim and never re-worded: "{Setting name} is set by {higher layer name} for this course and can't be changed here." It renders only through `ia.mode_layer_conflict_copy` and `ia.mode_layer_resolve`; 16C's composed resolver is a collector that gathers each layer's live state and calls the one 16B function, never a second precedence implementation (16B D8, D-16B-12). STRATEGY-02's conflict fixture appends rows to `CONFLICT_CASES` in `tests/mode_layer_roundtrip.py`, the extension point 16B's own comment reserves, rather than writing a second fixture.

**Rationale.** Two implementations of one precedence contract drift (16C-RESEARCH Pitfall 10); 16B-07 shaped its fixture list so 16C appends rows rather than duplicating enforcement.

## D-16C-6. The strategy-action-state naming rule

*Locked 2026-08-29 by plan 16C-01, transcribed verbatim from its objective decision table.*

**Open question.** The strategy-action-state naming rule (16C-RESEARCH Pitfall 6, UI-SPEC D15)

**Locked answer.** The per-action states `("not_started", "draft", "completed", "skipped_optional", "equivalent_completed", "needs_review")` are named **strategy-action states** in every string, fixture, module docstring, and test. "Activity view" (capitalized) means the 16B IA area for durable agent and maintenance jobs; "activity" (lowercase) means a learner task. Every 16C module docstring touching either carries the distinguishing sentence.

**Rationale.** Three vocabularies share the word activity (16B's IA area, the ACTIVITY-* requirement family, report 12 section 8.1's action states); naming the third distinctly closes the collision before any fixture exists.

## D-16C-7. The trio's input contract

*Locked 2026-08-29 by plan 16C-01, transcribed verbatim from its objective decision table.*

**Open question.** The trio's input contract (16C-RESEARCH Open Question 4)

**Locked answer.** The one parsed content instance is the pair of dicts `model.parse_lesson(path)` and `model.parse_terms(path)` return for one synthetic lesson, parsed exactly once. Typed concept relations are supplied by the fixture generator as explicit data, never a new inline grammar. Anchors target heading slugs through `model.lesson_slug` today; the upgrade to D-14A-2 component IDs is a named integration seam recorded in the 16C freeze, not a 16C code change. Concept-map edges derive from `[[term]]` refs plus the fixture-declared typed relations.

**Rationale.** Keeps the prototype executable over the shipped parser and keeps the one-parser rule literal (STYLE-DISCIPLINE corollary: a semantic style is a validator plus a projection over the one parsed content model).

## D-16C-8. The closed vocabularies

*Locked 2026-08-29 by plan 16C-01, transcribed verbatim from its objective decision table.*

**Open question.** The closed vocabularies

**Locked answer.** Transcribed verbatim from report 12 and REQUIREMENTS.md, each a module-level tuple: epistemic roles `("quote", "learner_claim", "learner_question", "learner_example", "calculation", "diagram", "accepted_reference_link")`; strategy-action states per D-16C-6; relocation states `("resolved", "relocated_exact", "relocated_probable", "orphaned")` where `relocated_probable` requires review and is never auto-applied; note status `("draft", "learner_accepted", "disputed", "superseded", "deleted")`; target kinds `("source", "lesson_step", "media", "item_public", "concept")`; artifact kinds `("proof", "program", "diagram", "explanation", "project", "observation")`; authorship types `("learner", "authored")`.

**Rationale.** Closed sorted vocabularies are the project-wide additive-registration discipline (`STYLE_CHECK_CATALOGUE`, `GATE_MODES`, `LINT_CODES`); transcription from the verified report 12 lines removes every executor judgment about spelling.

## Prohibition

No 16C plan, executor, or reviewer may re-litigate D1 through D16 or D-16C-1
through D-16C-8. D1 through D16 were approved by the checker on 2026-08-15 and
transcription is the only permitted operation on them; D-16C-1 through
D-16C-8 are locked so that plans 02 through 09 are transcription rather than
judgment. A change request against any of the twenty-four is a new decision
record with its own dated heading, an evidence line, and a named
reconsideration condition. It is never an edit to the record above.

## D-12.6-5. Notes placement and Evidence prominence (resolved by Weibao)

*Answered 2026-08-29 by Weibao at plan 16C-01 Task 2, the phase's one blocking
decision checkpoint. Recorded `Resolved: pending` in
`.planning/DECISIONS-12.6-REMAINING-2026-08-14.md` since 2026-08-14 and held
for him by `16C-UI-SPEC.md` D1 and `16C-RESEARCH.md` Assumption A8.*

**Question, both halves.** Where do learner notes live by default in the IA,
and is the Evidence view a primary navigation item or one level down.

**Answer: `option-c`, and `primary`.**

Weibao was shown all three placement options with the recommended default
named, and both Evidence-prominence options, and chose the recommended default
in each half: `option-c` (margin capture, course review) and Evidence as a
`primary` navigation item.

**What option-c means, restated so no later plan re-derives it.** Note capture
happens in place at the anchor inside Learn. The review home and durable
listing is the Notes panel inside Evidence. The cross-course global Notes
destination stays backburner. Evidence sits beside Learn, Practice, and Test
in primary navigation.

**Consequences.** None, which is the point of the recommended default. This is
the posture `16C-UI-SPEC.md` D1 already contracts and the reading plans 16C-02
through 16C-09 are written against, so no plan edit, no module change, no
schema change, no fixture change, and no test change follows from this answer.
Phase 17A renders against the recorded choice rather than against a default.

**One docs consequence, deliberately not executed here.**
`.planning/DECISIONS-12.6-REMAINING-2026-08-14.md` D-12.6-5 still reads
`Resolved: pending`. It may be updated to resolved by a later docs commit
citing this heading. Plan 16C-01 owns no file outside this phase directory, so
it is recorded rather than done.

**Reconsideration condition.** A presentation decision over a
placement-agnostic schema (anchors plus objective relation). Reversing it later
changes `16C-UI-SPEC.md` D1's placement prose, the 16B D4 placement note, and
17A's rendering. It never changes a 16C schema, fixture, or test.
