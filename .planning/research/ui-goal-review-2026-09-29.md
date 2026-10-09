# UI goal review and plain-language audit guide

October 1 continuation: [overall review and native reading modes](overall-improvements-2026-10-01.md)
implements a centered reader, existing split Study desk and wider Notebook
composition, plus tab-local view controls. It owns this bounded source diff
and rendered checks; visual preference and installed acceptance remain open.

Date: 2026-09-29. Status: proposed goal and bounded audit interpretation.
This document owns this chat's goal revision only. It does not replace the
product contract, prior audit evidence, or another chat's implementation plan.

September 30 source update: the [parallel overhaul](ui-overhaul-2026-09-30.md)
now owns the compact frame, course entry and reading/practice workshop
implementation and measured continuity checks. Twenty-four served desktop/narrow
light/dark observations pass, including note failure/retry, exact return and
keyboard answer/reload. One combined source-only run plus focused stale-test
repairs covers 170 Python scripts and 106 JavaScript cases; its dirty-tree gate
remains unsatisfied. This goal remains the experience owner; the packet owns
execution evidence and undo. Next action is source-preview review for human
visual preference and representative accessibility. Installed acceptance and
the fresh-build hold remain open.

## Improved goal

Make Itembank feel like a thoughtful place to learn: open the app and understand
where you left off, enter the right activity without sorting through software
status, work with readable and engaging material, and return without losing
your answer, notes, focus, or place. Give reading, coding, diagrams, and practice
the space and controls each needs while keeping navigation and behavior familiar.
Use prior audits to find useful missing abilities and unfinished interactions.
Preserve the breadth of viable ideas, but judge progress by complete tasks that
work in the actual app, rather than the number of features or completed plans.

The visual direction remains changeable. A precise study workbench is one
candidate, not a newly accepted theme or a reason to discard expressive teaching.

## What feature parity means here

Feature parity means people can accomplish the same relevant task to a comparable
standard. It does not mean identical buttons, layouts, implementation, or every
feature another application has. State the comparison and the task before using
the term. Parity between two Itembank views is a different claim from parity
with another learning product.

For example, two apps may both say they support reading notes. That establishes
very little. Can a learner attach a note to the intended passage, save it,
close and reopen the app, find it again, and understand what happens when the
source changes? If one can and the other only keeps text until reload, the
label matches but the usable capability does not.

The same distinction applies to questions. A category-assignment activity can
use dragging, buttons, or another accessible control. Compare whether learners
can assign and revise every row, preserve their answer, submit it reliably,
and receive the feedback allowed by the runtime. A visually similar drag
effect alone does not establish equivalent behavior. Execution output for code
also does not establish equivalent assessment or a settled grade.

Three separate questions must stay visible:

- **C1, capability:** Can the learner or author complete the relevant task?
- **C2, continuity:** Does it work through detours, restart, failure, and recovery?
- **C3, quality:** Is it understandable, comfortable, accessible, and engaging?

An app can satisfy C1 while feeling poor under C2 or C3. Appearance improvements
can improve C3 without closing a missing capability. Record both honestly.
Optional ideas remain available for later consideration; a scoped comparison
does not reject them or silently expand Itembank into institutional administration.

## How to reuse the prior audits

| Record | Useful contribution | How to read it now |
| --- | --- | --- |
| [September 18 renewal](ui-renewal-2026-09-18.md) | Connected learning journey, shared navigation, richer teaching, stable feedback | A changeable showcase and integration proposal, not the current app or a frozen design |
| September 19 parity audit and handoff, retained under `.reasonix/` | Joined course flow, authoring, teaching, assessment, recovery; named route failures | Historical evidence. Check later repairs before calling an old finding an open defect |
| September 19 subtle review, retained under `.reasonix/` | Explainer state, scroll and focus, narrow layout, course return, bounded help | U1-U4 were reproduced in a prototype. U5 was a consideration. Neither proves a current installed defect |
| [September 25 craft synthesis](ui-craft-2026-09-25/SYNTHESIS.md) | Actual learning material, deliberate hierarchy, subject-specific expression, complete journeys | Compare its viable visual directions on the same content. Do not equate minimalism or more decoration with quality |
| [September 28 absorption synthesis](absorption-2026-09-28/06-synthesis.md) | Groups repeated competitor findings and ranks concrete tasks | Its 604 source findings are an inventory, not 604 Itembank defects or a completion denominator |

For each retained finding, explain the learner's problem, the desired behavior,
the latest relevant repair evidence, and the next observable check. Keep the
original finding IDs in their owners. Avoid creating a second feature backlog
here or editing old observations to make them sound current.

Use precise status sentences: "present in source," "passed a synthetic browser
task," "passed in the packaged candidate," "verified in the installed app," or
"accepted by the user." These claims cannot substitute for each other.
Report counts only over an explicitly named set of tasks and required checks.

## What this chat actually observed

