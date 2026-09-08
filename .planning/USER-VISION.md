# User vision — verbatim and additive

**Owner:** Weibao
**Status:** authoritative intent record
**Editing rule:** preserve entries verbatim. Do not silently correct spelling,
grammar, emphasis, or ambiguity. Add new dated entries instead of rewriting old
ones. A dated interpretation note may follow an entry, but it must be visibly
separate from the quotation and point to any binding decision in
`SOURCE-TO-COURSE.md`, `PROJECT.md`, requirements, or phase plans.

This file exists so the program's goal remains available in the user's own
words next to the product team's interpretation. When the two appear to
conflict, reread this file, record the interpretation explicitly, and resolve
the difference rather than treating a prior summary as the user's intent.

## Verbatim goal statements

### 2026-08-24 - feedback that lets you proceed, and building from the standards

> Im not asking for partial credit, its just to rule out wrong answers and also show what I got right so I can keep on going rather than gambling and more other stuff to consider and more,

> Consider building all from the Education standards and whatever, and if the real test is all multiple choice the practice for it is fine to be all multiple choice and more, write relevant stuff into uservision accordingly. Stuff to consider and more?

#### Interpretation recorded 2026-08-24

Separate from the quotation above, and correcting one factual premise inside it
rather than editing his words.

**The first clause is a teaching requirement, not a scoring one.** He is
explicit that he is not asking for partial credit. What he is asking for is that
a not-fully-correct multiple-response attempt tell him what he got right and
what he got wrong, so the retry is reasoning rather than guessing. The word he
used is "gambling", and it names the current behaviour accurately: a wrong
`multi` answer in practice mode returns a generic "Not correct" and the learner
re-picks blind. The authored per-option rationale (`DA:`) that would answer this
already exists in the format and is already carried by `explain_payload`; what
is missing is the disclosure policy deciding when the runtime releases it. This
is therefore an addition to the Phase 6 feedback policy, mode gated, and not a
change to the scorer. See `.planning/research/2026-08-24-item-writing-standards.md`,
final section: no external standard governs per-option feedback, so this is a
free design choice constrained only by our own rule that exam mode stays silent.

**The second clause is right about the source and wrong about the format, and
the correction matters.** Building the course from the National EMS Education
Standards is correct: that document is curriculum and competency, and it is the
right authority for what to teach and in what order. Verified the same day that
it contains zero occurrences of "distractor", "item writing", "test item" or
"multiple choice", so it is NOT an authority on item construction; NBME and
Haladyna are.

**The real examination is not all multiple choice.** NREMT's published EMT test
plan names Multiple Choice, Multiple Response, Options Table, Build List and
Drag-and-Drop. Those map onto itembank's existing `mc`, `multi`, `table`,
`build` and `dnd`. So the premise "if the real test is all multiple choice"
does not hold, and acting on it would narrow fidelity rather than preserve it.
The underlying principle he is stating, that practice should mirror the real
examination's format, is accepted and is stronger than the example: it argues
for keeping all five types and for pinning their structure to NREMT's published
counts.

**Recorded consequence, not yet planned.** NREMT scores dichotomously and gives
no credit for a partially correct response, so itembank's existing all-or-nothing
`multi` scoring is already conformant for EMT and should not be changed to
partial credit. If partial credit is ever wanted for Math or CS, where no such
body binds, it is a per-subject policy and belongs with the subject profile.

**Planning effect, extracted 2026-09-04.** This field was missing, which is why
`scripts/vision_audit.py` reported the entry as having none. Nothing new is
interpreted here; the effect is restated from the paragraphs above so the audit
can see it. **The disclosure policy is an addition to the Phase 6 feedback
policy, mode gated, and not a change to the scorer**, since the per-option
rationale it needs already exists in `DA:` and is already carried by
`explain_payload`. The format half changes nothing and confirms a standing
commitment: keep all five item types and pin their structure to NREMT's
published counts. The partial-credit question is settled as a non-change for
EMT and left open as a per-subject policy elsewhere.

**Relationship to prior entries.** Extends the 2026-08-21 practice-fidelity
material rather than conflicting with it, and supersedes nothing. It corrects
one factual premise inside its own quotation, that the real test is all
multiple choice, without altering the quotation.

### 2026-08-13 — quality benchmark and visual ambition

> what will it take for the lessons and more to be brilliant.com level? WHy cant we scrape site and more?

> Not copying the content, like I wnat their visial design and more

#### Interpretation pointer recorded 2026-08-22

This statement predates the practice of writing a dated interpretation
beside each entry, so it has none. It was not dropped: its interpretation
is the Phase 17A visual system and component foundation, and `research/phase-16/10-visual-experience-system.md` for the presentation theme and token axis. The 2026-08-22 subscription entry later extended this statement from visual design to capability.

This is a pointer, not a new interpretation. Nothing here restates or
narrows what Weibao said, and the quotation above is untouched. Added after
`scripts/vision_audit.py` found that the seven oldest entries were the only
ones with no traceable planning effect.

### 2026-08-13 — source-to-course goal

> THe goal is for like kind of creating a course based on, say a book or a syllabus or something, and then it can extract the actual useful lessons, or the key terms or notes to be read, or if its best to read source text, etc, and be able to quiz and test albert style, and everything could be partially drivable by ai,

#### Interpretation pointer recorded 2026-08-22

This statement predates the practice of writing a dated interpretation
beside each entry, so it has none. It was not dropped: its interpretation
is `SOURCE-TO-COURSE.md`, which is the product contract this statement became and is the north star every later phase cites.

This is a pointer, not a new interpretation. Nothing here restates or
narrows what Weibao said, and the quotation above is untouched. Added after
`scripts/vision_audit.py` found that the seven oldest entries were the only
ones with no traceable planning effect.

### 2026-08-13 — course generator, assessment alignment, UI, and agents

> write down relevant stuff, fix claude and agent.md accordingly, rescoping and writing readme and plans and more to fi this goal, AI should be able to drive and understand collected metrics and more, and can play a reasonable role if need be? Like a curriculum genorator, creating a tangible useful learning experience, like proper questions following relevant guidelines and pointing to leanring objectives and more, in the case of standardized tests, and for what would be tested, in case of knowledge based exams, and other stuff accordingly for the specifi type of course,

> And then, inside, must also be a comprehensive UI for displaying the lessons, with all the cool, and benefitial things, like hoverable definitions, box for things to know and more, niche tips and more?

> and of course, we need relevant agentic skills/instructions so that quality of created course is of a high quality and more?

> And on top of that, supporting an local agent as a goal, but to be drivable via cowork or codex in a situation, something like this?

> more to consider?

#### Interpretation pointer recorded 2026-08-22

This statement predates the practice of writing a dated interpretation
beside each entry, so it has none. It was not dropped: its interpretation
is `SOURCE-TO-COURSE.md` for the loop, `REQUIREMENTS.md` for the obligations it became, and the Phase 16A semantic capability and activity contract for the assessment-alignment half.

This is a pointer, not a new interpretation. Nothing here restates or
narrows what Weibao said, and the quotation above is untouched. Added after
`scripts/vision_audit.py` found that the seven oldest entries were the only
ones with no traceable planning effect.

### 2026-08-13 — correcting the prior direction

> our work for pointing things in the direction might need phases and audtiting too, first the prior 14 phases, and also the ui design and research, and any remnant impacts or wrong direction and more? Explaining the situation, and satisfying and destroying all he grievances? seperating the goal in phases? Centeral goal correction, Learning UI pass, agentic stuff such how how to create fitting lessons and more, so like exposing how lessons are built and then making the agents follow that?

> Readme.md corrections, deleting or at least grouping relevant stuff like the hand offs? auditing them? More?

> Maybe we can spread these work to different chats, fixing accordingly?

> We need to research features and more, and what looks good/is cool

#### Interpretation pointer recorded 2026-08-22

This statement predates the practice of writing a dated interpretation
beside each entry, so it has none. It was not dropped: its interpretation
is the nine-subphase sequence in `ROADMAP.md` section 8, which is the rescoping this statement asked for, and `RULE-AUDIT-2026-08-15.md` for the audit of the prior phases.

This is a pointer, not a new interpretation. Nothing here restates or
narrows what Weibao said, and the quotation above is untouched. Added after
`scripts/vision_audit.py` found that the seven oldest entries were the only
ones with no traceable planning effect.

### 2026-08-13 — broader learning-program research

> might need to absorb how other similar programs, or to research things in sections,from researching similar programs, or the features of learning programs and more to be taken in to consideration

#### Interpretation pointer recorded 2026-08-22

This statement predates the practice of writing a dated interpretation
beside each entry, so it has none. It was not dropped: its interpretation
is `research/phase-16/05-learning-program-landscape.md`, and the feature atlas at `research/phase-16/06-feature-style-atlas.md`.

This is a pointer, not a new interpretation. Nothing here restates or
narrows what Weibao said, and the quotation above is untouched. Added after
`scripts/vision_audit.py` found that the seven oldest entries were the only
ones with no traceable planning effect.

### 2026-08-13 — keep the goal editable

> we should also write somewhere, stuff,  in my words exactly, the goal for the program? Next to it with what is there, I can Add to it as needed and more?

#### Interpretation pointer recorded 2026-08-22

This statement predates the practice of writing a dated interpretation
beside each entry, so it has none. It was not dropped: its interpretation
is this file, which exists because of this statement, plus `USER-VISION-INBOX.md` as the capture funnel and the promotion contract in `PLANNING-DIRECTIVES.md`.

This is a pointer, not a new interpretation. Nothing here restates or
narrows what Weibao said, and the quotation above is untouched. Added after
`scripts/vision_audit.py` found that the seven oldest entries were the only
ones with no traceable planning effect.

### 2026-08-13 — finding prior work, progressive lessons, and agent skills

> adding/working on uservision, it is important for the program to be able to find previously created lessons or questions(this could be done both manually agentically) and be linked, if things are in weird places, like say a seperate folder, and then other parts in an obsidian folder,, also maybe need to eventually work on adding a skill for updating older lessons or questions to be enhanced with new learning ui capabilities, like the hovering and the other stuff,

> also will then make the lesson doc file lessons, look reasonable without the display but look so mucch better and have extra features and more while inside UI display as lessons, like the hovering, the better UI with JS or some other way, diagrams and more? Might need further refinement of ideas too

> So skills so that Agents and Codex or claude code or anything else can understand how to work properly with itembank and at a higher level, so for creating lessons and questions and exams and more?

#### Interpretation pointer recorded 2026-08-22

This statement predates the practice of writing a dated interpretation
beside each entry, so it has none. It was not dropped: its interpretation
is the Phase 14C source adapter registry for finding work that already exists, `research/phase-16/04-portable-contract-agents.md` for the authoring contract, and the Phase 999.5 agent onboarding skill library for the skills half.

This is a pointer, not a new interpretation. Nothing here restates or
narrows what Weibao said, and the quotation above is untouched. Added after
`scripts/vision_audit.py` found that the seven oldest entries were the only
ones with no traceable planning effect.

### 2026-08-13: UI flow, lesson capabilities, question variety, and reusable visioning

> Further ideaboarding, Need a plan to work on how the UI flow should logically work, and how to make it look good too, so that is two phases maybe, we can absorb how notebook lm works, with their features for questions and stuff, but ours should be a better lesson based platform as well? Still need chats to research on possible features(hover definitions, maybe relevant pictures, cool things, tips and tricks box, and more), and on how to make them work, ofcourse will then also need relevant skill/descriptioms so that agents will know how to work with this. This almost feelsl ike workijg on a proprietary file type? Need to also look into
> question possibilities and more for a variety of lessons,

> Seperately, maybe we can make this uservisioning process as a durable thing for other projects if we want them, as a possible skill on github? We will ofcourse need to work on improving the process as well, such as like comments on how the user vision was interpreted below the words as well, what to do when something future changes something past and more, ideaboarding like this should have been more important in the future

#### Interpretation recorded 2026-08-13

**Status:** active direction with open design questions.

**Current interpretation:** rich learning UI work needs two deliberate stages.
The first researches learning flows, competitor patterns, lesson capabilities,
question possibilities, and the authoring contract. The second establishes the
visual system and implements the polished experience against that contract.
NotebookLM is a research input, not the product target; itembank should remain
course-, objective-, lesson-, practice-, and assessment-centered.

