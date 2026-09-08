# Learning phase, activation and source evidence

Date: 2026-09-08.
Status: bounded audit addendum and proposed Itembank representation.
Origin: live handoff from the reading-priorities task, incorporating the user's request to distinguish learning ahead from built but inactive material across subjects.

## Recommendation

Reconciliation update, 2026-09-08: the originating task reports that the planning owner incorporated activity-occurrence scoping, not-applicable axes and explicit Library activation in vault commit `aede2da0`. The commit itself was not inspected here. Direct inspection of the installed pace-course skill and reading-to-itembank reference confirms all three refinements. D3 below is therefore resolved at the personal-skill layer. Itembank activity/schema ownership and implementation remain proposed, and this update authorizes no schema implementation.

Preserve three independent axes: Ahead/Deepen/Prove describes the learning job, Now/Next/Library describes activation, and Published/Bounded/Provisional describes support for placement in the instructor sequence. Attach these to a course activity or activity assignment, not globally to the content file. One artifact can support several activities and phases without duplication.

Use the familiar labels in the UI, but do not turn them into fixed screens, mandatory stages, scoring modes or mastery claims. Internally, explicit names such as `learning_phase`, `activation` and `sequence_evidence` would avoid collisions with assessment `mode`, coverage `state` and learner evidence. These are proposed names, not accepted schema fields.

## Verified current fit and gaps

The current pace-course skill and reading-to-itembank reference contain the three-axis model, optional phase paths, subject shapes and separate completion requirement. This supersedes the earlier audit's description of the skill vocabulary, not its finding that Itembank lacks a combined activity contract.

The course graph binding schema supports objective/source references, treatment kinds, locators, coverage and confidence. It does not provide these three axes. `schemas/session.schema.json:mode` is feedback policy and must not be repurposed. `schemas/lesson_run.schema.json` tracks a lesson run and steps, not phase-specific course assignments. Notes have stable target and fingerprint anchors in `schemas/note.schema.json` and remain learner-owned. Existing identity, item and attempt models should retain their current authorities.

Searches over repository Python and JSON found no implemented Ahead/Deepen/Prove or learning-phase/activation model. This is a symbol-level audit, not proof that every possible equivalent concept is absent. Earlier inspection established fixed Day lanes, lesson completion events, generic source revision handling and caller-supplied staleness reporting. No behavioral suite or UI walkthrough was performed for this addendum.

## Completion and UI

Separate activity occurrences need separate completion evidence even when they share a file. Evidence should reference the activity, phase at attempt time, objective, relevant accepted revision and existing response/session evidence where applicable. Record assistance and evidence modality rather than awarding Prove to a whole artifact. Repeated practice needs occurrence identity and idempotency, not one permanent phase checkbox. Use the existing evidence authority rather than another log.

Day should normally project eligible Now activities, with explicit learner promotion or deferral. Next remains visible for planning. Library stays searchable and visible in the course map with its activation trigger. Mere existence, publication or successful generation must not activate a file. Activation does not bypass unavailable sources, rights, course policy or prerequisite gates.

Keep Now/Next/Library independent from completion, cancellation, availability and staleness. A completed activity can remain in history without being placed in Library. A published source can remain Library. A permissible provisional preview can be Now without becoming an instructor assignment.

## Rescoping

Agreement may strengthen sequence evidence without automatically activating Library material. Narrowing changes the required slice while preserving optional overflow. Reordering changes the class association and activation trigger. Contradiction or retirement flags affected future activities and assessment items for review. Preserve original completion and attempt records.

Remote-origin drift does not itself invalidate an accepted snapshot. Keep sequence relevance, source availability, accepted revision and policy permission separate. A new class post must not reset unrelated evidence or silently copy historical evidence into revised objectives.

## Edge-case matrix

