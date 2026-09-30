# UI goal review and plain-language audit guide

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