The durable lesson representation should be investigated as a semantic content
contract that remains useful outside the app and gains richer behavior inside
it. An opaque proprietary format is not yet justified. Agent skills must explain
how to author, validate, display, and upgrade every supported semantic feature.

**Open questions:** which lesson capabilities create learning value across
subjects; which require interactivity; which question families belong in
instruction versus formal assessment; how images are sourced and cited; which
features need author controls; and when the semantic Markdown contract becomes
too constrained and needs a packaged document form.

**Planning effect:** split the prior comprehensive UI phase into a learning-flow
and capability-contract phase followed by a visual-system and implementation
phase. Plan a reusable user-vision capture skill separately rather than mixing
it into itembank's runtime.

### 2026-08-13: lesson feature breadth, note modes, styles, and missing-feature tests

> what abiut feature research? for stuff like  hover defiitions, highlighting certain stuff, notebook style? Extracting/creating specific style notes? Full learning vs notes creation? Testing features that are missing? MOre features and other stuff? stuff that  stuff like brilliant and other research programs have? niche programs? stuff on githubb? stuff in lessons,  from style choices like books, say like the for dummies style and similar and more?

#### Interpretation recorded 2026-08-13

**Status:** active expansion of the Phase 16 research program.

**Current interpretation:** product-landscape and pedagogy research are not
enough. Phase 16 also needs a deliberately broad feature atlas before features
are filtered into the lesson-capability contract. The atlas should include
small reading and note interactions, authoring and extraction modes, distinct
lesson and note outputs, instructional style systems, open-source examples,
niche products, and tests that expose missing capabilities.

**Open questions:** which features belong to reading, learning, note creation,
authoring, review, or assessment; which styles are semantic transformations
versus cosmetic themes; which book-derived conventions transfer to interactive
lessons; how style affects accuracy and cognitive load; and which capabilities
should remain optional or user-selectable.

**Planning effect:** add a separate Phase 16 feature-atlas research stream and
require synthesis to distinguish the complete inventory from the smaller set
recommended for implementation.

### 2026-08-13: files, hierarchy, onboarding, packaging, and future audit

> my words will have to go into user vision later, but also, stuff like the executable notebooks, editing files where they are at now, finding previous files, creating relevant folders, user friendly instructiojs like for readme and in app, user considerations, like the walkthrough for first time and more, the finial packaged app, and other stuff I could have mised, goal of being applicable to something super complex, like being able to create and relevant course/lesson, it can have subcourses/semester/conecpts that builds up a field or course? Like say for something like math, sub category for kind of math, then further and further more, maybe can show completion, and like a progress on "completing" the entire frield, but that could be implemented but what counts as an entire field and more will need more ideaboarding.

> Will also need furuther future audit on how and when to get everything done and more?

#### Interpretation recorded 2026-08-13

**Status:** active direction with unresolved hierarchy and completion semantics.

**Current interpretation:** the product must work with existing and executable
materials, support complex nested or graph-shaped curricula, explain itself to
first-time users, and eventually arrive as a coherent packaged app. Progress
must be honest about who defined the scope and whether an open field can ever be
complete.

**Planning effect:** research file interoperability, curriculum hierarchy,
progress semantics, onboarding, packaging, and a later implementation-readiness
audit before committing to one universal structure.

#### Interpretation update recorded 2026-08-17

**Status:** the "what counts as an entire field" question is resolved; the
2026-08-13 interpretation above is partly superseded on that point only.

**Current interpretation:** the ideaboard Weibao asked for ran on 2026-08-17
(`.planning/IDEABOARD-FIELD-2026-08-17.md`, ledger entry IL-20260817-01). A
field is an authored, versioned scope object over the one typed graph, with
unlimited nesting through recursive scopes, free level labels, and a declared
boundedness: a bounded scope pins its membership and may truthfully report
complete under its named predicate, while an open field never reports
complete and states its scope version on every progress claim. Progress rolls
up through two registered display models (dimension-wise rollup and one-level
map view), never through a single percentage, per GRAPH-03.

**Relationship to prior entries:** resolves the open hierarchy and completion
question of the 2026-08-13 entry above; everything else in that entry keeps
its 2026-08-13 interpretation.

**Planning effect:** Phase 17B's tracer renders a minimal scope tree in both
rollup models (under gate G5, evidence honesty, in its details block); 14B
adds the scope object's boundedness and membership classes to its
course-package checklist.

### 2026-08-13: complete app flow, visual experience, files in place, and edge cases

> Also need to ideaboard/research comprehensively Comprehensive but also visually appealing app experience, what to show, how things folow, how things chain and more,  Splitting research into finer parts as needed? Working with files as they are and not moving them? More edge cases abd nire>

> How should we decide what to put into uservision, and what not to put? or just put everything?

#### Interpretation recorded 2026-08-13

**Status:** active product direction and resolved vision-capture rule.

**Current interpretation:** logical application flow and visual design require
separate deep research. Existing files should remain in place by default. The
vision process should capture every meaningful thought but promote only durable
product intent into this file.

**Planning effect:** split file lifecycle, curriculum hierarchy, app flow, and
visual experience into distinct research streams. Use `USER-VISION-INBOX.md`
as the capture funnel and `PLANNING-DIRECTIVES.md` as the promotion contract.

### 2026-08-13: guided highlighting, learner-built notes, and configurable learning paths

> also for features like highlighting and stuff, I meant the lesson prehighlighting stuff,(telling you to/forcing you to highlight too, or type out again<- which could potentially build into a note doc that the user typed out, all while going through the lesson!), so need to research and consider, creating notes, then quizzes, and/or creating comprehensive lessons, and then notes? Alof of things can simply be implemented at the same time and then letting the user decide stuff? Need more research for this in sperate chats, also write my visions and ideas into the user vision

> Might we need to improve uservision doc to see what its building into and more? other stuff tp cpmsoder?

#### Interpretation recorded 2026-08-13

**Status:** active learning-experience direction requiring dedicated research.

**Current interpretation:** highlighting includes both author-provided emphasis
and learner action. A lesson may ask the learner to identify, highlight, copy,
restate, organize, or explain material while reading. Those actions may build a
learner-owned note document that later supports review, practice, and quiz
creation. The system should investigate several valid sequences rather than
assuming every source becomes a full lesson or every learner must take notes in
the same way.

**Open questions:** when active note construction improves learning; when
copying becomes low-value transcription; whether a prompt may require a note or
only recommend one; how notes preserve source links; what remains private and
learner-authored; whether generated questions may derive from learner notes;
how correctness is handled when notes contain errors; and which choices belong
to the learner, course author, objective, or activity design.

**Planning effect:** add a separate active annotation and learner-note research
stream. Require it to compare source to notes to quiz, source to lesson to
notes, notes-first, lesson-first, and hybrid modes. Treat configurability as a
designed strategy interface, not a reason to ship every combination without
evidence.

### 2026-08-13: expected features, omissions, and one coherent product

> research: need to also consider features that logically and reasonably should have, but we might not have considered?

> add to vision as well,

> all the rules and ideas should hopefully coaless into something proepr

#### Interpretation recorded 2026-08-13

**Status:** active quality and synthesis requirement.

**Current interpretation:** research must not depend only on remembered ideas,
named competitors, or visible novelty. It must derive expected capabilities
from the product's jobs, users, lifecycle, risks, and quality promises, then
identify omissions. The final result must be one understandable product model,
not a catalog of loosely connected features, rules, modes, and agent skills.

**Open questions:** which capabilities are baseline expectations; which are
valuable differentiators; which are optional extensions; which rules can be
unified; which conflicts need a user choice; and which ideas should be rejected
because they make the whole product less coherent.

**Planning effect:** add an expected-capability and omission audit to the
research program. Require synthesis to produce a product model, a small set of
core loops and primitives, a disposition for every proposal, and a trace from
vision through requirements and verification.

### 2026-08-13: preserve viable ideas through core, options, prototypes, or backburner

> rather than reduce ideas we can put in backburner or implement if possible

#### Interpretation recorded 2026-08-13

**Status:** active planning and synthesis rule.

**Current interpretation:** making one coherent product does not mean deleting
useful breadth. Viable ideas should become core capabilities, composable options
or registered strategies, bounded prototypes, or backburner items with explicit
revisit triggers. Several ideas may ship together when shared primitives make
that reasonable.

**Boundary:** architecture may preserve broad possibility while execution stays
sequenced and verifiable. Rejection is reserved for conflicts with assessment
authority, accessibility, rights, safety, truthful evidence, portability, or
the coherent product model, and the rejected idea remains recorded with its
reason.

**Planning effect:** synthesis must use a durable disposition ledger and may not
invoke simplicity alone as a reason to erase a capability.

Rejected ideas remain written down with the originating idea, evidence,
reasoning, conflict, retained alternatives, date, and condition for
reconsideration. They are not silently deleted.

### 2026-08-21: the first real sitting, and what it cost to find out

The first entry in this file written while Weibao was actually using the
product. Phase 13.9 had been open five days; the sitting was started on
2026-08-16 and abandoned at question zero. Everything below came out of about
ten minutes of clicking.

> for item bank, quizzing options eems pretty good, but should lesson be gated behind the quiz? it seems to be inverted, but I guess this is the quiz part, but there seems to be njo way to go back to home page and more?

> Also writing summary and more seems to be token drain and more? costing me erxtra $$$

> thughts and suggestions? Whats being served seem only tto be the quiz section rather than the full LMS app style? weith the lessons and more? other stuff and more?

> do both, link the lesson and cut the summary rule, consider if the gsd rule us costing us too,  also need to consider, wasting time on duplicate tests if wasting time and also, Ui improvements and more?

#### Interpretation recorded 2026-08-21

**Status:** active. Three parts resolved the same day, two open.

**Current interpretation:** four separate observations, and the first one was a
real defect nobody had noticed in twelve completed phases.

**The reading had no entrance.** The gate direction was correct: the lesson
gates the quiz. What was wrong is that `/lesson/<stem>` existed, returned 200,
rendered the whole lesson, and linked into every item, and **nothing anywhere
linked to it.** The daemon index offered three links: sit, study, report.
Fixed the same day, reading first, guarded by a test that fails if the link
disappears. A route with no entrance is a route nobody has, and no framework
test could see it because every framework test knew the URL already.

**The quiz-only impression was correct but was the wrong surface.**
`itembank serve` is the single graded sitting and has no home by design.
`itembank daemon` is the app. That distinction is real and defensible, and it
is invisible to anyone who was handed a `serve` command. Whether `serve` should
exist as a separate front door at all is now an open question rather than a
settled design.

**The summaries were a real cost, not a feeling.** Measured: 129 `-SUMMARY.md`
files holding 23,261 lines, more than half the size of the entire runtime, most
of them restating commit messages. Cut the same day: a summary is now written
only when a plan was left incomplete or a measured fact contradicts the plan.
Recorded in `EXEC-CONTEXT.md` and `PLANNING-DIRECTIVES.md` section "Budget
discipline".

**GSD:** the plan format earns its cost, the ceremony around it does not. The
artifacts that multiply are summaries, verification records, and roadmap rows,
not plans. `CLAUDE.md` already permits skipping the framework for small work;
the new budget rules make that the default rather than the exception. No
further change recommended today.

**Duplicate tests:** largely a false alarm, with one real cost. 19 suites call
`score_response`, and that is the one-scorer invariant being enforced per
surface, which is the point rather than duplication. The real cost is
wall-clock: 32 of 71 suites spawn a server subprocess and 47 shell out to
`itembank.py`, so the daemon suite alone takes 62 seconds. The fix is a shared
fixture server, not fewer tests. Not scheduled.

**Open questions:**

1. Should `serve` remain a separate front door, or become a mode of the app.
2. What the app's home page should be once it is more than a file list. It
   currently lists bank stems, which is a directory listing wearing a product's
   clothes.
3. Which UI improvements come from use rather than from design sessions. This
   entry produced one defect in ten minutes; the question is what a full unit
   produces.

**Planning effect:** the daemon index change shipped. The summary rule and five
other budget rules are recorded in `PLANNING-DIRECTIVES.md`. B3 in particular,
do not plan a phase whose inputs do not exist, comes directly from this
sitting: the UI flow session was written before it and would have designed the
wrong-answer flow without anyone having answered one.