The installed app's Home and Courses screens were inspected on September 29.
Home repeated the course list, highlighted the first course by its stored order,
and used the same ambiguous multi-session message in the highlight and list.
Courses gave large rows and prominent reorder controls to each entry.
The sampled appearance used a black canvas, large navigation, a serif Home
title, heavy sans-serif controls, and blue emphasis.

Interpretation: administration and stored state receive more attention than
the learner's topic or immediate activity. The proportions and mixed typography
do not yet communicate a clear visual character. These are design judgments,
not measured learning outcomes. Reading and quiz feel were not inspected in this
pass. No real coursework or assessment content was opened.

## Next review, limited to five questions

1. **G1, entry:** Can someone identify their exact resumable activity from Home,
   with an understandable choice when several sessions exist?
2. **G2, composition:** Do the course list and navigation scan efficiently while
   the activity receives enough working space at desktop and narrow widths?
3. **G3, expression:** Does real subject material make the workspace recognizable,
   with a coherent role for typography, visual marks, diagrams, and playful detail?
4. **G4, continuity:** Can someone read, answer, inspect permitted feedback, open
   a reference, return, and recover a failed save without losing supported state?
5. **G5, delivery:** Do the same tasks work in the final packaged candidate and
   installed app, with human visual and accessibility checks recorded separately?

## Concurrent-work boundary

The active successor from `Review audit backlogs` owns candidate browser checks,
reproduced repairs, packaging, and its existing implementation evidence record.
Its September 29 snapshot reports a rebuilt archive, an embedded-daemon authoring
gate, and full preflight in progress. This is another chat's reported progress,
not this chat's independent verification or a final passing result.

This chat owns this new goal review and the linked capture entry. It does not
edit product source, STATE, EXEC-CONTEXT, the implementation record, or existing
backlogs. It does not run another full suite, rebuild the candidate, replace the
installed app, or steer the other chat. Those boundaries allow this review to
proceed concurrently; overlapping implementation would require one named writer
per shared file and agreement on the final candidate to test.

Recovery: remove this proposed review and its capture entry to undo this pass.
No existing audit evidence, product behavior, accepted course, or learner data
is changed. No commit, push, external message, or binding scope change is made.

## Implemented entry slice, September 29

The later instruction, "implement accordingly while the other chat is working
through [$daisy-chain-work](/Users/weiwei/.codex/skills/daisy-chain-work/SKILL.md)",
authorizes this bounded source implementation. It supersedes this document's
earlier audit-only write boundary for this slice, not the older evidence.

Home now highlights the first course in the saved order with an unambiguous,
canonically resumable sitting. It does not claim to know the learner's highest
priority or most recent overall activity. Without one, it keeps the first-course
fallback. It shows runtime-issued practice/test mode and question position when
known. Ambiguous sittings retain their course chooser; unknown positions stay
unknown. Reordering preserves this rule and the exact session link.

Home's heading now uses the control typography, course rows have less padding,
ordinary "Up to date" chips are hidden as redundant, and visible Drag controls
receive less emphasis. Nonordinary attention states and all course options stay
available. Touch target sizes and the narrow navigation remain unchanged.

The source owner is this UI chat, `01a0eec6-892a-78e2-9c9e-08df41fb0883`.
The other candidate chat, `01a0eebd-95bd-7343-b1ec-2a676010eeef`, received a scope
message before these edits and explicitly excluded this later slice from its
completed candidate evidence. This implementation does not invalidate its
earlier quiz/reading observations, but the old package does not contain this UI.

Checks passed: desk experience (including a served, read-only synthetic shelf),
desk craft, responsive product, course resume, course shell, 12 JavaScript desk
reorder cases, and quick preflight. The browser rendered the revised desktop
Home and 390px Home, with document width equal to viewport width. Moving an idle
course down preserved the saved-session highlight and question context. Reload
preserved the saved order and exact session link. No real course was opened.
This is source and Chrome evidence, not new native, packaged, installed, human
screen-reader, physical-touch, or learning-benefit acceptance.

Scope sampled only the desk/shelf helpers and shelf script in `surfaces/daemon.py`
and the product CSS in `surfaces/presentation.py`, not those full modules.
No parser, scorer, assessment disclosure, rights, or persistence rules changed.
Recovery is a bounded reverse diff over the four named source/test paths; do not
reset the shared checkout or remove another chat's edits.

Operational limit: importing filesystem code into the computer-use REPL while
trying to save a browser screenshot timed out and reset that REPL. No screenshot
file was created. Subsequent browser rebinding was unavailable. The successful
observations above preceded that failure, and the temporary viewport had already
been reset. The owned disposable server was then stopped through its test helper.

## Final candidate packet for the existing chain

GOAL: Include this Home/Courses slice in the combined native candidate and verify
that it preserves the already checked quiz, reading and authoring paths.

BASE: Existing local checkout, committed revision
`8ccd45832b66b0b86bb406d6232ef0633ef71dc3`, with unrelated uncommitted work.
Verify these dirty-input fingerprints before building:

