# 17B gate checklist

The acceptance record for Phase 17B (17B-CONTEXT D-04): one row per gate
G1 through G11, the concrete check transcribed from the ROADMAP 17B
details block, the proof command or fixture, the evidence pointer, and
the state. Scaffolded 2026-09-01 by plan 17B-01 with every row pending;
later waves fill proof, evidence, and state, and 17B closes with every
row either passed or carrying a named defect and a named owner (D-06).

| gate | concrete check | proof command or fixture | evidence pointer | state |
|---|---|---|---|---|
| G1 Coverage | every capability the tracer exercises maps to its requirement row and ledger disposition; no undischarged tracer promise | the wave-2 capability map (15 rows exercised, each with requirement row and disposition) plus the owed-promise table naming the wave that discharges each remaining gate; `python3 itembank.py lint course_fixture_17b/unit3_bank.md` exits 0 with 0 errors 0 warnings | evidence/17B-02-coverage.md; evidence/17B-03-legacy-audit.md (the D-05 legacy upgrade audit, wave 3) | pass (wave 2 scope; rendered, sitting, restore, and egress rows owed to 17B-03/17B-04 per the table in the evidence file) |
| G2 Object/authority | each artifact the tracer creates names its durable object, owner, authority, and source of truth; derived views rebuild | the transcribed binding flow over `course_fixture_17b/` (14A `journal.op_link`, 14B `course.create_course`/`bind_source`), registry deleted and rebuilt from the journal log alone (`identical = True`) | evidence/17B-02-binding.md | pass |
| G3 File safety | the tracer's unit survives the file-fault drills (move, external edit, conflict, interrupted write) preserving old or new valid state | the four transcribed drills on `unit3_lesson.md`/`unit3_bank.md` through the frozen 14A surface (`op_move`, `detect_external_edits`, `journal.stale_preflight`, `journal.conflict`, kill-mid-commit with `replay` naming the interrupted entry); re-lint exits 0 afterward | evidence/17B-02-faults.md | pass |
| G4 Portable capability | the authored lesson reads coherently in plain Markdown outside the UI, and in the UI by keyboard, touch, screen reader, narrow screen, and offline | agent half: the plain-Markdown structural check and read-through of `course_fixture_17b/unit3_lesson.md`; the served lesson at 1280/768/375 (no horizontal scroll, media contained), keyboard activation of a term popover (`Return`), the offline run (`t8_offline.py`, loopback-only journey); human half: the screen-reader walk through orient, lesson, practice, and sitting, plus touch activation | evidence/17B-03-learner-pass.md (stage 4, the plain-Markdown section, the network-unplugged section) | deferred-human: owner Weibao, 2026-09-01. Agent half observed (recorded in the evidence file, not certified); the screen-reader item is owed to Weibao under his 2026-09-01 deferral directive, never agent-certified (D-04). Deviation from Task 4's verify line recorded in 17B-03-SUMMARY.md |
| G5 Evidence honesty | progress over the tracer's scope tree (one open field containing one bounded course containing the unit) renders in both registered rollup models, ROLLUP-DIM and ROLLUP-MAP (IDEA-LEDGER IL-20260817-01), with stated denominators, pending and unknown states shown, and no aggregate score anywhere; the bounded course may complete, the open field never does. Weibao picks the default rollup from the rendered screens | `PYTHONPATH=. python3 t7_rollups.py` (transcribed) over the real evidence log through frozen `progress_claims` and 17A primitives; both screens read one tuple set (sha256 `66ec543c...`); rendered files `evidence/17B-03-rollup-dim.html` and `evidence/17B-03-rollup-map.html`; visible percent signs 0, no aggregate, field states its scope version, course complete under `afe101-complete-v1` | evidence/17B-03-learner-pass.md (stage 7) and evidence/17B-03-rollup-choice.md | pass (rendering and honesty checks); the default is PROVISIONAL (ROLLUP-MAP for trees deeper than one level, ROLLUP-DIM otherwise) recorded by the coordinator under the 2026-09-01 deferral directive, the real choice owed to Weibao; two 17A-03 primitive gaps recorded (17B-03 D-06 items 7 and 8) |
| G6 Assessment authority | no surface, agent, or note in the tracer leaks a key, invents a score, auto-grades prose, or changes a frozen sitting | pre-answer served bytes scanned (0 `CORRECT:`, 0 `WHY BEST`, no tier text); hint tiers unlocked one at a time by the runtime (practice, `TIER 3 · RATIONALE FOR B` named the wrong answer with its text locked); short item parked `score=None` until `python3 itembank.py mark` (practice and exam); exam `next`/`submit` payloads leak no key field and no `explain`; served exam `/api/submit` carries no `score`; submit against the closed sitting refused (`session is already complete`); mode immutable | evidence/17B-03-learner-pass.md (stages 5 and 6) | pass; one flow defect routed (17B-03 D-06 item 6: deferred sittings park on machine-scored items until a human mark) |
| G7 Course quality | the tracer's treatment decisions cite scope, demand, rationale, uncertainty, and the existing-artifact search, and pass review before authoring | `course_fixture_17b/treatments.md` (six fields per objective, seven review verdicts recorded through `director.record_phase` before Task 3 authored anything; operation ids in the file) | evidence/17B-02-coverage.md and course_fixture_17b/treatments.md | pass |
| G8 Flow/visual | first-run, resume, learn, practice, test, source inspection, review, agent failure, and narrow-screen transitions preserve context and hierarchy on the tracer's unit | agent-verifiable half: the driven pass at 1280/768/375 (accessibility trees, layout geometry, resume on every return to the quiz route, the real rate-limit interruption resumed from durable state, the APP-02 anchor-missing notice on served bytes, `Get optional guidance` left unactivated so the authored loop never depended on a model); visual half: acceptance at 1280 and 375 against 17B-UI-SPEC section 1 | evidence/17B-03-learner-pass.md (stages 1, 2, 4, 5, 6, 8) | agent half observed with five flow defects recorded (17B-03 D-06 items 2, 3, 5, 6, 9); visual half deferred-human: owner Weibao, 2026-09-01, under his deferral directive, never agent-certified (D-04) |
| G9 Strategy/notes | each strategy the tracer offers states choice, requirement, skip and resume, accommodation, evidence effect, privacy, provenance, and the note-authority guard | the four frozen strategy contracts read from `strategies.strategy_contract` on this tree and tabulated with all eight columns; the note-authority guard from the frozen `notes` record and the closed nine-key lifecycle event (D-16C-1) | evidence/17B-03-learner-pass.md (G9 section) | pass |
| G10 Portability/recovery | a clean machine restores the tracer's canonical objects and evidence offline; every unsupported capability appears in a loss report | `python3 tools/restore_drill_17b.py --commit HEAD --workdir "$TMPDIR/17b_restore"` (transcribed; the POSIX equivalent of the plan's PowerShell line, deviation recorded in the evidence file) over commit `48703ab4`: fresh detached clone, fresh empty data directory, empty home, every proxy at the discard port and sockets refused inside the worker (`network refused inside the worker = True`), export and validation through the frozen 14B surface (`course_package.export_package`, `verify_manifest`, `restore_package`) | evidence/17B-04-restore.md (the failing run) and evidence/17B-04-restore-repair.md (the repair and the passing re-run) | pass, after repair. The wave-4 run failed honestly: 6 of 7 canonical objects and 0 of 40 evidence events crossed, and two defects were routed rather than patched because both are contract changes in frozen surfaces (D-06 item 10, no operation could grant a right after an object was minted, and its second mechanism, `link` being the only way to bind an authored file so a course's own artifacts were refused as external links; D-06 item 11, the evidence export filter comparing sidecar objective ids against evidence bank slugs). Both were repaired 2026-09-05 as a deliberate contract change (commit `247ffbe`, additive: `journal.op_grant_rights`, `journal.op_adopt`, `course_package.evidence_scope`, and the `evidence-not-carried` loss category, with OPERATION_TYPES unchanged). Re-run over that commit: 7 of 7 canonical objects, 40 of 40 evidence events, manifest complete by recomputation, network refused inside the worker, loss report one honest `machine-local: settings` row |
| G11 Cross-cutting | egress capture equals disclosed manifests; rights-unknown refuses unsafe operations; diagnostics are redacted | egress: not applicable, verified four ways (no captured payload or disclosed manifest exists in evidence/, no non-loopback address anywhere in the wave 2 and wave 3 transcripts, the `Get optional guidance` control present and never dispatched at 17B-03-learner-pass.md:301, `settings.NETWORK_EGRESS_SETTINGS_DEFAULTS` reads `hosted_operations: off`); refusal: `python3 itembank.py source import --base <fixture copy> --file sources/unrightsed_bog_transect.md --adapter markdown` on an all-seven-rights-unknown source added inside `course_fixture_17b/` (copied to a scratch working directory so the repository fixture stays byte-identical) refuses `journal.rights_unknown` at exit 1 with no derived artifact and no registry row, and `course_package.export_package` carries no unknown-`package`-right bytes and names every omission in the loss report; redaction: no word of the source body reaches the diagnostic, the journaled refused entry, the loss report, or the manifest (only `rights` and `unknown` overlap, which are vocabulary) | evidence/17B-04-egress.md | pass (egress clause not-applicable with its reason recorded verbatim per 17B-CONTEXT D-09; refusal and redaction clauses proved). Two observations recorded, neither contradicting a frozen contract: a rights-refused entry carries `resolves_entry: null` because the gate fires before the `prepared` entry is appended, and `remote_process` has no consuming operation today, owed to whichever phase first ships a hosted operation |

Human checkpoints are mandatory for the G4 screen-reader item and the final visual acceptance; an agent never self-certifies those (17B-CONTEXT D-04).

Wave 3 note (17B-03, 2026-09-01): rows G4 and G8 carry `deferred-human` rather than the `pass`/`fail` Task 4's verify line expects, by the owner's standing directive of 2026-09-01 (human reviews deferred, recorded as owed, never self-certified, never silently defaulted). The screen-reader walk and the visual acceptance are owed to Weibao personally; the agent-verifiable halves are in the evidence file and are observations, not certification. The G5 default rollup is likewise a recorded provisional, owed to Weibao (evidence/17B-03-rollup-choice.md).

## Milestone exit record

Dated 2026-09-05, written by plan 17B-04 Task 3 (17B-CONTEXT D-06). Every
gate below carries a final state, and every non-passing gate names its
defect, the diagnosed mechanism, and the owning subphase. Defect ids are
qualified by the wave that recorded them, because waves 2 and 3 each
numbered their D-06 items from 1 and the bare numbers collide: `17B-02
D-06 item 1` (the `cmd_guard` skip list) and `17B-03 D-06 item 1` (the KEY
card body) are different defects.

| gate | final state | defect, mechanism, owner |
|---|---|---|
| **G1** Coverage | pass | none |
| **G2** Object/authority | pass | none |
| **G3** File safety | pass | none |
| **G4** Portable capability | deferred-human | not a defect. The agent-verifiable half is observed and recorded, never certified. The screen-reader walk through orient, lesson, practice, and sitting is owed to Weibao personally under his 2026-09-01 deferral directive (D-04) |
| **G5** Evidence honesty | pass on rendering and honesty; both primitive defects repaired 2026-09-05; the default rollup is still owed to Weibao | `17B-03 D-06 item 7`: no 17A card primitive carries a fill-state slot for ROLLUP-MAP child cards, so the screen composes from `course_shelf` and `fill_state`. Owner 17A-03. `17B-03 D-06 item 8`: `progress_comprehension_display` omits the determinate-claim `progressbar` role and `aria-valuetext` of `ARIA_CONTRACT`. Owner 17A-03. The default choice itself is owed to Weibao (evidence/17B-03-rollup-choice.md). Both primitive gaps were repaired on 2026-09-05 and both screens regenerated through the fixed primitives by the now-committed `tools/rollup_screens.py`: `course_shelf` carries a fill slot with one shared legend, `fill_state` and `progress_comprehension_display` emit the ARIA_CONTRACT roles, and every scope carries a visible heading with its own note above its own block. Addendum in the evidence file |
| **G6** Assessment authority | pass | `17B-03 D-06 item 6`: `defer_feedback` never moves the cursor and `marker_close` collects only human marks, so a deferred sitting parks on machine-scored items and an eight-item exam needs eight marks. No key leaked and no score invented, so the gate holds. Owner: the runtime phase that shipped `FEEDBACK_POLICIES` (Phase 6, amended 2026-08-24) |
| **G7** Course quality | pass | `17B-02 D-06 item 3`: the `lesson-authoring` skill is still a stub, so the lesson was authored against the 16A capability contract and `absorb-book`'s `## LESSON` contract directly, exactly as the stub instructs. Owner: the subphase that ships the lesson-authoring command surface |
| **G8** Flow/visual | agent half observed with five defects; visual half deferred-human | `17B-03 D-06 item 2` scope tree not on the shelf (FILE-04 degraded subdirectory scan; no route reads `scope.md`; owner: the phase scheduling FILE-04 and the 14B shelf wiring). `item 3` course areas carry no content (16B's recorded deferral; owner 14A/14B execution). `item 4` prediction recorded as a graded verdict, no participation-event producer for `activity_trace`/`activity_completed` (owner: the phase shipping the activity evidence producer). `item 5` `Item 1 of 8` never advances, `quiz_page.py:314` hard-codes the position (owner: the quiz surface, 13.5/13.9). `item 9` shelf next action not composed from session or evidence state (owner 14B / FILE-04 shelf wiring, 16C live-state collector seam). The 1280 and 375 visual acceptance is owed to Weibao (D-04) |
| **G9** Strategy/notes | pass | none |
| **G10** Portability/recovery | pass, after repair (see the 2026-09-05 note below the table) | `17B-04 D-06 item 10`: `course_package.build_manifest` gates every `PACKAGED_KIND` on `rights_granted(rights, "package")`, but rights live on a revision record and the frozen 14A surface has no grant or revoke operation, so granting `package` to an authored lesson or bank requires changing its bytes (a no-op commit is refused `journal.no_change`), which the audit-before-editing rule forbids. 14B's own `clean_restore` scenario missed it because it packages only a source granted at link time. Owner 14A, consequence in 14B. `17B-04 D-06 item 11`: `course_package._evidence_export_lines` filters events by the sidecar's `## Objectives` `id` column (graph object ids) while the evidence log's `objective` field carries bank slugs; the vocabularies never intersect, the sidecar has no join column, and no frozen loss category names an evidence loss, so 0 of 40 events exported silently and a restored course reads complete on the evidence axis while empty. Owner 14B. Both fixes are contract changes, outside D-06's single-file bound, so both were routed at the time rather than patched, and both were repaired on 2026-09-05 |
| **G11** Cross-cutting | pass | none. The egress clause is not applicable with its reason recorded verbatim (D-09); the refusal and redaction clauses are proved |

Also routed, not attached to a single gate: `17B-02 D-06 item 1`, the
`cmd_guard` directory skip list predating D-02's in-repo fixture rule,
fixed in phase in one file (`surfaces/cli.py`), owner 17B; and `17B-02
D-06 item 2`, the `[!KEY: <title>]` lint false positive, where `model.py`
compares the raw callout marker against `surfaces.lesson._CALLOUT_KINDS`
instead of routing through `_callout_kind_of`, recorded not fixed, owner
Phase 16A.

### Freeze condition

(Recorded 2026-09-05: G10's own defects were repaired after this condition
was written; the sentence below is left as it stood at the close and the
repair is recorded under it.)

Gates G5, G6, G7, G8, G10 carry named defects with owners 17A-03, Phase 6,
the lesson-authoring command surface subphase, 14A, 14B, FILE-04 and the
14B shelf wiring, the activity evidence producer subphase, and the quiz
surface (13.5/13.9); 17B closes with defects routed, freeze per Weibao's
Task 4 decision.

Neither verbatim freeze form covers G4 and G8's `deferred-human` legs,
because those are owed human reviews rather than defects. Recorded here
adjacent to the required wording rather than folded into it: the G4
screen-reader walk, the G8 visual acceptance at 1280 and 375, and the G5
default rollup choice are owed to Weibao personally and were never
agent-certified (D-04).

G10 was the one gate whose own check failed rather than carrying an
incidental defect. Both of its defects are contract changes in frozen
surfaces, so 17B-04 could not repair them without widening into a repair
phase, which D-06 forbids.

**2026-09-05, G10 repaired and re-run.** Under Weibao's directive of that
day, reaffirming his 2026-09-01 one, the two routed defects were repaired as
a deliberate contract change in its own commit (`247ffbe`) rather than left
owed. The change is additive: two new journal record types
(`grant_rights`, `adopt`), `OPERATION_TYPES` unchanged at six, no existing
operation's meaning changed, and an unadopted link still never copied into a
package. The drill was re-run unmodified over that commit and passes: 7 of 7
canonical objects, 40 of 40 evidence events, manifest complete by
recomputation, sockets refused inside the worker, and one honest
`machine-local: settings` loss row. Evidence:
`evidence/17B-04-restore-repair.md`. The freeze condition above stands as
written for the other gates; G10's own final state is now pass.

### Human acceptance (17B-04 Task 4, blocking)

Awaiting Weibao. Not yet answered; an agent never self-certifies the
milestone exit, and an unanswered checkpoint takes no silent default.

Verdict: ____________  Name: ____________  Date: ____________