**Relationship to prior entries:** confirms the 2026-08-13 UI entry, which
asked for a comprehensive lesson UI, by showing the lesson was not reachable at
all. Supersedes nothing. It is the first entry here backed by use rather than
by intention, and that is the part worth keeping.

## Additions

Add future statements below as new dated sections. They may be short, rough,
contradictory, exploratory, or questions. Do not require them to be rewritten
as requirements before recording them.

### YYYY-MM-DD — title

> Add the user's exact words here.

### 2026-08-20: the product does not match expectations

> the thing is the current product doesnt match expectations at all ngl

> also Im not going to lie the design is still not the best it could be even after all the inspiration? like where is the logical pulti page flow and more?

#### Interpretation recorded 2026-08-20

**Status:** active, and acted on the same day.

**Current interpretation:** the gap named here is specifically the experience
layer, not the runtime. Phases 1 through 13 shipped a working assessment
runtime with 65 test suites, and the lesson surface rendered semantic Markdown
as a plain HTML document: prose, a list, a table, a link list. That is a long
way from the 2026-08-13 "brilliant.com level" entry. The second quotation adds
that a single scrolling page of states is not a product flow, which was correct:
the 17A tracer stacked seven states on one page because a tracer proves a seam
and says nothing about navigation.

**Open questions:** whether the remaining gap is closed by design work inside
the current Python string templating, or whether it needs a component library
and a TypeScript frontend over the same daemon routes.

**Planning effect:** 17A was pulled forward ahead of 14B, 15A, 15B, 16A, 16B
and 16C, none of which its plan graph depends on. `17A-01` became eight
navigable screens rather than one scrolling catalog.

**Relationship to prior entries:** confirms and sharpens the 2026-08-13
"quality benchmark and visual ambition" entry by naming the shipped surface as
the thing that falls short.

---

### 2026-08-20: hover definitions for terms whose everyday meaning misleads

> also need a dictionary extention or something or explantion on hover for potentially confusing terms like inspiration, since that doesnt mean what I think it does

#### Interpretation recorded 2026-08-20

**Status:** resolved for the prototype; the capability already existed.

**Current interpretation:** this is a learner observation, not a feature
request in the abstract. "Inspiration" in a respiratory context means breathing
in. The capability shipped in Phase 3.1 (`## TERMS`, `[[term]]`, a Popover API
trigger, a panel, a glossary appendix, a print fallback) and was simply not
wired into the 17A tracer. The lesson generalizes: the terms that need a
definition are the ones whose ordinary meaning actively misleads, not the ones
that merely look technical.

**Open questions:** who selects the terms. An author, a model proposing
candidates for review, or the learner marking words that tripped them.

**Planning effect:** `17A-01` reuses `lesson.py`'s glossary rather than
building a second one, and `lesson.gloss_css()` was added so the tracer and the
reader style definitions from the same bytes. Five terms are defined in the
fixture, each chosen because its everyday sense misleads.

**Relationship to prior entries:** confirms the 2026-08-13 "hoverable
definitions" clause and supplies the selection criterion that entry lacked.

---

### 2026-08-20: home, app flow, sectioning, and a tab for the harness

> what about the home UI? app based flow? tabs for things? side bar? other stuff to ocnsider and more?

> consider how the app use workflow should  even look? Homepage? sectioning? other stuff and much more?a tab for just the deepseek harness kinda thing, and then other tabs for other stuff and more? with deepseek harness we can spend less work implementing Open agents and other stuff and more?

> right now both of these looks pretty broken and java script or whatver is blocked and clicking between dosnt do anything, and also things are section ed properly accordingly to vision and more? more to consider?

#### Interpretation recorded 2026-08-20

**Status:** partly resolved. The information architecture existed; its shape did
not.

**Current interpretation:** two separate things were being asked. `16B-UI-SPEC`
already settles which areas exist and what their routes are, including a
deliberate decision that Search is reserved but unbuilt and that Notes has no
route of its own. What no document settled was whether that navigation is a
sidebar, a tab row, or a bottom bar: searching `16B-UI-SPEC`, `17A-UI-SPEC` and
`UI-SPEC` for those terms returns zero hits. The areas were designed and the
navigation was never drawn.

The harness clause is a distinct and stronger claim: that hosting an existing
agent harness costs less than implementing agent features one at a time. It is
correct, and by more than expected, because the machinery already shipped
(`model_backend` in Phase 8, `auditor_autonomy` in Phase 11, ten skills, and
`journal.commit_operation` in Phase 14A). Nothing rendered it.

**Open questions:** whether Study, Build and Operate are the right three
sections or an artifact of the current feature set. Where the course switch
lives when the navigation is a thumb bar with no room for it.

**Planning effect:** navigation shape became a second switchable axis rather
than a decision, alongside the visual direction. An Agent screen was added
under Operate. `17A-06` was written for the harness.

**Relationship to prior entries:** extends the 2026-08-13 "complete app flow"
and "one coherent product" entries with the concrete observation that the
sections were rendering incompletely.

---

### 2026-08-20: keep every option, choose a default, and use what exists

> all of them?

> we caan keeep all of the options as something for the user to choose from, but the agent page, we use skills with  claude and codex, but for local ai, we need a homepage/harness there, and we can just take Deep seek harness and slap it there,

> structured studio, sidebar, indigo, consider higher starred stuff as well

> also everything has an interessting green theme right now, will we have swappoing options in the future?

> We can also just used an precreated recreation of learning software that is already out there for now

#### Interpretation recorded 2026-08-20

**Status:** active. The default is chosen; the options remain.

**Current interpretation:** four claims. First, a default is a starting point
and never a deletion, which restates `PLANNING-DIRECTIVES.md` section 1 as a UI
rule. Second, Claude and Codex are already harnessed by Claude Code and the
Codex CLI, so only the local model lacks a console; that split is the reason
`17A-06` builds one page rather than three. Third, the accent was never
hard-coded: `itembank theme preview/set/reset/pick` shipped in Phase 4 and
`derive_theme` raises a colour that fails contrast rather than accepting it.
Fourth, reusing existing software is worth splitting in two, because adopting an
LMS shell and adopting a component library are different trades.

**Open questions:** whether "higher starred stuff" should become a bounded
research pass over high-star learning and agent projects, and what specifically
would be taken from each.

**Planning effect:** `17A-DIRECTION.md` records structured-studio, sidebar and
indigo as defaults with every alternative retained as one deletable stylesheet.
Four accent swatches were added to the prototype. `theme.DEFAULT_ACCENT` is
deliberately unchanged, since moving the shipped default belongs to `17A-04`
with its accessibility pass.

**Relationship to prior entries:** confirms the 2026-08-13 "preserve viable
ideas" entry and applies it to implementation choices, not only to ideas.

---

### 2026-08-20: build off the original vision, course selector, cohesion

> build off the original vision too, course selector, opther stuf fand more, cohesion pass and more?

#### Interpretation recorded 2026-08-20

**Status:** partly resolved.

**Current interpretation:** a shell that names one course and offers no way off
it cannot express the stated goal of one learner across EMT, Math 1400 and CSCI
1100 at once. The course selector is shell furniture, not a control buried on
Home. "Cohesion pass" is read as an instruction to audit the whole surface
rather than fix the reported symptom, which found the same class of layout fault
in six of nine look-by-navigation combinations.

**Open questions:** whether courses are peers in one list or whether a term or
semester groups them.

**Planning effect:** a course selector with three courses, each stating where
the learner stopped, visible in sidebar and tabs and hidden in the thumb bar.

**Relationship to prior entries:** confirms the 2026-08-13 "files, hierarchy,
onboarding" entry at the shell level.

---

### 2026-08-20: get more per token

> how can we theoretically get all these done and implemented? NEed any planning? how to get more per token rather than spending 5 billion like last time and not getting much out of it?

#### Interpretation recorded 2026-08-21

**Status:** active. This is a process constraint, recorded here because it
shapes what gets built and how.

**Current interpretation:** the 5.1 billion tokens were not wasted on nothing.
That spend bought 76,465 lines of Python across 139 feature, 95 test and 32 fix
commits between 2026-08-08 and 2026-08-20, and twelve phases closed. The
dashboard shows 99.24 percent of it was cache-hit input, 0.32 percent output,
and 25,154 requests for 25.33 US dollars. The reason it reads as nothing is that
no phase output ever reached the learner: twelve phases closed without the
product being used on real material once.

Four measured rules follow. Context size times turn count is the bill, so the
standing prompt was cut from about 122,000 tokens to 775. Model tier matters
enormously: on 2026-08-11 one key spent 11.34 dollars and another spent 0.14 on
the same day's work, because a reasoning model emits thousands of discarded
tokens per turn. A test is cheaper than an explanation, because a guard costs
tokens once and a re-explanation costs them every time. And a turn should end in
something openable, because every correction in this session came from Weibao
opening a rendered file and looking at it.

**Open questions:** whether the roadmap's remaining phases should be re-ordered
so that each one ends in something the learner can open, rather than in a freeze
gate that can go green without anyone using the product.

**Planning effect:** `.planning/EXEC-CONTEXT.md` created as the entire standing
prompt for an execution run. `ROADMAP.md` halved, with completed phase details
moved to `ROADMAP-ARCHIVE.md`.

**Relationship to prior entries:** does not conflict with any product entry. It
constrains how they are delivered.

---

### 2026-08-21: embed the harness, and customize it

> I feel like we can embed, with how clean their interface is, we can use that to help with the main coherence and more too

> we can sustomize dsh as needed and more?

#### Interpretation recorded 2026-08-21

**Status:** active. Recorded because it corrected a planning decision.

**Current interpretation:** the claim is that a clean external interface can
serve coherence rather than fragment it, so embedding beats rebuilding. It was
tested rather than argued: `dsh` was installed and run, sets no
`X-Frame-Options`, no CSP and no `frame-ancestors`, frames cleanly with no
console error, and was already driving `qwen3.8-27b:latest`. The earlier
planning record had rejected embedding on coherence grounds and stated that as a
blocker. It is an ordinary integration cost, repaid by not maintaining a
console, and the rejection was revised.

The customization question is answered by the project's own architecture
documentation: everything is a plugin, including the model adapter, the tool
registry, the session log and the agent loop. Three tiers exist. A
`cordis.patch.yml` row replacement with no code, a plugin package, or a fork
under MIT.

**Open questions:** whether `dsh` exposes theming through plugin config, since
the chosen indigo accent cannot reach inside a cross-origin frame. Whether
itembank's ten skills should become a `dsh` skill provider, which would make the
embed genuinely coherent rather than merely adjacent. Neither investigated.

**Planning effect:** `17A-06-DECISIONS.md` revised from subprocess-only to
embed-plus-subprocess. Two items became work rather than objection: the served
document is `lang="zh-CN"` and a learner-facing embed must set locale
explicitly, and the theme seam is unresolved.

**Relationship to prior entries:** extends the 2026-08-20 harness clause above,
and supersedes the reasoning in the first version of `17A-06-DECISIONS.md`
without deleting it.

---

### 2026-08-21: a proper agentic based LMS, and a UI flow plan to get there

> push it, make reasonable plan and more, and make prompt to plan the UI flow and more to make everything truly a proper agentic based LMS?

> update uservision accordingly and relevantly

#### Interpretation recorded 2026-08-21

**Status:** active. New scope language, not yet a requirement.

**Current interpretation:** two words in this entry are new to the record and
neither is decoration.

**"Agentic based."** Earlier entries said the course "could be partially
drivable by ai" (2026-08-13) and that AI "can play a reasonable role if need
be" (2026-08-13). Those describe an assistant beside the product. This entry
asks for something stronger: the agent is an operator of the system. It should
be able to take a goal, read the course state, choose and run a skill, produce
a cited artifact, and have that artifact become real through the normal
acceptance path, without a human retyping the work into a different tool.

The measured gap on the day this was written: the Agent tab embeds a working
agent console (plan 17A-06), and `journal.commit_operation` is a working
compare-and-swap writer with an undo, and **nothing joins them.** The skill
buttons on that page run nothing. An embedded chat window beside a course is
not an agentic LMS, it is two programs in one window.