| Path | SHA-256 |
| --- | --- |
| `surfaces/daemon.py` | `38a12a1bb6bea5f4bd81e580ae417bbeeaefd5615aa54a80af699c850274bcd9` |
| `surfaces/presentation.py` | `f1a9d57b70e1360bf9ad7f6aa2e8487d5a689a8983a8087e8aa2097160e4af26` |
| `tests/desk_experience_roundtrip.py` | `bae4fdf321b1bf733d3cf0d721f8a7db413b94efb44781ada5499480aade761e` |
| `tests/js/desk_craft_reorder.test.mjs` | `5cd9adafe7f7d5d1cccc0aea6814744ca3009b27d907d22839d6765258151758` |

AUTHORITY: Rebuild and test the separate synthetic candidate. No commit, push,
release, installed-app replacement, real coursework, learner-data mutation,
donor code copy, or change to scoring/disclosure/rights authority.

WRITER: This chat freezes its four source/test paths after dispatch. The existing
candidate chat owns candidate integration, evidence in its current implementation
record, and only reproduced repairs if needed. Do not edit concurrent instructions.

AUDITS: This goal review reconciles sampled September 18, 19, 25 and 28 UI
findings. G1/G2 have partial source/browser evidence. G3 subject expression,
broader G4 continuity and G5 human/installed acceptance remain in their existing
owners. The prior absorption implementation record remains the candidate owner.

NEXT ACTION: Verify fingerprints, run `python3 tests/desk_experience_roundtrip.py`
and the desk JavaScript tests, then rebuild the combined candidate.

GATE: In the separate native candidate, reproduce idle-first/saved-last course
order and verify Home's exact resumable sitting and runtime position. Move an
idle course, reload, and verify course order and session destination. Check the
narrow layout without overflow. Reuse the packaged workbench gate. Run one full
preflight on this final combined input after repairs, with dirty-tree failure
reported separately. Do not certify this slice from the earlier package.

RETURN: Final source fingerprints, candidate/build evidence, actual failures,
and human-only or unavailable checks. Stop after this integration gate; do not
create another chat to retry unchanged external or human-only conditions.

## D4-D7 color and visual-detail implementation

The later user instruction, "implement d4-7 accordingly?", authorizes this
appearance slice after the previous combined candidate finished. This source
revision supersedes that candidate's appearance inputs, not its historical
quiz/reading evidence. The installed application is still separate.

- D4: Neutral charcoal dark surfaces and warm-white light surfaces replace
  the green-tinted base. OLED retains a true-black page with raised dark grounds.
- D5: Blue is the new default source accent in both the theme and settings
  schema. Existing saved accents remain unchanged. Success, error, warning,
  unknown and pending colors remain fixed, independent of the action accent.
- D6: Source excerpts have a cyan-toned border and surface; private notes use
  violet. Authored labels preserve their meaning without color. Examples,
  existing comparison/plot activities and code receive coherent working frames.
  This is presentation of existing authored blocks, not new diagrams, new
  lessons, code execution, or altered teaching/scoring content.
- D7: Product headings use the shared control typography while the reading
  title retains its deliberate prose typography. Topbars, fields, disabled
  buttons and walkthrough spacing share the same visual roles. Hover/press
  transitions remain brief and reduced motion disables them.

Owner: this chat, for `surfaces/theme.py`, `surfaces/presentation.py`, the
`product_reader_css` helper in `surfaces/lesson.py`, settings schema defaults,
the bounded theme test update, and `tests/visual_character_roundtrip.py`.
Other dirty source, instructions, and candidate records were preserved.
Only the relevant palette, reader CSS, product CSS and test symbols were read,
not the entire implementation modules.

Verification: theme, stylesheet, lesson, responsive product and desk experience
checks passed. The new visual-character check measures body, muted and teaching
text at 4.5:1 on the relevant backgrounds across all seven looks, light/dark/OLED
and four accent sources. It checks color-role independence and reduced motion.
Quick preflight and diff checks passed. No full-suite or native-candidate result
from the earlier build is attributed to this later slice.

Browser review used a disposable sample course with explicitly synthetic source
and note blocks, plus example code. Dark Home, reading and practice rendered
with the revised palette. At 390px, reading and practice had no horizontal
overflow. Chrome's Dark Reader extension recolored the light page even though
the authored theme tokens were correct; the clean in-app browser then verified
the warm-white light Home and reading with no extension overrides. Do not change
the user's extension or treat its transformed screenshot as the app's palette.
Human preference, screen-reader and physical-touch acceptance remain open.

Recovery: reverse only this slice's bounded diff. Do not reset the shared tree.
New default accents do not migrate or overwrite saved settings. The new teaching
tokens are generated presentation values, not new persisted schema fields.