| Shape | Valid treatment and gate |
|---|---|
| CSCI | Reading/prediction, mechanism/tracing, then fresh generic trace or program. Exclude labs and assignment-specific inputs. A built later lesson remains Library until activated. |
| MATH | Definitions and uncollected paper attempt, lecture/proof-move repair, then fresh paper problem or proof. Collected homework stays outside AI. |
| EMT and physical skills | Reading and decision cues may prepare for performance. Notes, cards and written scenarios cannot discharge an equipment/mannequin/instructor-observed gate. Record modality and authorized reviewer. |
| Mandarin | Text/audio/register and corrected usage may support new production. Recognition does not establish speaking or writing ability. Preserve original-draft and disclosure rules. |
| POL and no-AI seminars | Route permitted direct reading and learner-authored work. Do not generate or revise captures. Discussion evidence is descriptive unless an authorized assessment exists. |
| FYE and contact-hour work | Use task-specific attendance/submission/administrative completion. Do not force a learning phase or call attendance independent knowledge. |
| No textbook or sparse slides | Use exact posted sources and mark missing explanation or uninspected visuals. No invented lecture content or page sequence. |
| Lab, studio and performance | Match completion to the actual artifact or observed performance and course policy. Generic quizzes are not a substitute. |
| Familiar or first-seen-in-class topic | Allow Ahead to Prove or Deepen to Prove. No empty mandatory phase artifacts. |
| Spiral, self-paced and mixed courses | Support repeated occurrences and mixed modalities. Self-paced work may have no instructor sequence, so do not force Published/Bounded/Provisional when inapplicable. |
| Shared artifact across phases or courses | Reuse content identity, but keep activity activation, policy and completion scoped to its course and occurrence. |

## Minimum changes and boundaries

| Ref | Recommendation |
|---|---|
| D1 | Record the semantic axes in the owning Itembank contract after reconciling the activity owner. Do not immediately add enums to every artifact schema. |
| D2 | Define the smallest activity assignment and completion mapping using existing IDs, revisions, runtime events and operation contracts. Prototype one shared source supporting two phases. |
| D3 | Clarify two skill ambiguities: classify activity use rather than a whole artifact, and permit an inapplicable phase or sequence axis for administrative and self-paced work. Preserve the user's labels without forcing false classifications. |
| D4 | Prove Day eligibility and Library promotion using the current UI owner. Avoid three new screens, duplicate content, another evidence store or automatic grade changes. |
| D5 | Keep provider acquisition and calendar synchronization as separate dependent work. Do not expand this decision into every future course format. |

The supplied course-specific activation examples are reported handoff facts, not independently checked live Canvas state. No whole-vault inventory was performed. Current personal skill revisions were verified directly.

## Acceptance cases

| Case | Required result |
|---|---|
| Shared artifact | Ahead completion does not complete Deepen or Prove. Content is not copied. |
| Inactive content | Published Library material does not enter Day merely because it exists. Explicit promotion is recoverable and preserves identity. |
| Independent axes | Provisional Now preview is allowed when policy permits, remains labeled provisional and cannot enter graded/mastery-scored practice. |
| Assistance | A hinted Prove attempt retains actual assistance and cannot claim unsupported performance. No ambient UI label changes runtime scoring. |
| Physical gate | Flashcard or note completion cannot satisfy an observed physical-performance requirement. |
| Restricted course | Metadata routing works while prohibited generation, capture revision and collected-prompt intake remain blocked. |
| Source change | Affected future activities receive review state, accepted snapshot citations and historical attempts remain intact, unrelated work is unchanged. |
| Optional phases | Familiar and first-seen-in-class paths skip unnecessary phases without generating placeholders. |
| Administrative/self-paced | Required action is represented without inventing teaching sequence or knowledge evidence. |
| Recovery and access | Retry is idempotent, revisions remain traceable, missing/offline sources expose recovery, and keyboard/static views convey the same meaning. |

## Next action

Include this addendum in the combined next-steps analysis. Settle activity ownership and inapplicable-axis handling before proposing schema writes. Save reconciled findings and keep the original audit evidence linked. No implementation or installed-skill edits were made here.