**"LMS."** The first use of the term in this record. Read as the capability
set, not the administration model: a course a learner is enrolled in and moves
through, assignments and due work, a gradebook-shaped honest record of
evidence, and a next action that is chosen rather than browsed for. It is NOT
read as multi-tenancy, accounts, roles, or institutional administration, which
`CLAUDE.md` still rules out for one learner per installation. Phase 18 already
covers a second person installing their own copy, which is a different thing
from a second person in this copy.

**The boundary does not move, and this entry does not ask it to.** The runtime
invariant stands: one parser, one scorer, one evidence store, and the runtime
settles scoring, session state, keyed disclosure, and evidence. "Truly
agentic" means the agent can operate everything the learner can operate and
propose everything an author can propose. It does not mean the agent can
settle a mark or release a key. An agent that could do either would be the
second authority the architecture exists to prevent.

**Open questions:**

1. What is the agent's unit of work? A skill invocation, a goal that decomposes
   into several, or a standing role that watches evidence and proposes without
   being asked.
2. Where does an agent operation appear in the UI? Inside the Agent area only,
   or as a proposal that surfaces in the area it affects (a lesson revision on
   the lesson, a bank extension on the bank).
3. What does the learner see while an operation runs, and what happens to a
   half-finished operation when the app closes.
4. Does an agent get its own view of the course state, or does it read the same
   routes the learner does. The second is cheaper to keep honest.
5. Which of the LMS-shaped objects (assignment, due date, enrollment-style
   progress, gradebook view) are real durable objects and which are derived
   views over evidence that already exists.
6. Whether the embedded external console and an itembank-driven operation seam
   stay two paths permanently, or converge once the second one works.

**Planning effect:**

- `17A-07-PLAN.md` (registered 2026-08-21) builds the missing seam: one skill
  run from the Agent area through `model_adapter.invoke`, a bounded diff, and
  exactly one `journal.commit_operation` write with a visible undo. It is the
  smallest change that makes the claim true rather than aspirational.
- `PROMPT-ui-flow-agentic-lms-2026-08-21.md` carries the UI-flow planning ask
  into its own session, because flow design and seam implementation are
  different work and mixing them produces neither.
- The open questions above are the agenda for that session. They are not
  requirements yet and must not be cited as if they were.

**Relationship to prior entries:** extends the 2026-08-13 course-generator and
agent-skills entries, and the 2026-08-13 UI-flow entry ("Need a plan to work on
how the UI flow should logically work"), which asked for the same flow planning
and has not yet been done. It narrows nothing and supersedes nothing. It
conflicts with no recorded decision, including the runtime invariant, because
it asks for reach and not for authority.

### 2026-08-20: paper notes as a source, and digitization as an enhancement path

> functionality for notes stuff? consider OCR exiting paper notes, beautifying and highlighting and expanding on stuff and more? does stuff like that exist for digitizing ntoes and stueff? anything for Ai based highlighting and annotating and more? ALso aesthetics too? like papery style vs docs vs other stuff and more? other stuff to consider?

> yes write the inbox entry and reopen B9 and B10, as something to enhance other things, like expanding or adding depth, coreecting and checking understandning and more?

#### Interpretation recorded 2026-08-21

**Status:** active. New source class, not yet a requirement.

**Current interpretation:** the learner's existing paper notes are a source the
course can act on, and the second statement is the one that carries the scope.
Digitization is not the goal. The goal is what becomes possible once a written
page is readable by the system: expanding a thin note, adding depth from a
bound source, correcting an error in the learner's own wording, and checking
whether the learner understands what they wrote. OCR is the enabling step, not
the feature.

This is the first entry to treat something the learner already produced, on
paper, away from the machine, as course input. Every earlier source statement
(2026-08-13 on books and syllabi, and the source-to-course milestone) assumed
the source arrived as a file. A photographed page is a different kind of object:
its identity is an image, its text is a guess, and its author is the learner.

**The aesthetics half of the first statement is not new scope.** "Papery style
vs docs vs other stuff" resolves to three axes the record already separates and
must keep separate: presentation theme and tokens (Phase 17A and Stream 10),
instructional style (the style registry, RESEARCH-BRIEF-2 R1), and note format
such as Cornell, outline, or matrix (Stream 12 section 10.2). Collapsing them
into one style control is the failure mode already named in that stream.
Similarly, AI highlighting and annotating is not new: Stream 12 settled it,
including the finding that instructor-provided emphasis has better evidence
than learner highlighting, which is why AI emphasis is a reviewable proposal
rather than something applied to the learner's page.

**What the boundary already answers.** A learner note never becomes keyed truth
(Stream 12 section 7.2), so a transcribed page cannot become an answer key by
passing through a model. Transcribe, clean, and expand are three different
truth claims and stay visibly distinct in the artifact, because collapsing them
is how a model's guess becomes the learner's note and then a question. The scan
image is the record and the transcription is derived, so a better model later
re-transcribes without touching what was photographed. Rights differ between
the learner's own handwriting and a photographed copyrighted page. The CSCI
1100 AI-use ban applies to OCR-plus-expansion on that course's notes exactly as
it applies to hosted tutoring.

**Open questions:**

1. Whether a digitized note keeps its page identity, image beside transcript
   with the learner's own marks preserved, or becomes clean typeset text by
   default.
2. How transcription confidence is surfaced so an uncertain reading gets
   corrected rather than trusted.
3. Whether checking understanding against a learner's own note is a lesson
   activity, a practice form, or a diagnostic that must never be scored.
4. How a second scan of the same page is reconciled rather than duplicated.
5. Whether the real deliverable is transcription at all, or "rebuild my notes
   for objective X from every scan."

**Planning effect:** recorded verbatim in `USER-VISION-INBOX.md` on 2026-08-20
with disposition Split, and promoted here on 2026-08-21. The implementation
half is registered in `IDEA-LEDGER.md`: IL-20260820-01 reopens B9 (image and
paper-note intake), whose original deferral reason was sequencing behind the
Phase 3.2 generation path that now exists; IL-20260820-02 reopens B10 narrowly,
registering recognition of handwriting already on paper while live stylus
authoring and ink canvases stay descoped. The descope table in
`ROADMAP-ARCHIVE.md` carries dated pointers to both. No phase is scheduled.

**Relationship to prior entries:** extends the 2026-08-13 course-generator
entry, which named books and syllabi as sources, by adding a source the learner
wrote. Extends the 2026-08-13 guided-highlighting and learner-note entry, which
asked about notes the learner builds while going through a lesson, with the
inverse case: notes that already exist and arrive from outside. Supersedes
nothing, and narrows nothing except B10, which is narrowed deliberately and
recorded as such.

---

### 2026-08-22: recreating the paid learning subscriptions, including notes to quiz

> also stuff like recreating a certain subscription service?

> All of these, but also some sort of subscription based notes to quiz and similar, like gizmo unlimited or something, save to uservision

#### Interpretation recorded 2026-08-22

**Status:** active, and it introduces a scope claim the record has not carried
before.

**Current interpretation:** the target is not one competitor. Asked which
service he meant, from a list of the four already named somewhere in this
record, Weibao answered "all of these" and added a fifth class. The claim is
that itembank should do for him what a set of paid learning subscriptions does,
so that the subscription is not needed. That is substitution, and it is
different from every role those products already hold here.

What each product already holds, and what changes:

- **Brilliant.com** was recorded 2026-08-13 as the visual and quality benchmark
  ("I want their visual design"). It becomes a capability target as well, not
  only a look.
- **Albert.io** is the item-writing discipline the linter enforces and the
  "albert style" quizzing named in the source-to-course goal. Unchanged in
  substance, now also named as a paid product being displaced.
- **NotebookLM** was recorded 2026-08-13 as a research input, with the
  interpretation "NotebookLM is a research input, not the product target."
  This entry puts pressure on that line and does not by itself settle it.
- **Notes and reader products** (Goodnotes, Notability, RemNote and their
  competitors) were landscape research in the 2026-08-21 paper-notes entry and
  in stream 16. They gain a product-intent role.

**The fifth class is the new one.** Consumer notes-to-quiz apps, named by
example as Gizmo, take a learner's own material (typed notes, PDFs, slides,
photographed handwriting, an existing Quizlet or Anki deck) and return
gamified quizzing on a spaced-repetition schedule, with the useful volume
behind a subscription. This is the closest existing product to the paper-notes
source class promoted on 2026-08-21, and it is the first named example of what
that class is supposed to feel like once it works.

**Two recorded boundaries this claim runs into, and neither is resolved here.**
First, "Not a spaced-repetition engine. Anki owns retention." A notes-to-quiz
subscription is a scheduler with a quiz surface attached, so either the
boundary holds and itembank keeps exporting to Anki for retention, or the
boundary is revisited deliberately. Second, the notes-to-question authority
table (`research/phase-16/12-active-annotation-notes.md` section 7) already
forbids a learner note from supplying keyed truth, and explicitly rejects
turning every highlight into a cloze. Consumer apps in this class do exactly
that. Matching their convenience without adopting their epistemics is the real
design problem, not the OCR.

**A third distinction to keep visible:** recreating the experience is not
recreating the business. Hosted accounts, multi-tenancy and metered tiers
conflict with the no-accounts, evidence-on-disk, one-learner-per-installation
rules. Nothing in this entry asks for those.

**Open questions:**

1. Whether "all of these" means one product spanning four experiences, or a
   stated ambition level to measure any single capability against.
2. RESOLVED 2026-08-22, see the interpretation update below. Whether the
   retention boundary moves, and if it does, what happens to the Anki export
   path that currently owns scheduling.
3. ANSWERED 2026-08-22, see the interpretation update below. Which parts of
   the notes-to-quiz loop are worth having without the parts that make an
   attention mark into an answer key.
4. Whether displacing a paid subscription is a success criterion the product
   is measured on, or a motivation that stays out of the requirements.
5. Whether the gamification these products rely on belongs here at all, given
   the evidence-honesty rules already governing progress claims.

**Planning effect:** none scheduled. Recorded here on the user's instruction
("save to uservision") rather than routed through the inbox first, because he
named it as vision. The retention-boundary question and the notes-to-quiz
authority question are the two that must be answered before any phase cites
this entry.

**Relationship to prior entries:** extends the 2026-08-13 quality-benchmark
entry from visual design to capability, extends the 2026-08-21 paper-notes
entry with a named example of the finished experience, and conflicts with the
2026-08-13 interpretation that NotebookLM is not the product target. The
conflict stays visible and unresolved, per the interpretation protocol below.

#### Interpretation update recorded 2026-08-22

**Status:** resolves open question 2 of the entry above. Everything else in
that entry keeps its 2026-08-22 interpretation.

User statement, verbatim:

> keep anki for retention, but like we can also have the features of gizmo unlimited and more

**Current interpretation:** the retention boundary does not move. "Not a
spaced-repetition engine, Anki owns retention" survives this entry unchanged,
and the Anki export path keeps owning scheduling. What itembank takes from the
notes-to-quiz class is everything upstream and downstream of the scheduler:
intake of the learner's own material including photographed pages, generation
of cards and items from it, the quiz and feedback surface, and the evidence
record. The subscription is displaced by covering the whole loop except the
one part Anki already does well.

**The consequence that must be designed for, not discovered later.** In the
products being displaced, the quiz surface and the scheduler are one thing.
Splitting them means two systems can both hold a review history, and if both
claim to measure retention they will disagree. The split only stays coherent
if itembank practice is explicitly not a retention signal: sittings and
practice are diagnosis and evidence against objectives, Anki reviews are
retention, and neither reschedules the other. This is the same division
already shipped between this tool and `ankictl`, so the pattern exists rather
than needing invention.

**What this does not settle.** "And more" is open by construction. Gamification
in particular stays unresolved, because these products lean on streaks and
scores while the evidence-honesty rules here already constrain what a progress
claim may assert. Open questions 1, 3, 4 and 5 of the entry above remain open.

**Planning effect:** none scheduled, but the boundary is now firm enough to
plan against. Any future notes-to-quiz work inherits two fixed constraints: the
scheduler is Anki and is reached through export, and the stream 12 section 7
authority table governs what a learner note may become. A generated card
leaving for Anki is subject to the same rule as any other item, so a note
cannot acquire a key by being exported.