Final delivery evidence: `sh scripts/build_shell_macos.sh dist` rebuilt the
macOS candidate and checksum-verified its DMG after the final CSS edit. The
visual-character `--runtime` gate passed against both `dist/itembank.pyz` and
the frozen runtime inside the app. It generated an actual quiz through each
packaged CLI and verified the new light/dark and teaching-role tokens, rather
than assuming packaged/source parity. Settings, presentation and visual-system
checks also passed. The presentation harness deliberately prints one expected
negative-fixture failure before its successful final result.

Final archive SHA-256:
`e65494ff0c223d66ce313c7aeb29de1e89c9a04c0ace14bb87379d954c9f01e2`.
Final DMG SHA-256:
`ef59c3ae8b6ee5ca59e6ee5ac24ed3260b1afa1e9035cb7f0df71ed42dcb8064`.

The final note textarea explicitly uses shared card, ink and edge tokens,
overriding its older pale fallback in dark mode. Product source remains
uncommitted; no installed-app replacement or release occurred. Full preflight
and a new native-shell visual trial were not repeated for this appearance slice.
The temporary preview servers and owned review tabs were closed.

## Visual experience priority, September 30

Origin: [the user's priority statement](../USER-VISION.md#2026-09-30-prioritize-visual-experience-and-richer-app-inspiration).
This dated addition owns experience priorities, not another implementation lane.

**Direction:** Lead UI iteration with rendered composition and interaction
quality. Passing tests establish only their named behavior, not visual
preference, learning value or coherence. Retain required gates; avoid new
implementation-mirroring tests and repeated full runs for unchanged code during
reversible design exploration.

**Proposed sequence:** compare the current source preview with two materially
different compositions using identical synthetic material; choose by reading,
answering and reference-return experience; refine typography, proportions,
color, density and interaction details together; integrate the selected slice;
run focused behavior checks and required delivery gates. Existing package and
installation holds still apply. Report rendered before/after evidence before
test totals. No comparison or human acceptance occurred in this records pass.

Primary-source references checked September 30, offered as inspiration:

- **V1, hierarchy and craft:** [Linear's March 2026 refresh](https://linear.app/now/behind-the-latest-design-refresh)
  reduces navigation emphasis, compacts tabs and softens separators. Its live
  palette tool and old/new toggle support rapid in-context iteration. Proposed
  transfer: emphasize learning material and make visual comparison cheap.
- **V2, interactive teaching:** [Brilliant's algebra example](https://blog.brilliant.org/solving-equations/)
  and [learning FAQ](https://brilliant.org/faq/) describe interactive
  problem-solving. Proposed transfer: linked diagrams, prediction, manipulation
  and staged explanation where the objective benefits.
- **V3, spatial organization:** [Obsidian Canvas](https://obsidian.md/canvas)
  combines notes and media in a visual workspace stored in a local open format.
  Proposed transfer: optional concept/source maps with a readable list fallback.

Other richer candidates remain proposals: resizable reading/reference/note
panes, contextual passage actions, visible example steps and code execution
traces. Each needs a specific task and useful keyboard/static representation.
Reuse current capability contracts before adding a framework or schema.
No candidate is rejected merely for being ambitious or optional.

Disposition: IL-20260930-01 keeps the experience priority Core and richer
interaction candidates Prototype. Recovery removes only this dated addition and
its matching capture/vision/ledger entries, preserving prior and concurrent work.
No product source, learner data, commit or installation changed. This pass
sampled the current goal, overhaul packet, relevant contract and recent vision
entries; it did not inspect the rendered app. The structural vision audit's
historical link/relationship backlog remains open and does not measure UI quality.


## October 1: UI design and character as the next implementation slice

Origin: [exact user question](../USER-VISION-INBOX.md#2026-10-01-implement-parity-through-ui-design-and-character).
Status: proposed priority and rendered specimen, extending the September 30
visual/character direction and IL-20260930-02. No new accepted visual theme,
framework, curriculum, lesson grammar or milestone scope follows from it.

A current disposable source preview of the original coding unit was inspected
in continuous and guided modes. At 1030 by 571 pixels, the guided first concept
heading began at y=606.8, below the viewport. Metadata, title, mode copy and
reader controls precede it. This supports a concrete hierarchy problem on one
route. It does not establish the installed app's state or prove that UI causes
all of the gap with Boot.dev or Brilliant.

The [boundary lab study](../../prototypes/ui-character-20261001/README.md)
provides a connected course/concept/repair specimen, subject-derived character,
a real comparison experiment and a fixed, labeled teaching example of code
feedback. Its D1-D5 table names the proposed native edit seams and acceptance
tasks. The [platform comparison](platform-parity-2026-10-01.md) keeps broader
parity separate from visual direction; the [coding owner](coding-learning-2026-10-01.md)
retains its current implementation and learning-review gates.

Proposed next action: correct the native guided lesson's first-screen hierarchy,
then join its existing teaching/practice journey using one shared presentation
owner. Review the rendered experience before spreading its composition to one
visual unit in another subject. Keep source, packaged, installed and human
acceptance distinct. Neither the prototype nor its palette is final acceptance.

Record operation: additive goal section, expected base SHA-256
73c38ae116612360a9b16889fb15ad3f74afe3752064979a2a41273b0a0b48bd; additive inbox
entry, expected base SHA-256
b735121edc24b0f838ec6b94f534299edab98e814aba079e625deaa7f2be7a05. Preserve earlier
bytes and compare before atomic publication. The prototype starts from absence.
Undo removes only these dated additions and the prototype directory. Current
production writers, dirty code, STATE and the permanent ledger are preserved.

Bounded drift review: exact words are captured, observations and design
inferences are labeled, existing idea routes remain, and no optional capability
is rejected. No scoring, disclosure, rights, storage or accepted format changes.


## October 1: interaction craft in the visible object

Origin: [exact user observation](../USER-VISION-INBOX.md#2026-10-01-subtle-interaction-details-shape-perceived-quality).
The [marker problem](../PROBLEM-LEDGER.md#p-20261001-01-boundary-marker-looks-draggable-but-is-decorative)
owns reproduction, repair and its exact remaining review gates. This extends
IL-20260930-02 and D1-D5 without freezing a new theme or activity format.

The user names subtle presentation and gesture details as part of quality.
The prototype's visible triangle invited dragging while the real control sat
below it. Direct marker manipulation now matches that invitation, removes the
duplicate visible track and keeps native keyboard semantics. Human preference
for the result remains unverified.

Carry three craft questions into each representative interactive treatment:

- C4, invitation: Does the visible object communicate where an action begins?
  Inspect direct manipulation, hit areas, cursors and discoverable alternatives.
- C5, feedback: Do pointer movement, values and visual consequences update
  together without accidental text selection, lag or a surprising jump?
- C6, completion and recovery: What happens at bounds, release, cancellation,
  resize, keyboard focus and coarse input? Preserve a useful static form.

These refine the existing C1-C3 capability/continuity/quality review rather than
create another backlog. Apply them to selected controls and complete tasks, not
as a requirement for decorative animation on every element. Technical checks
prepare review; they do not decide whether an experience feels premium.


## October 1: broader interaction craft pass

Origin: [exact continuation](../USER-VISION-INBOX.md#2026-10-01-extend-interaction-craft-across-the-specimen).
Status: implemented in the specimen, browser/source verified at its named
checks, with human and native promotion separate. The existing C4-C6 craft
questions now have additional worked examples, not a new product format.

The [prototype owner](../../prototypes/ui-character-20261001/README.md#broader-craft-pass-october-1)
records F1-F5: actual navigation/return, reopenable experiment choices, inline
inspect/close feedback, narrow-layout controls and code readability, and local
focus/selection/reset cues. [P-20261001-02](../PROBLEM-LEDGER.md#p-20261001-02-specimen-navigation-discards-browser-history)
owns the reproduced Back defect. The current reading/coding source writers
remain untouched. D1-D5 still owns native implementation; this pass neither
replaces that route nor claims all UI polish or platform parity complete.

Carry forward direct manipulation, meaningful state feedback and exact return
as parts of composition. Avoid making a control look interactive while placing
its action elsewhere, and inspect density/indentation at an actual narrow width.
The renderer should own how a task feels while canonical state and assessment
authority remain in their existing owners.


## October 1: next local chat for the small details

The user asked what other small details could be improved and to continue in a
new chat. The [next-pass packet](../../prototypes/ui-character-20261001/NEXT-PASS.md)
owns a ranked A1-A5 investigation/implementation queue: drag cancellation,
anchored contextual tools, code selection/copy, honest status feedback and
layout/focus as content changes. These are candidate review areas, not a claim
that all five are missing or defective.

The sending chat freezes and releases its prototype write scope for the new
local chat. Current source and reading/coding writers keep their paths. Existing
C4-C6, D1-D5, prototype evidence and human/native gates remain authoritative.
This continuation authorizes bounded source review and prototype refinement,
not a new product format, accepted visual theme, app installation or Git action.


## October 1: native D1-D5 parallel implementation

The user's continuation, "run in parallel accordingly", authorized the bounded
native pass through the existing D1-D5 route. Three parallel lanes owned lesson
hierarchy/code/glossary, one comparison treatment and real native journey checks.
The [native pass owner](../../prototypes/ui-character-20261001/README.md#d1-d5-native-parallel-implementation-october-1)
and [exact evidence](../../prototypes/ui-character-20261001/evidence/native/checks.md)
record the implementation, source fingerprints, browser faults and recovery.

D1's first concept moved from below the 1030x571 viewport to y=303.4. D2 and D3
now provide bounded glossary return and exact public-code selection/copy. D4
promotes direct manipulation in an existing teaching comparison, preserving
its static meaning and native keyboard range. D5 proves course entry, lesson
detour and exact saved-session Resume. A real header hit-test defect was fixed
in the shared presentation owner; the selected answer survived the course return.

Focused source/browser checks and quick source-only preflight pass. The frozen
specimen remains historical, and unrelated dirty coding/reading source stays
preserved. Native clipboard readback, installed app, physical touch, screen
readers, browser-native zoom, human visual acceptance and learning benefit remain
separate gates. Exact Resume uses the course route; generic lesson Continue to
practice retains course context without the saved-session identifier. No new
format, palette acceptance, app installation, Git action or authority change
follows from this source pass.

## October 3: course map composition and exact context return

Origin: the user asked "whats next to be considered?" and then
"implement accordingly and more" after five ranked considerations, C1-C5.
Interpretation: implement the next useful native course slice and adjacent
visible improvements. This does not settle a final visual language or any
pending assessment format.

Scope and readiness: the existing course-guidance/read-only projection owns
prerequisite facts and runtime-released evidence. The concurrent backlog pass
owns prerequisite/history logic, bounded source discovery/impact, synthetic
transfer and author cancellation/retry. This pass owns presentation in
`surfaces/course_context_view.py`, scoped shared CSS, bounded map/source
rendering seams and exact objective return. Graph identity, source rights,
runtime scoring/disclosure, accepted revisions and operation authority remain
with their existing owners. No schema, learner-file or evidence migration is
needed. Read roots are this repository and its prior source/research pointers;
verification uses original synthetic temporary courses and local Chrome only.
No external content or learner data is sent remotely.

- C1 uses the current projected authored prerequisites, rationale and released
  evidence. An addressable prerequisite detour carries exact objective IDs;
  return is offered only when the currently projected relation still exists.
- C2 separates numbered objective headings, prerequisite explanation and a
  visible activity area. Sources/treatments and relation metadata use native
  disclosures. Shared colors/type remain user-switchable. Narrow layouts stack
  in document order, with focusable fragment destinations and 44px controls.
- C3 stays with the concurrent synthetic transfer/rubric owner rather than
  creating a second unit or grader.
- C4 puts affected objectives ahead of long revision fingerprints, which move
  into a native disclosure. Source previews have a named keyboard scroll region.
  Source detours return to the exact originating objective, including after a
  prerequisite detour. Unknown/repeated return IDs create no return control.
- C5 records source checks and reviewable recovery below. Source consolidation,
  Git actions, app delivery, human preference/accessibility and learning benefit
  remain distinct from this bounded presentation result.

Expected bases and before-images live in the ignored
`.reasonix/course-map-craft-20261003/` operation folder, with .txt recovery
suffixes. The source patch touches only map/source presentation seams; preserve
the other owner's concurrent additions. Undo only this pass's context-matching
diff and shared CSS block, then remove its new view/test module if unused.

Visual review exposed a separate composition problem: raw readiness diagnostics
preceded every objective and dominated the phone page. The map now shows its
objectives first and keeps full checks in a native disclosure below them.
The closed summary still states clean, review-needed, failed or unavailable;
failure details are retained, and current activity eligibility is unchanged.

Completed commands:

- `python3 tests/course_context_journey_roundtrip.py --browser-shots .reasonix/course-map-craft-20261003/screenshots`
  passes read-only GETs, exact relation/source return, fresh-process restart,
  unknown/repeated identity refusal, escaped authored text and withholding
  changed source content. Chrome passes six light/dark layouts at 1280/390/320,
  native keyboard activation and exact fragment focus, script-free 320px pointer
  return, changed-source revision disclosure and no horizontal overflow.
- `python3 tests/course_workbench_roundtrip.py`,
  `python3 tests/course_guidance_engine_roundtrip.py`,
  `python3 tests/course_guidance_ui_roundtrip.py`,
  `python3 tests/course_guidance_journey_roundtrip.py`,
  `python3 tests/a3_course_workflows_roundtrip.py`, and the concurrent owner's
  `python3 tests/backlog_course_roundtrip.py` pass on the joined source.
  The existing workbench assertion now verifies source selection and exact
  return identity rather than requiring the old query-free URL.
- `python3 scripts/preflight.py --quick --source-only` exits zero. Every running
  lint, broken fixture, guard, mirrors, README, schema, vendored, path and summary
  gate passes; build/full Python/full JS/clean-tree gates are skipped by these
  flags. The concurrent backlog owner is running the single full source-only
  suite in `.reasonix/backlog-implementation-20261003/preflight-full.log`.
- `python3 scripts/vision_audit.py` exits zero, with no missing dated
  interpretations or inbox dispositions. Its old missing/ambiguous reference,
  relationship and downstream-link debt remains open. `git diff --check` passes.

Desktop and 320px dark map screenshots plus the narrow changed-source view were
visually inspected. A disposable native synthetic preview was prepared locally;
its browser tab is queued for this chat. No real course, app install, Git action
or human learning/accessibility acceptance ran. Source modules were sampled by
symbols: course_workbench, daemon and presentation were not read in full.

Operational finding: waiting for a page's existing network-idle state can race
the next keyboard navigation. The browser helper now awaits the navigation
it triggers. A first script-free pointer check also timed out while scrolling;
the final reduced-motion native-pointer run passes. Keep these original failed
checks distinct from the passing final run. Snapshots prove the view does not
append evidence or change accepted data; the sole browser source mutation is
an explicitly injected synthetic changed-file case.

Recovery must preserve the concurrent backlog owner's later course-route ID,
empty-prerequisite fast path and evidence-copy changes. The before-image is not
a license to overwrite the whole shared module. This pass's owned diff and
final fingerprints are retained with its local receipts.

## October 3: review from the first implementations to today's UI

Status: historical sampling, native browser observations and a reversible
design specimen. No product source, assessment contract, accepted learner file,
Git commit, package or installation changed. This extends the existing UI owner
and IL-20260930-01's visual-experience direction. The specimen is Prototype;
the recommendations below are review inputs, not accepted implementation plans.

### Scope and authority

The request is preserved in
[the capture funnel](../USER-VISION-INBOX.md#2026-10-03-review-the-implementation-history-with-ui-emphasis).
Read AGENTS, AGENT-WORKFLOW sections 1, 2, 5 and 7, STATE's current position,
SOURCE-TO-COURSE's learner-experience contract, the September 30 visual priority,
the existing prior-implementation owner and UI-REMAINING reconciliation.
Earlier audit pointers were used to avoid repeating completed source work.

HEAD was `28bf561`; 1,163 commits were reachable. Ordered logs, selected early
snapshots and symbol histories were inspected. This is a sampled retrospective,
not a claim that every commit or every surface was reviewed. Large source
modules were read around shell, course-frame, navigation and backlink symbols.
The parser, runtime and evidence implementations were not audited in full.

| Historical checkpoint | Verified purpose | Current implication |
| --- | --- | --- |
| `c3ee935`, July 26 | Machine-checkable bank contract and an offline 800px quiz with browser scoring. | Preserve the useful authoring feedback loop; reconsider bank-centered learner wording. Browser scoring was subsequently superseded by runtime authority. |
| `93da874`, July 27, and `e25fbdf`/`deb754e`, August 5 | Agent runtime, scoring consolidation and protocol/surface separation. | UI revisions consume current runtime state and preserve its scoring and disclosure authority. |
| `4678fb0`, August 7, and `4871b52`/`912e0da`, August 8 | One daemon, shared presentation adapter and the first linked lesson reader. | The reader's original byline and raw truncated question previews still reach the current learner flow. |
| `a79c626`/`44482d5`, August 24 | Shared type/density tokens and accessible component primitives. | Reuse these primitives while evaluating composition across screens. Token reuse alone does not establish a coherent rendered journey. |
| `9edd9e8`/`1f092d7`, September 8, through `49f0499` and `b37fac3`, September 25/30 | Course operations, learner workspace and integrated course workbench. October 3 source adds guidance and context work. | Review the current dirty source and normal native entry flow. A dated source or installed snapshot does not establish acceptance of later work. |

### Ranked findings and proposed revisions

**F1, P2: repeated course context delays useful content.** At 1280x720 the
course title began at document y=180, Overview at 388, Next activity at 502 and
the resume link at 526. At 390x844 the resume link began at 578. The course name
appears in the topbar and heading; the area appears in Current area, navigation
and another heading. No page overflow was observed at these sampled widths.
Proposed revision: one course header, one area indicator and a compact activity
region. Owner: `surfaces/presentation.py:surface_shell` and
`surfaces/daemon.py:_course_frame`. Gate: long course titles, keyboard navigation
and the actual primary action at 1280, 390 and 320, with useful reflow at zoom.

**F2, P2: the same saved sitting has three competing resume labels.** The
native overview exposed Resume your saved sitting, Resume practice and Resume
Boundary workshop. All three hrefs carried the same session and course IDs.
Proposed revision: one primary resume action, a distinct lesson detour and a
collapsed history list when it adds no new current action. Preserve other
sessions, reports and unavailable-state recovery. Owner: `_course_frame` and
`_course_guidance_html`. Gate: active, complete, pending and unavailable sittings
remain independently reachable; a projection never invents completion.

**F3, P2: the continuous reader still feels like a separate bank document.**
The normal Learn-to-lesson flow changed from the course frame to a separate
wrap/header composition. It displayed Application: itembank and Reading
material for this bank. Its first lesson section began at y=447 on desktop and
415 on the phone. Guided reading already has a more compact header and About
this reading disclosure. Proposed revision: reuse that concise orientation and
the shared app frame for both reading modes, while preserving the content's
serif measure and the wider space needed by code, tables and diagrams.
Owner: `surfaces/lesson.py:product_reader_css` and `lesson_page`, plus the shared
presentation frame. Gate: course-to-continuous/guided-to-practice-to-return,
including the existing rich controls and useful plain/static representations.
An optional section outline should reuse `_reader_nav_html` and its disclosure
filter; the sampled five-section lesson had no exposed outline. This observation
does not establish that all lesson styles lack section navigation.

**F4, P2: learner-facing question links retain author diagnostics and raw
markup.** The byline promises a new tab. Clicking the actual Q1 section link
navigated the same browser tab to `/quiz/coding_boundary_unit#q1`. Its preview
included literal triple-backtick Python markup because `_backlinks_html`
escapes the first 100 characters of the raw stem. Items testing this and No
items reference this section yet also expose the bank-author view during
reading. These strings and the truncation originate in `912e0da`.
Proposed revision: truthful navigation copy, concise escaped prompt previews
and deliberate Practice this section actions where a binding exists. Keep
author linkage diagnostics in the author/review flow. Do not infer objectives,
hide unsupported states or create a new content parser. Owner:
`surfaces/lesson.py:SUB_BYLINE`, `_backlinks_html` and existing parsed fields.
Gate: plain, code, math and visual prompts have useful previews without raw
markup or unsafe HTML; offline/export navigation remains honest.

**F5, P2: section practice links lose the course return context.** Opening
Continue to practice from the lesson carried `course=<id>` and the practice
context link returned to that course. Opening Q1 under Items testing this used
`/quiz/coding_boundary_unit#q1`, with no course query. In the same native fixture,
the resulting Boundary workshop context link pointed to `/`, the desk.
This reproduces breadcrumb/context loss. It does not establish lost answers,
a changed runtime score or loss of the saved sitting itself.
Proposed revision: carry the admitted course, occurrence and appropriate
session context through the existing backlink adapter. Preserve unbound/offline
navigation and refuse ambiguous identities rather than guessing.
Owner: `_backlinks_html`, `lesson_page` and the daemon's existing lesson/quiz
context adapters. Gate: start from a course, use a section question, follow its
course return, and verify exact identity, unfinished input, focus and no new
response event. Include one lesson used by more than one course.

### Concrete specimen and measured limits

[The self-contained specimen](../../prototypes/history-ui-20261003/index.html)
shows a compact header, one primary resume action, a distinct lesson detour,
nearby objectives and collapsed history. It uses fictional data from the
existing native interaction-lab fixture. Resume is disabled; other links are
local layout anchors. It is not wired to the runtime or an implemented repair
of F5. No synthetic skill/mastery/completion score is displayed.

The resume control moved from y=526 to 370 at 1280x720 and from 578 to 407 at
390x844. At 320x740 it began at 426. The specimen had no horizontal document
overflow at these three widths. Keyboard Enter expanded and collapsed its
native Course tools disclosure. These establish placement and the sampled
interaction, not human preference, physical touch, screen-reader acceptance,
learning effectiveness or installed behavior. Dark, zoom and broader state
matrices were not exercised in this pass.

Local measurements and screenshots live under the ignored
`.reasonix/history-ui-20261003/` evidence folder: baseline overview and reader,
the reproduced question-return context, and the specimen at all three widths.
Browser inspection used only the disposable synthetic native root created by
the existing `native-preview.py`; no real learner roots or provider calls were
needed. Initial keyboard probes against a role locator and an unfocusable body
failed. Targeting the visible summary directly and using native scrolling
completed the intended checks. Coordinate measurements use document position;
an earlier capture with restored scroll was corrected before comparison.

### Continuation and recovery

Start a bounded native revision with F5 context propagation and F4 truthful
copy/previews, then integrate the chosen F1/F2 composition and F3 reader frame
through the same existing authorities. The specimen demonstrates a candidate,
not a binding new theme. The earlier source-question registration, immutable
submission provenance and restore-reference policy choices remain owned by
their current records; this UI review does not answer those contract choices.

The current prior-implementation owner still distinguishes uncommitted source,
failed original full runs with passing scoped repairs, installed delivery and
human acceptance. That distinction also applies to this review. No full suite
was repeated for this static design study. Final quick source-only and vision
gate results are recorded below when executed.

Recovery removes only the new specimen and these dated record additions after
checking their recorded fingerprints. Preserve all earlier and concurrent
source/document edits. Expected-base fingerprints, before-images and a local
operation journal are retained in the ignored evidence folder.

Final checks: `python3 scripts/preflight.py --quick --source-only` exited zero.
Every executed gate passed; build, Python suites, JavaScript and clean-tree
checks were skipped by those flags. `python3 scripts/vision_audit.py` exited
zero with no inbox entry lacking a disposition and its existing structural
relationship backlog. `git diff --check` passed for this pass's paths. The
lesson, presentation and daemon SHA-256 fingerprints still match the captured
pre-review bytes. These receipts certify the bounded records/specimen pass,
not a native UI repair, a clean candidate or the earlier combined full run.
