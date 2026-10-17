# Fresh learning workspace: implementation prompt

Build a polished, complete personal study application that I can actually use.
Start with the coherent studying experience described in
`ORIGINAL-QUIZLET-PROMPT.md`, then grow it into the learner-owned learning
workspace in `FULL-LEARNING-WORKSPACE-BRIEF.md`. Use an original name and assets.
The stages below sequence that full vision; they do not discard its breadth.

Your main success measure is whether I can do useful learning work easily,
with good feedback and durable results. Prior architectural choices, planning
volume, component counts and test totals are not evidence of product quality.

## Starting point

Work in a separate candidate project. Do not overwrite, move or delete my
existing Itembank repository or learner data. Do not inherit its planning tree,
architecture or application instructions as this candidate's design contract.
My personal preferences and explicit instructions still apply.
Follow the instructions applicable to the chosen candidate workspace.

If I provide the better existing study app, first run it and evaluate its real
create/edit/study/reopen/backup workflows. Use it as the foundation if those
work and its code can support the scope. Fix demonstrated problems there. If
no working app is supplied, start with a clean implementation. Do not create
a third app merely to repeat work that already delivers the desired experience.

For the initial build, derive the experience from these briefs rather than
examining old Itembank plans. After the study baseline works, selectively
inspect old code only for a specific observed gap. Do not port old abstractions
or records wholesale.

The supplied Quizlet-style prompt is the functional study baseline, including
its editor, modes, imports, accessibility, storage and completion criteria.
This prompt adds execution priorities, quality gates and the broader product
direction. It does not remove any of those requested modes.

## What the app should feel like

A serious, welcoming learning product with a familiar dashboard, fast set
editing, a strong study workspace, and an obvious next action. Let me study
before I organize a whole curriculum. Navigation, state changes, saved work
and recovery should be obvious without reading implementation terminology.

Use React and TypeScript with a straightforward build setup when starting
empty. Prefer the supplied working app's framework if there is one. Keep
storage, grading, scheduling, import/export and presentation separable, but
do not build a plugin system or generic framework before it solves a real need.
Make visual and interaction decisions yourself within the brief. Do not stop
for routine taste choices. Keep me informed of actual findings and blockers.

## Build in complete stages

### Stage 1: dependable daily studying

Implement the baseline prompt's dashboard, set/card editor, manual creation,
pasted/CSV/TSV import with preview, full backup/restore, and flashcard studying.
Make all visible controls work. Support real image persistence and readable
math, code and multilingual content. Include removable original demo content.

Then complete Learn, Test, Write, Spell and Match with correct generation,
appropriate checking, saved results, missed-item return and review scheduling.
Follow the baseline prompt's details for alternate answers, normalization,
manual correction, small sets and duplicate cards. Show self-reported known
cards separately from correct typed responses or settled test results.

Make creating a small set and starting useful practice a short, direct path.
Use keyboard shortcuts, good focus states and phone layouts. Surface saving,
unsaved changes, unavailable speech and storage errors clearly.

No AI, account, subscription, payment or network call is required for this
stage. Do not let later features postpone a usable, persistent study app.

### Stage 2: durable sources and reusable learning work

Once Stage 1's gate passes, make sources first-class. Preserve originals and
their titles, locations and revisions. Support useful Markdown/plain-text
intake first and add optional document intake through actual adapters with
explicit unsupported states.

Link existing material rather than recreating it. Search only user-selected
roots and distinguish read, link, copy and write-back. Do not silently modify
Obsidian or external folders. A local inventory can offer relevant existing
notes, lessons and sets without requiring exhaustive organization up front.

Let me read material, save notes, annotate where supported, search saved work
and return to its context. Cards, explanations and questions retain source
references and authorship. Generated material is editable and reviewable;
learner wording is preserved. Missing or changed sources flag links without
deleting notes or study history.

Add optional AI for selected-source explanations and editable drafts. Preview
the exact context that will leave the device. Record citations and uncertainty.
An explanation can be saved as a note or card and found later. A failed or
disabled provider does not strand the learner or break existing material.

### Stage 3: a course that actually teaches