### 2026-08-22: paper item formats as a fit check, and the answer to question 3

Weibao supplied photographs of four worked paper assessments as examples of
question shapes to consider. No item text from them is reproduced here or
anywhere in this repository: they are third-party published handouts, and the
never-a-content-store rule applies to them exactly as it applies to a course
bank. Only the shapes are recorded.

**Three of the four shapes are already shipped.** A shared code list applied to
a long stem list is `[TYPE: table]` and its shuffled sibling `[TYPE: dnd]`:
categories declared once, many rows classified against them. Ordinary four
option multiple choice is the default type. Neither is a gap.

**What the sample does raise, in order of value:**

1. **A deliberately unscored item, and the record has no such type.** One
   handout asks the learner to judge each case before instruction, in its own
   words go with the initial instinct for now, and the value of the answer is
   entirely in the later contrast with the taught answer. Every shipped type
   scores dichotomously except `short`, which is pending-review rather than
   unscored. A commitment item that must never be scored is a real gap, and it
   is the same object as the diagnostic named in question 3 of the
   subscription entry above. One type answers both.

2. **Elimination marks are response data and nothing captures them.** The
   photographed quizzes carry crosses through rejected options and circles
   around finalists. That is the reasoning, and it separates an answer reached
   by elimination from a lucky guess. The runtime records the chosen option and
   nothing else, so the distinction is lost at the moment it is made. Capturing
   it changes what remediation can say without changing what scoring may claim.

3. **A shared-taxonomy block at real scale is untested.** The handout runs
   nineteen stems against seven categories, and its whole pedagogic point is
   discriminating between near neighbours across many instances. `table`
   supports that structurally. Whether the linter's answer-position balance and
   item-mix checks behave sensibly at that shape is a calibration question
   nobody has asked.

#### Interpretation update recorded 2026-08-22

**Status:** answers open question 3 of the 2026-08-22 subscription entry above.
Answered by the agent at Weibao's instruction rather than by him.

**The dividing line.** Keep every part of the notes-to-quiz loop where the note
is evidence about the learner. Drop every part where the note is evidence about
the world. Consumer apps in this class blur the two, and that single blur is
what produces a confident wrong card from a confidently wrong note.

**Worth having, all five safe under that line:**

1. Intake and transcription of the learner's own pages, image kept as the
   record. Transport, carrying no truth claim at all.
2. Gap detection against the bound source: objectives the learner wrote nothing
   about. Pure diagnosis, needs no key.
3. Misconception mining. The learner's wrong wording becomes a candidate
   distractor on a source-backed item, subject to author review. This is the
   highest-value use in the whole loop and it is safe precisely because the key
   still comes from the source, so the note improves the question without ever
   answering it.
4. Unkeyed self-prompts, labeled as from your notes, ungraded and editable.
   This is the fast Gizmo-style loop, minus the claim.
5. Note-driven selection: the notes decide which source-validated objectives
   get practiced next. Influence over what is asked, never over what is right.

**Not worth having, at any convenience:** auto-cloze from highlights, already
rejected in stream 12; any key derived from a note; and streak or score
gamification attached to note quizzing, which would put a progress claim on
material the evidence rules do not let it stand on.

**Recommendation on the scheduling question:** paper-note intake earns a narrow
phase. Items 1 through 3 above are bounded, and every rule they need is already
written in stream 12 and the 2026-08-21 entry. Item 4 is small. Item 5 waits on
the graph. The unscored commitment item from the fit check should be scoped
with it, because it is the one new type both halves of this entry ask for.

**Planning effect:** none scheduled yet. When it is, the phase covers intake,
gap detection, distractor mining, and the unscored commitment type, and it
cites `research/phase-16/12-active-annotation-notes.md` section 7 as its
authority rather than restating it.

### 2026-08-26: Navigate2 as a scrapeable template for organizing multiple courses

> Scrape and download code and more accordingly starting from https://navigate2.jblearning.com/my/courses.php
>
> as a way to organize multiple courses and more, we can use this as an template and develope better ones as we try more learning programs and more, dont forget to record all these in user vision as well accordingly

#### Interpretation recorded 2026-08-26

Separate from the quotation above.

**The durable intent is the container, not the specimen.** The clause that
matters is "a way to organize multiple courses and more". itembank has banks,
sessions, lessons and a cross-subject `day` cockpit, but no durable object that
says this is a course, these are its parts, here is where the learner stands in
it. Every new subject therefore costs bespoke wiring. Navigate2 was walked as
the first specimen of that container. The proposed answer is
`.planning/COURSE-SHELL-TEMPLATE.md`, a tentative v0: workspace, course, unit,
treatment.

**"Use this as a template and develop better ones" is accepted as a method, and
it is the more important half of the statement.** It sets up a repeating
practice rather than a one-off copy: study a real learning program, tear it
down into observed fact and separate interpretation, take what is good, record
what is rejected and why, and raise the template each time. Section 8 of the
template names the next candidate specimens (Brilliant, Albert, Anki, Khan,
Duolingo, edX or Coursera). This is compatible with the existing bounded
research-wave contract in `AGENT-WORKFLOW.md` and needs no new process.

**"Scrape and download code" was performed, with one boundary the agent set and
is recording rather than burying.** The pages were read in Weibao's own
logged-in browser and captured structurally to a scratchpad outside the
repository. Nothing was vendored. The finding that justifies the boundary is
also the finding that makes it cheap: the platform is stock Moodle 4.x with a
Boost child theme, Bootstrap 5 markup, and unmodified core `block_myoverview`,
and its design tokens are Boost defaults. There is no bespoke expression worth
copying, so the template is clean-room derived from the information
architecture. Moodle core is GPLv3; the `navigatexl` theme and JB Learning
branding are not ours. No item content, eBook text, or TestPrep question was
extracted, and the never-a-content-store rule was applied exactly as it was to
the 2026-08-22 paper handouts.

**The specimen's central defect is now a design rule.** Navigate2 gives every
chapter the same nine activities, seven of which are plain outbound links, and
completes all nine with a self-pressed `Mark as done`. Its gradebook carries 41
SCORM rows and one practice assessment, all empty. Eight of nine activities
emit no evidence and the shell still displays `Progress: 0 / 9`. That is
presentation state standing in for evidence, which the standing rule forbids.
The template answers it in two places: treatment purpose determines the
evidence contract, and coverage and mastery are shown as two numbers that may
never be merged. There is no `Mark as done` primitive; the nearest thing is a
typed, dated, visibly-a-claim `self_report` on a reading.

**One mechanism is taken outright.** Moodle 4.x types activities by pedagogical
purpose and tints them consistently course-wide. Navigate2 inherits it and
leaves every purpose blank. itembank should define its own closed set (`orient`,
`read`, `teach`, `drill`, `apply`, `check`, `reflect`) and make purpose
load-bearing rather than decorative, because purpose is exactly what decides
whether a treatment may move a mastery number.

**What this does not settle.** The template ships three levels below the
workspace. The 2026-08-13 entry asks for field, subject, subcourse, concept and
for progress on completing an entire field, and that depth question stays open
by the same reasoning Weibao gave then: what counts as an entire field needs
more ideaboarding. Four further questions are carried in section 7 of the
template, the sharpest being that no evidence event type exists today for a
non-scored treatment, so `self_report` needs an honesty story before it ships.

**Planning effect.** Recommendation only, nothing accepted. Evidence is
`.planning/research/2026-08-26-navigate2-teardown.md`; the proposal is
`.planning/COURSE-SHELL-TEMPLATE.md`. Binding scope remains
`SOURCE-TO-COURSE.md`, and the course shell has no phase assignment yet.

### 2026-08-26: the course first page, reading as its own surface, and TestPrep

> commit this, dont forget the first page for the course either, like how it shows the completeness and  more? Other stuff to consider?
>
> Reading stuff, well this one is where the readings are in the sections/chapters, which is a good enough way for now but we can have a better page or tab for reading and more, and everything testprep right now is localized into https://testprep.jblearning.com/TestPrep/Home/MyHome?ProductId=... which is also worth scraping, more stuff to consider and more?

(The TestPrep URL is abbreviated above only to keep an account-scoped product
token out of the record. The full link was supplied by Weibao and was used.)

#### Interpretation recorded 2026-08-26

Separate from the quotation above.

**"The first page and how it shows the completeness" turned out to be the
sharpest finding of the whole teardown.** The workspace card shows one number,
a bar reading `0% complete`, and the course landing page shows the same
quantity per section as `Progress: 0 / N`. Both are activity-completion counts
that never consult the gradebook. Counted out: the course holds 435 activities,
41 of which carry a grade item, so **394, or 90.6%, complete by a self-pressed
`Mark as done`**. A learner who opens nothing and ticks every box reads as 100%
complete beside an empty gradebook. The template's answer is that the first page
shows three quantities that may never be merged into one bar, `coverage`,
`mastery` and `claimed`, with `claimed` rendered visibly weaker because it is
the learner's own word, and `mastery` the one shown if only one fits.

**The reading judgment is accepted as stated, and refined rather than
overturned.** Readings living inside the chapter is the correct default
placement, because a reading belongs to the objective it serves and pulling it
out would break the treatment ladder. What Weibao is missing is a second view
over the same bindings, not a second home for them: a `Read` tab across all
courses, grouped by source so a book reads as a book, showing what is bound,
what each objective cites, what has been read, and coverage of the source itself
as distinct from coverage of the course. That is a renderer over existing `read`
bindings and costs no new durable object. Section 5.3 of the template.

**TestPrep was scraped and is the best-designed thing in the specimen.** It is a
separate application on a separate domain, reached by an outbound link. Three of
its four selection ideas are already itembank's, which is useful independent
confirmation rather than new scope: `Tutorial Mode` versus `Test Mode` is
mode-gated disclosure arrived at by another vendor for the same reason, and
`Include Confidence meter` ships checked by default, so the existing `conf`
field is not an eccentricity.

**Two genuine gaps came out of it.** First, **pool depletion**: every category
reads as unanswered over total, `Airway and Breathing (115 / 115)`, over a
`Qbank (690 QUESTIONS)` at `0 Taken, 690 Remaining`. itembank records attempts
but has no notion of how much of a bank has ever been seen, and that number
answers whether the learner is practising or recycling. Second, **error-driven
reselection**: the checkbox `Include questions previously answered incorrectly`
composes a form from the learner's own wrong answers, which itembank holds the
evidence to do and has no selector for. Both are recorded in section 5.4.

**One thing from TestPrep is explicitly rejected.** Its six categories hold
exactly 115 items each. That flatness is a content-production artifact, not a
blueprint, and the real NREMT weights its domains unevenly. Equal pools per
category quietly teach the wrong proportions. A blueprint in itembank states
weights explicitly, and the linter should notice suspiciously flat category
counts.

**The silo is the finding that matters most, and it is the invariant observed
failing in the wild.** TestPrep knows taken, remaining, correct, incorrect,
confidence and per-subject depletion. Moodle's gradebook knows 41 empty SCORM
rows. Neither knows what the other knows, so the learner's real evidence is
split across two products that cannot see each other, and no page in either can
answer "how am I doing". This is exactly what one runtime, one scorer, one
evidence store exists to prevent, and it is worth keeping as the standing
example of why.

**Boundaries held during the scrape.** The practice-test dialog was opened to
record its options and cancelled without creating a test; no assessment was
started; no item text was viewed or captured; the 690-item Qbank remains at
`0 Taken`. Nothing was vendored.

**Planning effect.** Still recommendation only. Evidence is
`.planning/research/2026-08-26-navigate2-teardown.md` sections 2c and 2d; the
proposal is `.planning/COURSE-SHELL-TEMPLATE.md` sections 5.1, 5.3 and 5.4.
Open questions grew from five to seven: pool depletion needs a definition of
what "seen" counts, and the reading view probably borrows the unresolved
`self_report` answer rather than needing its own.


#### Correction appended 2026-08-26

Appended the same day, before commit, and kept separate from both the quotation
and the interpretation above rather than folded into either.

The proposal recorded above was written **without first reading the shipped
Phase 14B code or `REQUIREMENTS.md`**, and three of its parts duplicated work
that already exists. `graph.py`, `course.py` and `course_package.py` ship the
course sidecar, containers with free-text labels nesting arbitrarily,
objectives, treatments, outline projection, and validated package export and
restore.

- The proposed fixed three-level hierarchy is withdrawn. Containers already
  nest freely, deliberately, because GRAPH-01 requires a local structural label
  to be accepted without a schema change.
- The proposed seven treatment purposes are withdrawn. TREAT-01 already defines
  an eleven-value closed vocabulary, and proposing a parallel one is the
  second-authority mistake this repository legislates against.
- The proposed coverage / mastery / claimed model is withdrawn. GRAPH-03
  already specifies seven permanently separate dimensions with no aggregate
  score, and is owned by Phase 16C.

**What actually remains missing is one level: the workspace**, the named set of
courses. The teardown's other findings stand, and the 90.6% measurement is now
recorded as field evidence for GRAPH-03's no-single-score clause rather than as
a competing model. Dispositions are in `IDEA-LEDGER.md` IL-20260826-01 through
-12; the withdrawn parts are marked Duplicate there rather than deleted.

This correction is recorded because the same mistake is cheap to repeat: the
planning documents describe the product, and the shipped code is ahead of the
part of them a fresh reader lands on first.

### 2026-08-27: percent is permitted, and user vision outranks a contract clause

> Percent is fine even if it breaks contract, since uservision over any other contracts and more

#### Interpretation recorded 2026-08-27

Separate from the quotation above. Recorded by the agent, who had argued the
other way the previous day and is recording the reversal rather than softening
it.

**Two rulings, and the second is larger than the first.**

**Ruling one, the narrow one.** A percent character and a progress percentage
may appear on a course card. This overrides plan 16B-04's must-have truth that
"no shelf card, chip, or resume cue contains a percent character", and its
prohibition, carried at `status: kept`, that "a single aggregate completion,
mastery, or readiness percentage must not appear on a course card". Both were
written by the agent-side planning process, not by Weibao, and he has now ruled
against them.

**Ruling two, the standing one.** `USER-VISION.md` outranks any other contract
in this repository. This is a precedence rule and it applies beyond percentages.
It resolves a question the planning documents never stated: `USER-VISION.md`
already described itself as the authoritative intent record, but nothing said
what happens when it conflicts with `REQUIREMENTS.md`, a phase plan's
`status: kept` prohibition, or a hard rejection in the Phase 16 synthesis. The
answer is that the vision wins and the other document is amended to match.

**What this costs, stated once and then acted on.** The 2026-08-26 teardown
measured Navigate2's completeness bar at 90.6% self-report and argued from that
that a single card percentage is a fabricated measurement presented as fact.
That argument is not withdrawn as an observation about Navigate2; it is
overruled as a constraint on itembank. The risk it names is real: a percentage
invites a learner to read it as attainment. Weibao has weighed that and decided
a percentage is worth more than the risk, and that is a legitimate owner
judgment about his own tool rather than a mistake to be argued down twice.

**One distinction the agent kept without being asked, and which Weibao may
strike.** Navigate2's failure was not the percent character; it was a
percentage with no honest denominator behind it. The mockup therefore shows
percentages that are computed from a real numerator over a real denominator the
records actually hold: objectives carrying an accepted treatment binding, over
objectives. The card whose record cannot be read shows `unknown` instead of a
number. If Weibao wants a synthesized cross-dimension figure as well, or wants
the denominator dropped, that is a further instruction and it will be followed;
the distinction is preserved here only because it was free.

**Blast radius, flagged rather than silently applied, then applied on
instruction.** The clause overridden is not only 16B-04's. The agent listed the
four affected documents rather than editing them, because amending a
requirement and a hard rejection is a recorded act rather than a side effect of
a mockup change. Weibao then instructed "yes, apply all four amendments", and
**all four were applied the same day**, each preserving its original wording for
trace and none deleted. The four:

- `REQUIREMENTS.md` **GRAPH-03**: "no single aggregate completion, mastery, or
  readiness score is produced". This is a requirement, not a plan clause.
- Phase 16 synthesis section **12.4**, which carries the single-aggregate-score
  rejection in the permanent hard-rejection ledger. Under the append-only rule
  it is overturned by a dated note with evidence and authority, never deleted.
- Plan **16B-04**: the line 30 must-have, the line 39 prohibition, threat
  **T-16B-04-05** ("an invented progress figure presented as a measurement"),
  and the three tests at line 301 and line 384 that assert a percent character
  appears in no chip, cue, or CTA.
- `IDEA-LEDGER.md` **IL-20260826-03**, whose disposition rests on GRAPH-03.

**Planning effect.** The mockup at `prototypes/16b/` shows percentages as of
today, and all four document amendments are applied. The applied state is
recorded in `IDEA-LEDGER.md` IL-20260827-01. Phase 16B's remaining blocker is
unchanged and unrelated: its precondition check still halts on Phase 16A.

**One replacement rule the agent adopted throughout, not instructed.** Where the
old text forbade a percent, the amendments do not simply delete the constraint;
they replace it with the requirement that a percentage carries the numerator and
denominator it came from, and that a record supplying neither reports
indeterminate rather than an invented number. This is the agent's reading of
what the ruling permits (a percentage) versus what the ruling was reacting
against (being told no). It is recorded as an agent choice so Weibao can strike
it with one sentence if he wants the constraint gone entirely rather than
replaced.

### 2026-08-27: adaptability and modularity as a coding principle