Build one representative course loop:

Source -> objective -> appropriate reading/example/activity -> practice ->
useful feedback -> saved evidence -> scheduled review -> next-day return.

Connect the existing study objects to objectives and courses. Let courses group
materials and offer a useful path without forcing everything into flashcards.
Choose treatment by objective: a clear original passage may need only reading;
calculus may need a worked derivation and production problems; coding may need
prediction, tracing or repair; humanities may need source comparison and
argument practice. Use at least three genuinely different subjects in the
demonstration content. Preserve a direct study-set workflow alongside courses.

Instructor pacing and exam emphasis come from provided evidence, not guesses.
Progress distinguishes introduced, reported studied, practiced, demonstrated
and due. Reading or a self-pressed known button does not prove mastery.

Keep deterministic grading in one testable authority. Typed facts and numbers
use explicit rules. Long prose, arguments and proofs remain pending or clearly
labeled advisory interpretations until a learner or authorized reviewer settles
them. Preserve response history separately from a correction or later mark.

Keep subject-specific tools, notebooks, diagrams and rich response formats
viable, but deliver each as a complete activity with accessible fallback,
persisted state and useful feedback. Do not turn their future possibility into
placeholder buttons. Later additions extend the working core.

## Storage and ownership

Use the baseline prompt's IndexedDB approach for a browser candidate. Put
large learner objects and images there; localStorage holds only small settings.
Keep a versioned, documented backup format that includes content, media,
preferences where portable, study sessions, schedules and result history.
Validate imports before changing data. Use transactions and refuse destructive
conflicts rather than silently replacing existing work.

Provide a stable application origin and explain that a different origin uses a
different browser store. Handle quota failures without losing an unsaved draft.
Offer persistent-storage status where available, while explaining that browser
data can still be cleared by the user. Test offline reload through a real
service worker/cache path, including an update that preserves learner data.

Prove complete backup restoration in a fresh browser profile, not only reimport
into the profile that already contains the objects. Keep downloadable backups
easy to obtain. A later desktop/file-backed storage adapter is an option if
the browser experience cannot meet the actual ownership or library needs;
do not build two independent sources of truth now.

No telemetry. No background uploading. No copying real learner files into Git.
Do not commit, deploy, install or replace my old app without my authorization.

## Acceptance gates and execution discipline

Implement continuously in these stages. A stage boundary is a verification
checkpoint, not a request for me to authorize the next already-requested stage.
Fix consequential failures before widening scope. Show me a working local app
early, then keep it usable while improving it. A short task list and concise
architecture/limitations record are enough unless a real design uncertainty
requires more. Do not create a large speculative planning programme.

Verify Stage 1 using the baseline prompt's completion checklist, plus:

1. Create a set, edit/reorder cards, study, close/reopen and resume the exact
   unfinished session. Change a card later and handle its old history explicitly.
2. Exercise every requested mode with normal, one-card, two-card, duplicated,
   multilingual and image-bearing sets. Distinguish unsupported speech from
   unfinished deterministic functionality.
3. Trigger wrong answers and manual corrections, finish a test, practice misses,
   return on a later date and explain why review items are due.
4. Export a complete backup and restore into a fresh profile. Check exact images,
   cards, histories and schedules. Test invalid imports, storage failure and
   a real offline reload without corrupting existing data.
5. Use keyboard-only desktop and narrow phone layouts. Show readable feedback,
   clear save/error states and sensible navigation back to the set or course.

For Stages 2 and 3, verify original-source preservation, note/draft save and
edit/reopen, source return, reuse, model failure recovery, source changes and
the joined course loop. Do not claim human accessibility or learning efficacy
from automated checks alone.

If the old app or better clone is available, compare the same tasks using the
same material: time to useful practice, editing ease, quality of feedback,
next-day return and restoration. Record measured results separately from my
preference. Do not claim a speed improvement unless measured.

Deliver setup/run instructions, a working entry point, concise architecture,
actual verification results and named remaining limitations. Report source,
browser-verified, packaged and installed states separately. Keep unfinished
future capability ideas in a small durable list without presenting them as
available features.