> make adaptability and modularity a important coding principle, (add to uservisio as well

#### Interpretation recorded 2026-08-27

Separate from the quotation above.

**Status:** active direction, newly stated, with one open question named below.

**Origin, stated plainly because it matters.** This was given in place of an
answer to the Phase 14B-05 checkpoint (what `manifest.json` carries, and whether
a package is a plain directory tree, an archive by default, or BagIt). **It is
recorded here as a standing principle and is NOT read as an answer to that
checkpoint.** 14B-05 remains unanswered and wave 5 remains stopped. Treating a
general principle as a specific one-way answer is exactly the silent-default
pattern every 14B plan forbids.

**Current interpretation:** adaptability and modularity join the small set of
standing coding principles the project judges designs against, alongside the
existing one-parser, one-scorer, one-evidence-store invariant and the
additive-format rule. Concretely, and in the terms this repository already
uses: a capability should compose rather than special-case; a new medium,
treatment kind, item type, surface, or backend should enter through a
registered extension point rather than through a branch inside an existing
function; a durable artifact should stay readable and reusable by something
other than the tool that wrote it; and a part should be removable with a
stated degraded behaviour rather than being load-bearing by accident.

**What it does not license.** Modularity is not a reason to add a second
parser, a second scorer, or a second evidence store, and adaptability is not a
reason to leave a durable contract unfrozen. Those two are the standing
non-negotiables, and this principle is judged inside them rather than against
them. Where the two genuinely pull apart, for example the 14B-06 freeze
question (freezing record shapes buys composability for 15A and 16A, and costs
adaptability if the shapes turn out wrong), the tension is a decision to be
put to Weibao, not one an agent resolves by citing this entry.

**Open questions:**

1. Whether this is meant as a general standing principle, which is how it is
   recorded here, or as guidance specifically toward the most modular of the
   three 14B-05 package shapes. A plain directory tree is the most adaptable
   and the most independently readable of the three, so the principle does
   point that way, but the checkpoint is rated by its plan as needing an
   explicit answer and is being re-asked rather than inferred.
2. Whether it should become a testable obligation in `REQUIREMENTS.md` (a
   MAINT-family requirement) or stay a judgement principle. Not decided here.

**Planning effect:** recorded as direction. No requirement is added, no phase
is opened, and no checkpoint is answered by this entry. It is available to be
cited in design arguments from 2026-08-27 onward, and under the 2026-08-27
precedence ruling it outranks a conflicting clause in another document.

**Relationship to prior entries:** extends the 2026-08-13 "keep the goal
editable" and "complete app flow" entries, and sits beside the 2026-08-09
constraint relaxation, which already judged ideas on product merit and real
cost rather than on a fixed stack.


### 2026-09-06: SaaS-quality experience in the desktop product

> Consdiering SAAS as an entry point, whatever that means?

> I guess SAAS experience or wahatever thats fitting, I mean the goal will be a electron app or something so I am unsure

> That makes more sense, how can that be combines with current plans and more?

#### Interpretation recorded 2026-09-06

**Status:** active direction. The desired experience is settled enough to guide
current work. A hosted SaaS business is not requested by these statements.

**Current interpretation:** itembank should feel like a coherent, approachable
software product rather than a collection of local tools. The useful part of
the SaaS comparison is the experience: guided first use, a clear course home,
visible progress and recovery for long operations, understandable settings,
consistent navigation, and ordinary product controls. The current Tauri shell
already carries the desktop goal, so Electron is an example of an installed
app and not a request to replace the shell. Canonical courses, sources, banks,
and evidence remain local. Hosted services remain optional and disclose exact
egress.

**Open questions:** commercial licensing, subscriptions, managed model usage,
cloud synchronization, and accounts are not settled by this entry. Each would
need a separate user decision because each changes cost, privacy, recovery, or
data authority. The current direction needs none of them.

**Planning effect:** no new architecture or phase is created. The binding
experience statement is added to `SOURCE-TO-COURSE.md`. The Reach milestone
uses the Phase 18 cold-install evidence, the Phase 19D visible learner journey,
and the current UI character audit as the acceptance path. The UI audit remains
a bounded implementation proposal and does not gain authorization to change
application code from this interpretation alone. `IDEA-LEDGER.md`
IL-20260906-07 records the disposition.

**Relationship to prior entries:** extends the 2026-08-13 complete app flow,
visual ambition, source-to-course, and course-shelf entries. It also extends
the 2026-08-22 paid-learning-subscription entry from capability substitution
to product coherence. It does not reverse that entry's distinction between
recreating an experience and recreating a business. It confirms the existing
local-first, no-hosted-storage direction.

### 2026-09-06: comprehensive future UI character

> that UI is alot more better and has more character than mines currently, did we have it in the books to adjust to have more character? we can forget how the ui was prior and improve it comprehensicely in the future accordingly

#### Interpretation recorded 2026-09-06

**Status:** active direction. The future visual redesign may replace the
current visual language comprehensively rather than treating its appearance as
a compatibility requirement.

**Current interpretation:** itembank should develop a distinctive, coherent,
and engaging learning-workspace identity. The reviewed Syntax Lab interface is
evidence that a focused hierarchy, restrained but deliberate color, concise
controls, a strong activity frame, and visible interaction state can give a
small learning surface more character. It is a reference point, not a request
to copy its code-training layout or visual details. Existing runtime behavior,
learning authority, accessibility, responsive use, local data, and durable
learner settings remain constraints. The current colors, component shapes,
page composition, theme catalogue, and default look do not.

**Open questions:** the final visual direction, component vocabulary, motion,
illustration, density, and treatment of existing optional looks require
comparative prototypes and direct user review. Retiring a saved look or theme
needs an explicit migration and recovery decision. This entry does not select
Syntax Lab as the final design.

**Planning effect:** the UI character audit owns the revised comprehensive
design direction. Its earlier bounded preservation-first proposal is partly
superseded as a future visual target, though its verified defects and
accessibility gates remain valid. The current Reach milestone may still fix
functional UI defects without opening a redesign. A future UI phase should
prototype materially different directions against the complete course journey
and may promote a new default after user review.

**Relationship to prior entries:** strengthens the 2026-08-13 visual ambition,
the 2026-08-16 structured-studio selection, and the 2026-09-06 SaaS-quality
experience direction. It partly supersedes preservation of the current
production aesthetic in the 2026-09-06 UI character audit. It does not
supersede the local-first product, one-runtime authority, readable lesson,
responsive, accessibility, or recoverability requirements.

### 2026-09-06: Syntax Lab inspiration and an expandable CS Dojo

> we can even be inspired by 'syntax lab' from diego, incoporate that into a relevant subsection, or as a cs dojo and stuff, it can easily be expanded for other leanguages and more

#### Interpretation recorded 2026-09-06

**Status:** exploratory product direction. Syntax Lab may inspire a dedicated
CS Dojo capability as well as the broader visual redesign.

**Current interpretation:** a CS Dojo would be a focused executable-practice
surface within a course. It can preserve Syntax Lab's useful rhythm of prompt,
editor, provided context, deterministic check, actionable feedback, retry, and
next activity while connecting every exercise to itembank objectives, runtime
authority, and durable evidence. Language support should be adapter-based so
Python and JavaScript are initial examples rather than a closed list.

**Open questions:** the first supported languages, execution isolation,
resource limits, package policy, multi-file projects, compile versus run
activities, debugging and test-writing treatments, and the boundary between
instructional practice and formal assessment require a reversible prototype
and threat review.

**Planning effect:** the audit remediation plan's executable-practice section
owns the bounded CS Dojo prototype route. `IDEA-LEDGER.md` IL-20260906-09 records
its disposition. No current item format or milestone scope changes until the
prototype passes its runtime, evidence, security, accessibility, offline, and
recovery gates.

**Relationship to prior entries:** extends the comprehensive UI character entry
and its Syntax Lab comparison. It also gives the existing runnable-code and
changed-context application goals a concrete optional surface. It does not
make executable practice the default treatment for every programming
objective.

### 2026-09-07: CS coursework extension beyond code drills

> adjust and add into plan or make these addressed accordingly? so we can have a code learning sub program/extension for cs coursework and more, will whatever is happennigning in code learner be psueudo leetcode and more?

#### Interpretation recorded 2026-09-07

**Status:** active product direction. The CS Dojo route must cover a coherent
CS coursework extension rather than only a bank of short code-completion
drills.

**Current interpretation:** the code learning extension belongs inside a
course as an optional, objective-linked CS Dojo. Its activity range includes
code reading and prediction, tracing and explanation, typed executable code,
debugging, test construction, tool and multi-file work, and learner-owned labs
or projects. A concise function challenge similar to LeetCode is one useful
practice mode, but it does not define the extension or provide a curriculum by
itself.

**Open questions:** the first representative course and languages, the safe
execution and package boundary, which activity responses become formal scored
items, how multi-file and terminal work degrades offline, and which project
qualities require human review remain prototype decisions.

**Planning effect:** D3.1 of the consolidated audit remediation plan now owns
the question-and-activity matrix, the distinction between drill practice and
authentic coursework, and a broader representative prototype gate.
`IDEA-LEDGER.md` IL-20260906-09 carries the amended prototype scope. No new
item type is committed until the activity contract proves whether executable
code is an item response, a lesson capability, a learner artifact, or more
than one of these under distinct policies.

**Relationship to prior entries:** extends the 2026-09-06 Syntax Lab and CS
Dojo entry. It narrows the interpretation that Syntax Lab's current drill
shape could stand for the whole extension, while retaining its editor,
declared-context, deterministic-check, retry, and feedback patterns.

### 2026-09-06: close audit findings and prefer the best-fitting future UI

> keep in mind the audit findings and make sure everything will be addressed, making sure our future UI is modern and fitting and that anything old can be replaces if there are better/more fitting options and more

#### Interpretation recorded 2026-09-06

**Status:** active direction. Audit findings must remain traceable to closure,
and the future UI is not constrained by the age or current presence of a
component or visual pattern.

**Current interpretation:** every accepted audit finding needs a durable final
state with an owner and evidence. The future interface should use contemporary,
task-appropriate interaction and visual patterns that make the source-to-course
workspace coherent, understandable, accessible, and comfortable for sustained
learning. Existing components, navigation, themes, layouts, and presentation
patterns may be retained, redesigned, migrated, or replaced according to which
option better serves that outcome. Modern does not mean copying a trend. It
means clear hierarchy, familiar controls where familiarity helps, responsive
behavior, visible state, purposeful character, and reduced friction across the
complete course journey.

**Open questions:** comparative prototypes and representative learner journeys
must determine the final visual language. A replacement that changes stored
preferences, navigation behavior, accessibility semantics, or recovery needs a
reviewed migration and fallback. Human visual and accessibility acceptance
remain required where already assigned.

**Planning effect:** the UI character audit gains an explicit replace-or-retain
fitness test. The consolidated remediation plan gains an audit closure
protocol. Reach continues to fix immediate journey defects first, while the
comprehensive visual replacement remains a later reviewed phase. No audit item
may disappear merely because its milestone or original plan closes.

**Relationship to prior entries:** confirms and sharpens the 2026-09-06
comprehensive future UI character, SaaS-quality desktop experience, audit
remediation, and UI-priority entries. It does not supersede accessibility,
local-first ownership, runtime authority, responsive use, or recoverability.

### 2026-09-06: keep the final design language open

> save and adjust accordingly, we are unsure and we can establish better in the future

#### Interpretation recorded 2026-09-06

**Status:** partly superseded. The need for a coherent modern design language
remains active, but Monkeytype is no longer part of the app-wide comparison.

**Current interpretation:** retain three credible directions for comparison:
a calm editorial learning studio, a focused practice instrument inspired by
the clarity and visible state of tools such as Monkeytype, and a crafted
workshop that combines reading and doing. A hybrid may ultimately assign these
qualities to different modes under one shared system. No direction is selected
by this conversation alone.

**Open questions:** representative prototypes must show which direction best
supports shelf navigation, sustained reading, active practice, assessment,
notes, evidence, agent operations, recovery, desktop use, and mobile use. User
review should select the direction after those comparisons rather than from a
single attractive screen.

**Planning effect:** the future UI phase must prototype the three directions or
justify a smaller comparison set from evidence. It uses the same content and
tasks for each prototype and records what is retained, combined, superseded,
or rejected. Current Reach work may fix navigation and interaction defects but
does not establish the final design language.

**Relationship to prior entries:** narrows the commitment implied by the
2026-09-06 comprehensive UI and best-fitting replacement entries. It confirms
their outcome and replacement freedom while keeping the final aesthetic and
mode balance open.

### 2026-09-06: Monkeytype is coding-surface inspiration

> monkey type's ui design was the intended insiration for code sstuff, we just need good design language and more and stuff

#### Interpretation recorded 2026-09-06

**Status:** active clarification.

**Current interpretation:** Monkeytype's visual focus, immediate state,
keyboard fluency, customization, and low-friction repetition may inform coding
practice and CS Dojo. It should not define the course shelf, lessons, notes,
evidence, settings, or the application shell. The complete product needs its
own fitting design language with shared typography, color, spacing, geometry,
navigation, state, and accessibility rules.

**Open questions:** the broader design language remains unsettled. Comparative
prototypes should explore coherent learning-product directions without treating
a typing or coding tool as the overall product archetype.

**Planning effect:** remove Monkeytype from the app-wide candidate comparison
and retain it only in the CS Dojo reference and prototype route. The future UI
phase still compares broader design systems across the complete course journey.

**Relationship to prior entries:** partly supersedes the 2026-09-06 open
design-language interpretation where Monkeytype informed a general focused
practice candidate. It confirms the separate Syntax Lab and CS Dojo entry and
the requirement for a comprehensive modern design language.

### 2026-09-06: make the broader product feel like a technical instrument

> all of them feels a little weak, I want a techy feel like monkey type or something else, update accordingly?

#### Interpretation recorded 2026-09-06

**Status:** active direction.

**Current interpretation:** the three initial broad directions lacked enough
technical character. The app-wide language should feel precise, responsive,
purposeful, and tool-like through strong state communication, disciplined
monospace accents, keyboard confidence, compact but readable controls,
high-contrast focus, restrained surfaces, and meaningful data density.
Monkeytype is one reference for this quality, but its typing-test layout still
belongs chiefly to coding practice and CS Dojo. The product should not become a
terminal imitation, code editor, neon dashboard, or typing-test clone.

**Open questions:** a revised prototype pass must test at least three distinct
technical languages and determine how much density, color, motion, and
monospace treatment remains comfortable for long reading and broad subject
matter. User review selects the balance.

**Planning effect:** the prior editorial, workspace, and workshop prototypes
are rejected as presented, not as abstract categories. The next prototype pass
must show stronger technical-instrument character across the same course
journey. Preserve the best reading and learning qualities only when they fit
the sharper shared system.

**Relationship to prior entries:** refines the open design-language and
Monkeytype-scope entries. It broadens Monkeytype's influence to the desired
level of precision and technical character while keeping its specific layout
and coding interaction patterns scoped to CS Dojo.

### 2026-09-06: keep both selected finalists on one foundation

> Okay [Measured field guide](/Users/weiwei/.codex/worktrees/d78d/itembank/prototypes/17c-finalists/field-guide.html)
>
> 1. [Learning trajectory deck](/Users/weiwei/.codex/worktrees/d78d/itembank/prototypes/17c-finalists/trajectory-deck.html)
>
> Those two are the most fitting, we can keep both? Make method to setup base stuff and make it easy to adapt or implement skills in the future? other stuff to consider?

#### Interpretation recorded 2026-09-06

**Status:** active direction.

**Current interpretation:** retain Measured Field Guide and Learning
Trajectory Deck as two coordinated compositions built from one design system.
Field Guide is strongest for source-grounded reading, explanation, annotation,
and reflection. Trajectory Deck is strongest for course movement, active
practice, evidence, operation state, and recovery. Shared semantic roles,
tokens, primitives, state language, navigation identity, and accessibility
behavior must make them recognizably one product.

**Open questions:** implementation must test whether the compositions should be
selected automatically by task, offered as user-selectable presentation
profiles, or combined within a single journey. The first production vertical
slice should resolve this without maintaining duplicate markup or state logic.

**Planning effect:** preserve both prototype files in the main checkout. The UI
character audit owns a layered foundation and extension method. Future learning
capabilities map their semantic needs to shared primitives before requesting a
new component. Production migration begins with one representative vertical
slice and expands only after visual, behavioral, responsive, accessibility,
settings, and recovery gates pass.

**Relationship to prior entries:** resolves the finalist-selection question
created by the open design-language and technical-instrument entries. It keeps
the permission to replace old presentation while narrowing future work to two
selected compositions and one shared foundation.

### 2026-09-06: expose both finalists as presentation profiles

> so both can be kept as a switchable theme or something, save and update things accordingly? more to consider

#### Interpretation recorded 2026-09-06

**Status:** active direction.

**Current interpretation:** Measured Field Guide and Learning Trajectory Deck
remain available as user-switchable presentation profiles. A profile controls
composition, navigation arrangement, density, and emphasis. Color scheme,
contrast mode, and accent remain independent appearance settings, so either
profile can support light, dark, OLED, high contrast, and custom accent where
the contrast derivation permits it. Both profiles render the same semantic
content, URLs, runtime state, evidence, and accessibility meaning.

**Open questions:** the first implementation slice must settle the default
profile and whether an optional automatic task-based mode adds value. It must
also test whether profile choice is global or may be overridden per course.
No automatic mode or per-course override is committed yet.

**Planning effect:** add a recoverable presentation-profile setting with a live
preview and explicit fallback. The UI character audit owns the setting model,
extension contract, and cross-profile verification. Future capabilities must
work in both profiles or declare an honest equivalent fallback before release.

**Relationship to prior entries:** resolves the switchability question in the
selected-finalists entry. It keeps both compositions and supersedes automatic
task-based switching as the assumed first implementation, while retaining it
as a later option to test.

### 2026-09-07: make the complete UI adaptable through extensions and themes

> for UI 2, we can have the UI designs be implemented extension/theme style, for everything and anything can be updated or adjusted as extension accordingly? thoughts? Plug other parts in accordingly and more, then create a prompt to continue work

#### Interpretation recorded 2026-09-07

**Status:** active direction.

**Current interpretation:** the learner interface should be composed from
stable semantic roles, shared primitives, presentation profiles, appearance
themes, and capability adapters. A new or revised course shell, reader,
activity presentation, editor, source view, agent panel, or integration should
enter through a named seam instead of requiring an unrelated frontend fork.
Profiles and themes may replace or rearrange presentation broadly while the
same canonical content, runtime state, assessment authority, evidence, rights,
accessibility meaning, and recovery behavior remain underneath.

**Open questions:** the future UI phase must prove the smallest descriptor and
mount contract on one representative vertical slice. It must decide which
variation belongs to a profile, an appearance theme, a capability adapter, or
a separate product surface. External package loading remains unresolved until
its supply-chain and isolation gate is accepted.

**Planning effect:** strengthen the UI character plan and extension-delivery
contract around named presentation and capability seams. Implement the two
selected profiles as the first proof. Require representative cross-profile,
responsive, accessibility, unavailable-state, migration, and recovery checks.
Use `PROMPT-EXTENSIBLE-UI-CONTINUATION-2026-09-07.md` as the next operational
handoff after current Reach packet ownership is reconciled.

**Relationship to prior entries:** extends the selected-finalists and
switchable-profile entries. It also applies the existing named-seam plugin
direction to the complete presentation layer without reopening the rejected
swappable-authority design.

### 2026-09-07: comparative homes, complete transitions, and renewable UI research

> like right now its like this, and I assume it can be sectioned better somehow but Im not sure how, can we look accross existing learning platforms and LMS and more and scope improvements?

> unsure, we can have multiple options and implement all of them and have the user decide what they like instead, look accross sites and more and scope accordingly

> Save accordingly also need to consider UI flow, from returning to home/finishing exam/quiz and more,&#x20;
>
> Combine prior audits and new findings, make prompt to look further, also looking at githubs and repos and more, and then make sure we can absorb everything and more and address everything

> re research in case of new info and more in the future

#### Interpretation recorded 2026-09-07

**Status:** active direction.

**Current interpretation:** the future UI comparison must cover the complete
learner journey rather than isolated screens. Home may have multiple reversible
projections over identical course and runtime state so the user can compare a
resume-first, shelf-first, agenda-first, and within-course path presentation.
The comparison must include leaving and returning home, starting and stopping
activities, completing practice, quizzes, and exams, post-assessment review and
remediation, exact resume, interruption, stale or changed courses, and course
completion. Existing audits and current platform evidence are reconciled before
new recommendations. Public repositories contribute inspectable behavior and
test patterns, not code to copy. Research remains renewable through named
change, failure, freshness, and coverage triggers.

**Open questions:** comparative prototypes and learner review must determine
which home projections remain distinct, which combine, and which are
superseded. Deeper research must verify current product behavior and repository
paths, identify omitted transitions, and set evidence-specific freshness
windows. No permanent four-view commitment or automatic switching rule is
settled.

**Planning effect:** add the exploratory scope note
`notes/2026-09-07-home-and-transition-ui-scope.md`, the research handoff
`PROMPT-UI-FLOW-AND-OPEN-SOURCE-ABSORPTION-2026-09-07.md`, and idea-ledger
entry IL-20260907-02. Feed their verified findings into the existing UI
character owner and extensible-UI continuation after Reach. Do not expand the
active Reach execution path or change binding requirements from this initial
comparison.

**Relationship to prior entries:** extends the complete app-flow entries from
2026-08-13 and 2026-08-20, the 2026-09-06 comprehensive UI direction, and the
2026-09-07 extensible-presentation direction. It adds explicit home variants,
post-practice and post-assessment transitions, repository inspection, and
future re-research triggers. It does not supersede the selected Measured Field
Guide and Learning Trajectory Deck profiles.

### 2026-09-07: a learning harness for people, operated by AI

> should we consider itembank a learning based harness for ai in the future? or just keep it as is as something agentically driven?

> okay write that down accordingly

#### Interpretation recorded 2026-09-07

**Status:** resolved.

**Current interpretation:** itembank is a local-first, agent-operable learning
harness for people. Stable contracts connect learner-owned sources, objectives,
treatments, activities, assessments, evidence, validation, permissions, and
accepted revisions. AI may construct courses, tutor within runtime grants,
interpret evidence, and propose improvements. The learner remains the intended
beneficiary, and the deterministic runtime remains the authority for scoring,
assessment disclosure, session state, and accepted evidence. An AI-training,
reinforcement-learning, prompt-optimization, or general model-evaluation
harness is not the primary product identity.

**Open questions:** later research may test AI evaluation or improvement
capabilities that directly support learning-system quality. Each begins as a
registered capability and must prove a learner-centered use, inspectable
artifacts, declared evidence authority, rights and egress, validation, and
recovery before it affects product scope.

**Planning effect:** the north star in `SOURCE-TO-COURSE.md` now names itembank
as a local-first, agent-operable learning harness for people and distinguishes
that identity from infrastructure whose primary subject is training or
evaluating AI. Existing course, agent, runtime, and authority requirements
remain in force. `IDEA-LEDGER.md` records the framing and the gate for adjacent
AI-facing capabilities.

**Relationship to prior entries:** confirms the 2026-08-13 source-to-course
goal and course-generator direction. It clarifies the 2026-08-19 agentic
capability direction by naming the stable learning contracts as the harness
and agents as replaceable operators. It narrows neither useful AI work nor the
goal of supporting local and hosted agents.

### 2026-09-08: acquire transcripts, Canvas course material, and other sources

> extend itembank capability to scrape and download or absorb transcripts by providing tools like canvas stuff downloader and more, we can also audit other stuff to consider and more, and imprvoements for that repor or other lacking extention features

#### Interpretation recorded 2026-09-08

**Status:** exploratory.

**Current interpretation:** itembank should acquire learner-authorized course
material instead of requiring every source to be manually downloaded first.
The experience should include Canvas course discovery and download, transcript
and caption intake, optional transcription when captions are unavailable, and
an audit that exposes other missing acquisition capabilities. Acquisition feeds
the existing source adapter, binding, rights, and course-building contracts.

**Open questions:** research and a prototype must settle Canvas export versus
API order, token or OAuth handling, the exact first resource set, local ASR
backend choice, hosted transcription egress, assessment-content boundaries,
and which non-Canvas LMS format should follow. A real learner-approved Canvas
course walkthrough is required before promotion.

**Planning effect:**
`SOURCE-ACQUISITION-EXTENSION-AUDIT-2026-09-08.md` records the current capability
map, missing cases, proposed command surface, dispositions, sequence, and
acceptance gate. The work is routed after Reach and does not change the current
19D recovery path.

**Relationship to prior entries:** extends the 2026-08-20 remote-source and
paper-note OCR direction, the 2026-08-26 Navigate2 scrape direction, Phase 14C
source intake, and the 2026-09-07 extension architecture. It distinguishes
upstream Canvas course acquisition from the existing downstream Canvas LTI
surface. It does not supersede the requirement that unknown rights remain
restrictive.

### 2026-09-08: defer local AI and skip the sitting for now

> we can skip the sitting for now

#### Interpretation recorded 2026-09-08

**Status:** active direction.

**Current interpretation:** the current milestone may proceed without a new
Math 1400 assessment sitting and without repairing live local-model proposal
generation. Both remain deferred product-validation legs. No sitting, score,
mastery result, next-activity recommendation, accepted model proposal, or
model-backed treatment may be claimed from this decision.

**Open questions:** the deferred learner journey still needs a representative
source-grounded lesson and assessment, a runtime-owned sitting, honest evidence
denominators, and export and restore observation. The local-AI leg still needs
a parseable provider response through the strict proposal contract.

**Planning effect:** reconcile Reach and Phase 19D as closed under an explicit
scope waiver, retain their unmet evidence as deferred work with owners and
triggers, and allow Phase 20 to execute without manufacturing the missing
evidence. Phase 20 may use deterministic fixtures and existing representative
content for UI checks.

**Relationship to prior entries:** narrows the 2026-09-06 SaaS-quality Reach
exit and the 2026-09-07 UI handoff by deferring the new Math 1400 sitting. It
does not supersede the earlier evidence, assessment-authority, accessibility,
or recovery requirements.

### 2026-09-08: reader definitions and external documents

> future reader should have the option of double clicking for definition and more, be able to work with external slides/pdf/epub and more?

#### Interpretation recorded 2026-09-08

**Status:** exploratory interaction, active product direction.

**Current interpretation:** the future reader should let a learner act on text
to request a definition or related learning help, with double-click available
as one discoverable option. It should also work alongside external PDF, EPUB,
and slide sources by opening and navigating them, preserving source location,
and connecting selected passages or pages to definitions, notes, citations,
objectives, lessons, and activities. External files remain sources with their
own identity. Importing, annotating, editing, converting, and exporting them
are distinct operations rather than one vague mutation.

**Open questions:** a reader prototype must test double-click against ordinary
text selection and browser conventions, and settle the definition panel's
additional actions. It must provide equivalent keyboard, touch, and
screen-reader paths. Format trials must settle embedded versus side-by-side
display, locator fidelity, annotation ownership, supported slide formats, and
whether any format needs lossless round-trip editing rather than read and bind.

**Planning effect:** register a reader interaction prototype under the shared
lesson capability contract. Apply it to the existing PDF, EPUB, PPTX, and
source-adapter work rather than creating another parser or source model. No
current milestone is expanded until representative external files pass the
reader, rights, offline, accessibility, and recovery gates.

**Relationship to prior entries:** confirms the 2026-08-13 hoverable-definition
direction and extends the 2026-08-20 confusing-term criterion with an explicit
learner activation option. It also extends the 2026-08-14 editor and reader
direction and the source-intake work without superseding portable Markdown,
progressive enhancement, or restrictive unknown-rights behavior.

### 2026-09-08: adopt the greenfield learner interface in the original app

> okay with this, we bring this to the original itembank repo accordingly, scrapping old UI acordingly, open chat in right place accordingly

#### Interpretation recorded 2026-09-08

**Status:** accepted product direction.

**Current interpretation:** the accepted greenfield prototype now defines the
normal learner-facing visual identity in the original Itembank app. Its
personal desk, course-led path, source reading, practice, evidence, exact
resume, and proposal review belong on the existing production routes. The
prototype's browser-local answer key, scores, progress, revisions, and model
states remain synthetic and must not enter production authority.

**Open questions:** human touch-device, screen-reader, 200 percent text, 400
percent zoom, and aesthetic review remain acceptance gates. The deferred live
local-model proposal and four-subject parity backend remain separate from this
design adoption.

**Planning effect:** replace the shared production shell and its superseded
visual styling with this direction. Retain existing routes and canonical
runtime, evidence, source, objective, permissions, journal, and recovery
owners. Do not ship the prototype as a detached app, optional theme, or second
state store.

**Relationship to prior entries:** resolves the comparative UI exploration and
selects one product identity. It preserves the earlier extensible semantic
presentation seam as implementation infrastructure, not as a competing
learner-facing design.

## Interpretation protocol

An interpretation may appear immediately after a verbatim entry when it helps
the user inspect how rough ideaboarding became product direction. Use a dated
subheading and keep these fields explicit:

- **Status:** active, exploratory, partly superseded, superseded, or resolved.
- **Current interpretation:** the smallest faithful statement of meaning.
- **Open questions:** ambiguities that research or later ideaboarding must test.
- **Planning effect:** documents, requirements, or phases affected.
- **Relationship to prior entries:** confirms, extends, narrows, conflicts with,
  or supersedes named earlier statements.

Never edit the quotation when interpretation changes. Add a new dated
interpretation note, mark the older interpretation's status, and link both to
the decision that resolved the change. Later statements do not silently erase
earlier ones. A conflict remains visible until a dated resolution explains what
changed and why.

## Interpretation pointers

These files interpret, but do not replace, the statements above:

- `SOURCE-TO-COURSE.md` — current product contract and boundaries.
- `PROJECT.md` — milestone context and north star.
- `REQUIREMENTS.md` — testable obligations.
- `ROADMAP.md` — phased delivery.
- `UI-SPEC.md` — learner and reviewer experience.
- `PLANNING-DIRECTIVES.md` — standing rules for planning agents.

## What this vision is building into

The verbatim entries above feed a visible chain:

1. `USER-VISION-INBOX.md` captures meaningful rough ideaboarding.
2. This file preserves promoted product intent and dated interpretations.
3. `SOURCE-TO-COURSE.md` states the current product contract.
4. Research files test open questions and competing possibilities.
5. `REQUIREMENTS.md`, `ROADMAP.md`, and `UI-SPEC.md` turn accepted conclusions
   into obligations, sequence, and experience contracts.
6. Phase plans implement bounded work and verification checks shipped behavior
   against the original intent.

This chain is traceable in both directions. A plan should identify the vision
and research behind it. A vision entry should identify its current planning
effect without pretending that an unresolved idea is already a requirement.
