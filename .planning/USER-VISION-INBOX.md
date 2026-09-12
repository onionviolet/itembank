# User vision inbox

**Purpose:** preserve rough ideaboarding that may affect product intent before
deciding whether it belongs in the authoritative `USER-VISION.md`.

**Rule:** entries remain verbatim. Review them after the ideaboarding pass.
Promote statements about outcomes, experience, scope, values, boundaries,
users, success, or unresolved product direction. Route implementation ideas,
research leads, and task mechanics to their owning documents. A promoted entry
gets a dated disposition and link; it is not deleted from this inbox.

## Awaiting review

### 2026-08-13: files, hierarchy, onboarding, packaging, and future audit

> my words will have to go into user vision later, but also, stuff like the executable notebooks, editing files where they are at now, finding previous files, creating relevant folders, user friendly instructiojs like for readme and in app, user considerations, like the walkthrough for first time and more, the finial packaged app, and other stuff I could have mised, goal of being applicable to something super complex, like being able to create and relevant course/lesson, it can have subcourses/semester/conecpts that builds up a field or course? Like say for something like math, sub category for kind of math, then further and further more, maybe can show completion, and like a progress on "completing" the entire frield, but that could be implemented but what counts as an entire field and more will need more ideaboarding.

> Will also need furuther future audit on how and when to get everything done and more?

**Status:** promoted to `USER-VISION.md` on 2026-08-13. Research and planning
details remain routed through the Phase 16 research program.

### 2026-08-13: complete app flow, visual experience, files in place, and edge cases

> Also need to ideaboard/research comprehensively Comprehensive but also visually appealing app experience, what to show, how things folow, how things chain and more,  Splitting research into finer parts as needed? Working with files as they are and not moving them? More edge cases abd nire>

> How should we decide what to put into uservision, and what not to put? or just put everything?

**Status:** promoted to `USER-VISION.md` on 2026-08-13. The user-vision process
question also changed `PLANNING-DIRECTIVES.md`.

### 2026-08-14: comprehensive UI, powerful multi-style learning, and a fitting editor/reader

> also how to make sure UI is like good and comprehensive, learning part is powerful too, from notebook style to other potentially powerful style, or particularly stylized, and also for editor to be fitting too, can use the various editors, or readers, from stuff like Ellipsus and their competitors and other produccts and more

**Disposition:** Route (with one new research thread).

- "Good and comprehensive UI" and "powerful learning" are already owned by the
  Phase 16 flow/capability contract (16A/16B) and the Phase 17 visual system, with
  freeze-gate tracers. No new phase needed; make sure those gates actually run.
- "Notebook style to other potentially powerful or particularly stylized" styles
  route to the existing lesson-style work: `research/2026-08-10-lesson-style-catalogue.md`,
  `research/phase-16/06-feature-style-atlas.md`, and the registered output modes in
  synthesis 12.2 (notebook page, Cornell, concept map, glossary, formula sheet,
  timeline, comparison table, study guide). Open question already recorded: which
  styles are semantic transformations versus cosmetic themes.
- "Editor to be fitting, various editors/readers, Ellipsus and competitors" is a
  NEW research thread that widens the existing editor mechanics research
  (`research/2026-08-09-lesson-display-editor.md` Q2 = CodeMirror 6 + external-
  editor-watch + textarea floor) from a single-editor decision to a product
  landscape: versioned-prose editors (Ellipsus), block editors (Notion), markdown/
  local-first editors (Obsidian, iA Writer), and reader surfaces. Goal: confirm the
  in-app editor and the external-editor-in-place path are both "fitting," and mine
  reader/editor products for patterns without breaking the portable-file contract.

### 2026-08-14: walking skeleton, external-user v1, and agent-guided onboarding

> write the walking skeleton adjustment into the readiness audit, consider a proper v1 that would be good enough for a external user like my friend to make use of this, and the readme it would require for a user that doesnt know anything about it to use it? enough for him to paste the github to claude code or something and the nclaude code can read github and then can go through the setup for them and more>

**Disposition:** Split (2026-08-14).

- **Product intent (promote-worthy):** an external user, a friend, is now a
  named target for a "proper v1". This revises the recorded "Users: One"
  constraint: still one learner per installation, still no accounts, auth, or
  multi-tenancy, but a second person installing and using their own copy is now
  a supported goal rather than explicitly out of scope. It also fires the
  recorded trigger on `V2-DEL-01` ("signed binaries revisited when a second
  person runs the tool"). Onboarding must work for someone who knows nothing
  about the project, including the path where they paste the GitHub URL into
  Claude Code (or another agent) and the agent reads the repo and walks them
  through setup.
- **Routed:** the walking-skeleton adjustment landed as section A9 of
  `.planning/READINESS-AUDIT-14A.md`; the external-user v1 bar as section A10
  of the same file; the agent-guided onboarding section landed in `README.md`
  ("Quick start for someone brand new").

### 2026-08-14: durable plan standard, and agent-facing update awareness

> plan out the 13.9 walking skeleton so sonnet can execute it, need to set up this so that it is long standing for other plans as well, also need to include in readme, or in skills, updating the program and more, both skill wise and app wise? where the app can tell the agent that the app is outdated andd what new features and more, but that could be a future phase, write into vision accordingly

**Disposition:** Split (2026-08-14).

- **Product intent (durable):** two lasting capabilities are named. First, the
  planning standard itself: plans are written so a lesser model executes them
  without inventing decisions, as a standing practice, not a one-off. Landed as
  `.planning/PLAN-TEMPLATE.md` plus the executor bar in
  `PLANNING-DIRECTIVES.md` section 5. Second, **agent-facing update and
  capability disclosure**: the app should be able to tell an agent that the
  installed version is outdated and what new features and contracts arrived,
  so both skills and app knowledge stay current; skills likewise need an
  update path. This builds on shipped ground (`itembank update`, the
  disclosure-gated launch check, `itembank usage`, `itembank schema`) but the
  machine-readable "what changed for agents" surface does not exist yet.
- **Routed:** the walking-skeleton plans landed in
  `.planning/phases/13.9-walking-skeleton/`. Agent-facing update disclosure is
  registered as a future-phase capability on the Phase 18 roadmap entry (a
  candidate, not a commitment; it may also land earlier as a cheap additive
  surface, e.g. a versioned capability manifest the updater already knows how
  to fetch). The shipped `itembank update` step was added to the README
  agent-onboarding checklist. Skill-update mechanics route to the skill
  library's operation contract owner (slice 4b) when that surface exists.

### 2026-08-16: plugins as a feature mechanism; web and app runtimes

> consider the plugin-first core as a way to add or iwork on features instead? Also, a digital web based runtime and also a app based runtime too, readjust accordingly?

**Disposition:** Split (2026-08-16).

- **Product intent (promote-worthy):** the product should be usable both as a
  web experience in a browser and as an installed app. This extends the
  recorded end goal "a packaged desktop app" (2026-08-09 amendment) with a
  web-delivered sibling. One naming correction applies before this enters any
  plan: these are two shells over the one runtime, not two runtimes. The
  runtime invariant (one runtime, one scorer, one evidence store) means the
  web surface and the app surface are both clients of the same runtime, the
  same way the CLI and the loopback browser surfaces already are. A hosted
  multi-tenant web service is not implied and would conflict with the
  no-accounts rule and evidence-on-disk; the web shell is the learner's own
  runtime reached through a browser.
- **Routed:** the plugin question is a scoped reconsideration of rejected
  ledger entry IL-20260815-04, registered as IL-20260816-01 (plugins as the
  delivery mechanism for feature seams, never for the scorer, parser, or
  evidence store). The two-shell runtime intent is registered as
  IL-20260816-02 and ties to the Phase 18 packaging conflict already recorded
  in IL-20260815-11.

### 2026-08-16: subtle disclosure polish, hints collapsed by default

> consider suble stuff like collapsing all of the hints originally and more

**Disposition:** Route (2026-08-16).

- Read as: the hint ladder (and similar assistance surfaces) should start
  fully collapsed, with subtle progressive disclosure rather than visible
  stacked tiers; "and more" invites a sweep for sibling refinements of the
  same kind (collapsed session details, quiet secondary controls, disclosure
  that never pre-announces what is behind it).
- Constraint already binding: the ladder must never pre-announce a reveal
  (RTS-09) and tier entitlement stays runtime-owned; collapsing is
  presentation only and cannot change what is served.
- Routed to the Phase 17A visual-system discussion (running 2026-08-16) as a
  named consideration, with 16B's IA contract as the bound: default-collapsed
  assistance, disclosure subtlety, and a pass over existing surfaces for
  "quiet by default" candidates.

### 2026-08-20: paper-note OCR, AI annotation, and note aesthetics

> functionality for notes stuff? consider OCR exiting paper notes, beautifying and highlighting and expanding on stuff and more? does stuff like that exist for digitizing ntoes and stueff? anything for Ai based highlighting and annotating and more? ALso aesthetics too? like papery style vs docs vs other stuff and more? other stuff to consider?

> yes write the inbox entry and reopen B9 and B10, as something to enhance other things, like expanding or adding depth, coreecting and checking understandning and more?

**Disposition:** Split (2026-08-20).

**Promoted 2026-08-21** to `USER-VISION.md` as "2026-08-20: paper notes as a
source, and digitization as an enhancement path". This entry stays here as the
intake record.

**Promotable clause (promoted 2026-08-21):**
the learner's existing paper notes are a first-class source class, and
digitizing them is not the goal in itself. The goal is that a scanned note
becomes something the course can act on: expand it, add depth to it, correct
it, and check whether the learner actually understands what they wrote. This
makes note intake an enhancement path for lessons, practice, and diagnosis
rather than a filing feature.

**Already owned, no new research needed:**

- Highlighting, guided notes, note provenance, note-to-question authority, and
  the note strategy registry (Cornell, outline, matrix, concept map, close
  reading, worked reasoning) are settled in
  `research/phase-16/12-active-annotation-notes.md`.
- "Papery style vs docs vs other stuff" is three separate axes that already
  have owners, and they must not collapse into one theme control: presentation
  theme and tokens in `research/phase-16/10-visual-experience-system.md`;
  instructional style in `RESEARCH-BRIEF-2-lesson-styles-2026-08-10.md` R1
  (the style registry); note format in stream 12 section 10.2. The open
  question already recorded there, which styles are semantic transformations
  versus cosmetic themes, covers this.
- Editor and reader surface patterns are in
  `research/phase-16/16-editor-reader-landscape.md`.

**Routed as new work:** paper-note intake is the one part with no owner. It was
deferred as B9 (image ingestion and OCR) and descoped as B10 (handwriting and
stylus) in `RESEARCH-BRIEF-learning-platform-2026-08-09.md` lines 336 to 337,
and parked again in stream 12 section 10.3. Reopened on this entry as
`IDEA-LEDGER` IL-20260820-01 and IL-20260820-02. Constraints those entries must
respect, all pre-existing: the scan image is the record and the transcription is
derived; transcribe, clean, and expand are three different truth claims and stay
visibly distinct; a learner note never becomes keyed truth (stream 12 section
7.2); AI-proposed highlighting is a reviewable proposal and never color-only
(section 11.1); rights and egress differ between the learner's own handwriting
and a photographed copyrighted page; and the CSCI 1100 AI-use ban applies to
OCR-plus-expansion on that course's notes exactly as it applies to hosted
tutoring.

**Open questions for the eventual research stream:** whether a digitized note
keeps its page identity (image beside transcript, marks preserved) or becomes
clean typeset text by default; how transcription confidence is surfaced so an
uncertain reading is corrected rather than trusted; whether checking
understanding against a learner's own note is a lesson activity, a practice
form, or a diagnostic that must not be scored; how a second scan of the same
page is reconciled rather than duplicated; and whether "rebuild my notes for
objective X from every scan" is the real deliverable rather than transcription.

### 2026-08-21: the completion bar, quality enough to be useful

> What we need is something to finish up itembank to a quality extent to be usefu;l

**Disposition:** Hold (2026-08-22).

Captured from the 2026-08-21 model-budget session, where the surrounding
discussion was provider cost and not product scope. It is recorded here because
the clause is about the product, not the budget: it names a completion bar
("quality extent to be useful") that the record does not currently define
anywhere as the user's own standard.

Held rather than promoted because two existing bars may already cover it and
the overlap has not been resolved. `READINESS-AUDIT-14A.md` A10 defines the
external-user v1 bar, and Phase 13.9 defines the walking-skeleton bar of one
real unit sat end to end. Neither was written as an answer to "useful to
Weibao, daily", which is what this clause appears to mean. Promote it if it
turns out to be a third, learner-facing bar; mark it Duplicate against A10 if
it is not.

### 2026-08-28: be more like the specimen, and a slideshow-with-quiz style

> for stuff like the course,, we should also be more like https://navigate2.jblearning.com/

> maybe slideshow with quiz style as one of the options and more, check out https://navigate2.jblearning.com/pluginfile.php/57822603/mod_scorm/content/7/Shell/main.html if needed

> scrape and odnwload as needed

**Disposition:** Split (2026-08-28).

- **Duplicate half.** "Be more like Navigate2 for the course" restates the
  2026-08-26 statement that produced the teardown and `IL-20260826-01`. It adds
  no new intent on its own, and the existing reading stands: take the treatment
  template and the three level navigation, do not take the plumbing. See
  `.planning/research/2026-08-26-navigate2-teardown.md` sections 3 and 4.
- **New half, and it is product intent.** "Slideshow with quiz style as one of
  the options" names a treatment itembank does not have. Today `teach` is a
  lesson document, a continuous reading surface. A paced, narrated sequence of
  steps with checkpoint questions inside it is a different treatment with a
  different failure mode, and it is the specimen's only evidence bearing rung.
  The word "options" is the load bearing one: it is an addition to the treatment
  set, not a replacement for the lesson.
- **Routed.** The URL was inspected on the same day, with the learner's
  authorization to scrape and download.
  `.planning/research/2026-08-28-navigate2-interactive-lecture-shell.md` records
  what the player is and what a paced mode would owe. Raw structural capture
  stayed out of the repository. Registered as `IL-20260828-01`, with the
  specimen's timed slide lock rejected as `IL-20260828-02`.
- **Promote if:** the paced mode turns out to change what Weibao means by a
  course rather than only how a lesson is presented. It is held here rather than
  promoted because on the current reading it is a presentation of an existing
  durable object, which is a design decision and not a vision statement.

### 2026-08-28: readability, for notes and lesson writing

> for notes and lesson writing, consider readibiltiy and more in the future and more

**Disposition:** Route (2026-08-28), forward-looking, nothing to decide now.

Sent with a screenshot of an ordinary content page from the same specimen deck:
a collapsible panel, one concept in the header, three or four bullets inside,
one level of nesting, about forty words. Recorded in section 1a of
`.planning/research/2026-08-28-navigate2-interactive-lecture-shell.md`.

- **The observation this supports.** The specimen's teaching pages are small and
  chunked, and the checkpoint pages sit at 12, 22, 32 and 38 of 39. Read
  together, the unit of the deck is one concept per screen with a check every
  ten or so. Whatever itembank's paced mode turns out to be
  (`IL-20260828-01`), a lesson written as long continuous prose will project
  into it badly. That is an argument about how lessons are *written*, not only
  about how they are rendered, which is what makes it a note-and-lesson
  question rather than a renderer one.
- **Where it already has an owner.** Adaptive disclosure is named in the
  `CLAUDE.md` course artifact workflow step 6, alongside hover and focus
  definitions. Lesson styles are catalogued in
  `research/2026-08-10-lesson-style-catalogue.md` and
  `research/phase-16/06-feature-style-atlas.md`. The accessibility gates in
  `UI-SPEC.md` already bind anything collapsible: a panel that hides content
  must be keyboard reachable and its state announced, and the plain Markdown
  form has to stay readable with nothing collapsed, per the dual-form rule.
- **What has no owner yet, and is the real content of this entry.** No recorded
  bar says what makes an authored lesson *readable*: chunk size, nesting depth,
  words per step, when a wall of prose should have been a list, when a list
  should have been prose. The linter checks format compliance and item quality,
  not prose readability. Note that a naive readability metric would be worse
  than nothing here, since EMT and Math text is legitimately dense with terms;
  any bar has to survive that.
- **Promote if:** readability turns out to be a quality bar Weibao wants the
  product to enforce or report on, rather than a style preference for whoever
  is authoring. Held short of promotion because the statement is explicitly
  about the future and names no requirement yet.

### 2026-09-06: plans against vision and less future waste

> will the current plans achieve uservision? refine and reduce waste of tokens and more for future

**Status:** routed to `REACH-MILESTONE.md` "Vision alignment refinement,
2026-09-06" and `AGENT-WORKFLOW.md` "Budget and continuation".
The cost preference confirms the 2026-08-21 entry in `USER-VISION.md`.
No duplicate authoritative vision entry is needed. The bounded review tightens
existing acceptance evidence and reading scope without removing features.

### 2026-09-06: feature opportunities and future additions

> features worth considering and more?

> write these down or put as issue, create a prompt to audit this and stuff, looking for stuff 'features worth considering and more'
>
> stuff planned for future, stuff to add on top and more

**Disposition:** Route (2026-09-06) to
`FEATURE-OPPORTUNITY-AUDIT-PROMPT.md` and `IDEA-LEDGER.md` entries
IL-20260906-01 through IL-20260906-05.

**Interpretation:** preserve the five assistant suggestions and prepare a
reusable audit of existing capabilities, future plans, valuable extensions,
and overlooked opportunities. Recording them does not approve implementation.
This extends the existing feature-breadth and expected-omissions direction in
the 2026-08-13 vision entries without duplicating authoritative quotations.
The prompt requires evidence of actual learner flows and retains viable future
ideas beyond the shortlist. Next action: run the saved audit when requested.

### 2026-09-06: SaaS-quality experience in the desktop product

> Consdiering SAAS as an entry point, whatever that means?

> I guess SAAS experience or wahatever thats fitting, I mean the goal will be a electron app or something so I am unsure

> That makes more sense, how can that be combines with current plans and more?

> adjust accordingly, look at the latest audits and more and stuff

**Disposition:** Split and promote (2026-09-06).

The product-intent clauses are promoted verbatim to `USER-VISION.md`. The
request to adjust current plans is routed to `SOURCE-TO-COURSE.md`,
`REACH-MILESTONE.md`, `UI-CHARACTER-AUDIT-2026-09-06.md`, and
`IDEA-LEDGER.md` IL-20260906-07. Electron is treated as an uncertain example,
not a stack decision. The shipped Tauri shell already supplies the desktop
container. The accepted direction is a local-first desktop product with the
coherence and convenience associated with SaaS software. It does not imply
hosted accounts, multi-tenancy, hosted storage, or a subscription business.

### 2026-09-06: comprehensive future UI character

> that UI is alot more better and has more character than mines currently, did we have it in the books to adjust to have more character? we can forget how the ui was prior and improve it comprehensicely in the future accordingly

**Disposition:** Promote and route (2026-09-06).

The product direction is promoted verbatim to `USER-VISION.md`. The planning
effect is routed to `UI-CHARACTER-AUDIT-2026-09-06.md`,
`AUDIT-REMEDIATION-PLAN-2026-09-06.md`, and `IDEA-LEDGER.md`
IL-20260906-08. The current visual appearance is no longer a compatibility
constraint for future comprehensive UI design. Behavioral authority,
accessibility, responsive operation, settings migration, and recovery remain
binding. Syntax Lab is recorded as a useful comparison, not the selected
design or an implementation dependency.

### 2026-09-06: Syntax Lab inspiration and an expandable CS Dojo

> we can even be inspired by 'syntax lab' from diego, incoporate that into a relevant subsection, or as a cs dojo and stuff, it can easily be expanded for other leanguages and more

**Disposition:** Promote and route (2026-09-06).

The product idea is promoted verbatim to `USER-VISION.md`. The bounded
prototype is routed to `AUDIT-REMEDIATION-PLAN-2026-09-06.md` D3.1 and
`IDEA-LEDGER.md` IL-20260906-09. Syntax Lab supplies comparative interaction
evidence. It is not an implementation dependency or authority for scoring,
disclosure, evidence, accessibility, or sandbox behavior.

### 2026-09-06: preserve workflow-efficiency findings

> save these findings for future optimization and workflow for this repo

**Disposition:** Route (2026-09-06).

This is workflow mechanics rather than a product outcome, so it is routed to
`AGENT-WORKFLOW.md` "Proportional workflow" and
`AUDIT-REMEDIATION-PLAN-2026-09-06.md` D0. The recorded conclusion is that GSD
remains valuable for consequential authority, recovery, security, and format
work, while direct execution and bounded evidence-gated packets become the
default for reversible settled tasks. The structural counts are preserved as a
baseline and are not described as measured token consumption.

### 2026-09-06: shorten idle time and match focused prototype velocity

> do that accordingly, also how can things be sped up, since we are wasting too much time in betwee n andd more? considering Code\_learner was able to achieve a subfeature so much faster and of higher quality than what we spent so long on prior

**Disposition:** Route (2026-09-06).

This is a request to change execution mechanics, not a new learner-facing
feature. It confirms the earlier cost and useful-product direction and is
routed to `AGENT-WORKFLOW.md`, `AUDIT-REMEDIATION-PLAN-2026-09-06.md`,
`REACH-MILESTONE.md`, the active 19A context, and the 19D seed. The
`code_learner` comparison is evidence that a focused, coherent vertical
prototype can expose value faster than a long sequence of component plans. It
does not adopt that repository's client-owned scoring, disclosure, evidence,
dependency, or maintenance choices. The planning effect is to require an early
visible slice, bounded planning time, one active writer, and escalation only
after an observable gate fails or a named consequential decision appears.

### 2026-09-06: prioritize UI and app-quality repairs

> do that accordingly, prioritize important stuff like UI and app stuff fix and more,

**Disposition:** Promote and route (2026-09-06).

The request confirms that visible product coherence and app usability should
come before more invisible breadth when both are ready. The product priority is
promoted through the existing SaaS-quality desktop and comprehensive UI
entries in `USER-VISION.md`, without duplicating their quotations. The current
execution effect is routed to `AUDIT-REMEDIATION-PLAN-2026-09-06.md`,
`REACH-MILESTONE.md`, and `STATE.md`: run the bounded R5 course-shell and
first-use journey repair before 19A-06. This does not authorize the full future
visual redesign inside Reach and does not weaken scoring, disclosure, recovery,
accessibility, or accepted-write gates.

### 2026-09-06: close every audit route and allow better UI replacements

> keep in mind the audit findings and make sure everything will be addressed, making sure our future UI is modern and fitting and that anything old can be replaces if there are better/more fitting options and more

**Disposition:** Promote and route (2026-09-06).

The product direction is promoted verbatim to `USER-VISION.md`. The execution
effect is routed to `UI-CHARACTER-AUDIT-2026-09-06.md`,
`AUDIT-REMEDIATION-PLAN-2026-09-06.md`, and `REACH-MILESTONE.md`. Every audit
finding must retain a disposition, owner, trigger, and acceptance evidence.
Future UI work judges existing components by fitness for the accepted course
experience rather than age or compatibility with the current appearance.
Replacement remains subject to behavior, accessibility, migration, and
recovery gates.

### 2026-09-06: preserve design-language uncertainty for later comparison

> save and adjust accordingly, we are unsure and we can establish better in the future

**Disposition:** Promote and route (2026-09-06).

The uncertainty is intentional product direction and is promoted verbatim to
`USER-VISION.md`. The comparison and future selection gate are routed to
`UI-CHARACTER-AUDIT-2026-09-06.md` and the consolidated remediation plan.
Current Reach repairs may establish shared usability primitives, but they must
not silently select the final visual language.

### 2026-09-06: scope Monkeytype inspiration to coding

> monkey type's ui design was the intended insiration for code sstuff, we just need good design language and more and stuff

**Disposition:** Promote and route (2026-09-06).

This corrects the prior interpretation. Monkeytype belongs to the CS Dojo and
coding-practice reference set, not the app-wide design-language comparison.
The correction is promoted verbatim to `USER-VISION.md` and applied to
`UI-CHARACTER-AUDIT-2026-09-06.md` and the remediation plan. The broader design
language remains open and must fit the complete learning product.

### 2026-09-06: use Terra for the comparable UI prototypes

> okay save accordingly, use terra to show the 3 to me

**Disposition:** Route (2026-09-06).

This selects execution mechanics rather than a product direction. Terra at
medium owns the first comparable HTML and CSS prototype set for the editorial
learning studio, modern learning workspace, and reading-and-doing workshop.
The prototypes use identical content and states and remain throwaway review
artifacts. User review, not the builder, selects or combines a direction.

### 2026-09-06: strengthen the prototypes toward a technical instrument

> all of them feels a little weak, I want a techy feel like monkey type or something else, update accordingly?

**Disposition:** Promote and route (2026-09-06).

The product-direction correction is promoted verbatim to `USER-VISION.md` and
routed to the UI character audit and the next prototype pass. The desired
app-wide quality is a deliberate technical-instrument feel, not a copy of
Monkeytype's typing-test composition. Monkeytype remains the strongest direct
reference for CS Dojo, while the shared system may borrow its restraint,
precision, keyboard confidence, and visible state.

### 2026-09-06: retain both finalists through one adaptable foundation

> Okay [Measured field guide](/Users/weiwei/.codex/worktrees/d78d/itembank/prototypes/17c-finalists/field-guide.html)
>
> 1. [Learning trajectory deck](/Users/weiwei/.codex/worktrees/d78d/itembank/prototypes/17c-finalists/trajectory-deck.html)
>
> Those two are the most fitting, we can keep both? Make method to setup base stuff and make it easy to adapt or implement skills in the future? other stuff to consider?

**Disposition:** Promote and route (2026-09-06).

The selection is promoted verbatim to `USER-VISION.md`. Both finalists are
retained as compositions over one semantic design foundation, not independent
frontends. The method, extension contract, migration sequence, and verification
gates are owned by `UI-CHARACTER-AUDIT-2026-09-06.md`. Stable copies of the
selected prototypes live under `prototypes/17c-finalists/` in this checkout.

### 2026-09-06: make both finalists switchable profiles

> so both can be kept as a switchable theme or something, save and update things accordingly? more to consider

**Disposition:** Promote and route (2026-09-06).

The choice is promoted verbatim to `USER-VISION.md`. Both finalists become
user-switchable presentation profiles over identical semantic content and
state. They are distinct from color themes, contrast modes, and accents. The
settings, migration, preview, fallback, and capability-extension contract is
owned by `UI-CHARACTER-AUDIT-2026-09-06.md` and the binding product contract.

### 2026-09-06: DSH extension comparison and bounded implementation plans

> is current structure similar to DSH [https://github.com/deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness) where we can add things or adjust things accordingly like plugins and more?

> if that makes it more optimal create plans that a lesser agent can act upon to implement and more

**Disposition:** Route (2026-09-06).

This revisits the existing IL-20260816-01 named-seam plugin direction and asks
for executable planning mechanics. It does not replace the product vision or
authorize a swappable scorer. The conditional benefit assessment, one detailed
packet, and follow-on seeds live in `EXTENSION-DELIVERY-2026-09-06.md` and
`EXT-01-PLAN.md`. Implementation remains unrun. External packages retain their
own supply-chain and isolation design gate.

### 2026-09-07: make the complete UI adaptable through extensions and themes

> for UI 2, we can have the UI designs be implemented extension/theme style, for everything and anything can be updated or adjusted as extension accordingly? thoughts? Plug other parts in accordingly and more, then create a prompt to continue work

**Disposition:** Promote and route (2026-09-07).

The product intent is promoted verbatim to `USER-VISION.md`. The implementation
direction is routed to `SOURCE-TO-COURSE.md`, the UI character audit, the
extension-delivery contract, and `IDEA-LEDGER.md`. Presentation profiles,
appearance themes, capability adapters, and integration adapters become named
extension seams over shared semantic contracts. This does not make canonical
content, scoring, evidence, permissions, or recovery replaceable plugins. The
continuation packet is `PROMPT-EXTENSIBLE-UI-CONTINUATION-2026-09-07.md`.

### 2026-09-07: compare home presentations and complete the UI flow research

> like right now its like this, and I assume it can be sectioned better somehow but Im not sure how, can we look accross existing learning platforms and LMS and more and scope improvements?

> unsure, we can have multiple options and implement all of them and have the user decide what they like instead, look accross sites and more and scope accordingly

> Save accordingly also need to consider UI flow, from returning to home/finishing exam/quiz and more,&#x20;
>
> Combine prior audits and new findings, make prompt to look further, also looking at githubs and repos and more, and then make sure we can absorb everything and more and address everything

> re research in case of new info and more in the future

**Disposition:** Promote and route (2026-09-07).

The product intent is promoted verbatim to `USER-VISION.md`. The screenshot
observation, current platform comparison, four reversible home projections,
transition-complete matrix, repository leads, and re-research triggers are
routed to `notes/2026-09-07-home-and-transition-ui-scope.md`. The reusable
research packet is `PROMPT-UI-FLOW-AND-OPEN-SOURCE-ABSORPTION-2026-09-07.md`.
The four home projections remain prototypes until comparative user review.
Complete navigation, stop, finish, return-home, post-assessment, resume,
interruption, and recovery behavior is Core and extends existing FLOW, APP, and
UI-audit obligations. External repositories are evidence sources, not
authorization to copy or vendor code.

### 2026-09-07: a learning harness for people, operated by AI

> should we consider itembank a learning based harness for ai in the future? or just keep it as is as something agentically driven?

> okay write that down accordingly

**Disposition:** Promote and route (2026-09-07).

The product identity is promoted verbatim to `USER-VISION.md`. The binding
interpretation is routed to the north star in `SOURCE-TO-COURSE.md`, and the
capability disposition is recorded as IL-20260907-03 in `IDEA-LEDGER.md`.
Itembank is a learning harness for people that AI can operate and extend. It is
not primarily an AI-training or general model-evaluation harness. Adjacent
AI-facing uses remain eligible as registered capabilities when they serve the
learner-centered system and pass its existing authority, rights, validation,
inspectability, and recovery gates.

### 2026-09-08: acquire transcripts, Canvas course material, and other sources

> extend itembank capability to scrape and download or absorb transcripts by providing tools like canvas stuff downloader and more, we can also audit other stuff to consider and more, and imprvoements for that repor or other lacking extention features

**Disposition:** Promote and route (2026-09-08).

The source-acquisition outcome is promoted verbatim to `USER-VISION.md`.
Implementation choices and the gap audit are routed to
`SOURCE-ACQUISITION-EXTENSION-AUDIT-2026-09-08.md`. The audit separates the
existing transcript and single-page web adapters from the missing authenticated
Canvas course acquisition layer. It registers a Canvas export prototype, a
live Canvas API integration, local ASR, and later LMS targets without expanding
the active Reach milestone.

### 2026-09-08: defer local AI and skip the sitting for now

> we can skip the sitting for now

**Disposition:** Promote and route (2026-09-08).

The scope decision is promoted verbatim to `USER-VISION.md`. Its execution
effect is routed to `STATE.md`, `REACH-MILESTONE.md`, `REACH-CLOSURE-INDEX.md`,
the Phase 19D records, and `IDEA-LEDGER.md`. The representative Math 1400
sitting is deferred rather than treated as completed. Runtime scoring,
disclosure, session, and evidence authority remain unchanged.

### 2026-09-08: feedback must pause before the next item, and the UI needs reconciliation

> it should show correct and should remain in the same page before moving onto the next, Im not going to lie the UI looks same, and right now it says item 3 of 2, there are many things to adjust accordingly? Save to problems list accordingly(makeing that a new skill too like uservision)

> make a prompt to make sure UI gets looked trhough, audit of the piror audits got actually implemented and more, and also, the UI looks the same as before

> we might need to make new profiles as defaults, consider purging old ones and more

**Disposition:** Split and route (2026-09-08).

The direct learner reports, separately labeled diagnoses, and closure evidence
are recorded in `PROBLEM-LEDGER.md` as P-20260908-01 through P-20260908-03.
The feedback repair remains presentation-only and preserves runtime scoring,
disclosure, session, and evidence authority. The self-contained audit packet is
`PROMPT-PHASE-20-UI-IMPLEMENTATION-AUDIT-2026-09-08.md`. Replacing, changing
the default, or removing a profile remains an explicit Weibao decision after a
comparative prototype and migration proposal.

### 2026-09-08: reader definitions and external documents

> future reader should have the option of double clicking for definition and more, be able to work with external slides/pdf/epub and more?

**Disposition:** Promote and route (2026-09-08).

The reader outcome is promoted verbatim to `USER-VISION.md`. The exact
double-click behavior is routed to a reversible interaction prototype because
it must coexist with text selection and have equivalent keyboard, touch, and
screen-reader actions. External PDF, EPUB, and slide use routes through the
existing source-adapter, binding, rights, citation, and recovery contracts.
The first meaning of "work with" is open, navigate, cite, bind, annotate, and
launch relevant course treatments alongside the source. Editing or round-trip
export of each proprietary format remains an open question rather than an
implied commitment.

### 2026-09-08: competitor scope and selective generation absorption

> scope all the competitions, absorb stuff and more, you can run through the experience, and also using [$efficient-agent-routing](/Users/weiwei/Documents/Dev/agent-skills/skills/efficient-agent-routing/SKILL.md) check out everything and then absorb properly

> maic seems inefficient for what we need, we can absorb the lesson generation and more, but we dont need the extra stuff like multiple sub agents and more and stuff, look at uservision and absorb what should be absorbs

**Disposition:** Split, promote, and route (2026-09-08).

The product direction is promoted verbatim to USER-VISION.md under selective generation absorption. The broad research and routing request belongs to `research/competition-2026-09-08/ABSORPTION.md`, which reconciles the landscape, hands-on trials, actual prototype adoption, exclusions, and remaining gates. Classroom agent multiplicity is not a requirement for lesson generation.

### 2026-09-08: interactive visual teaching without conversation

> we can absort the interactiveness, small slight, bright text highlighting and other stuff and more, just without the conversational stuff and stuff

**Disposition:** Promote and route (2026-09-08).

Promoted verbatim to USER-VISION.md. IL-20260908-06 and `research/competition-2026-09-08/ABSORPTION.md` preserve interactive treatments and bright highlighting separately from excluded conversational staging. Subtle motion is an interpretation to evaluate, not an invented exact requirement.

### 2026-09-08: absorb LiaScript and the wider platform landscape

> what about the highlights from lia script and other stuff and more? also make those absorbed and more

> other platforms and more as well

**Disposition:** Promote and route (2026-09-08).

Promoted verbatim to USER-VISION.md. The existing competition ABSORPTION.md owns implementation evidence and the full landscape. IL-20260908-07 extends absorption beyond OpenMAIC and LiaScript. Broad intent does not mean every surveyed runtime or institutional feature must be installed.

### 2026-09-09: UI scope and an auditable project history

> consider these projects and if there is any thing we caan learn form them

> both, I still feel like our UI isnt the best it cant be but idk how to scope it, also how can we organize our prior ideas and audits and more into one progressive timeline and ideaboarding surface that can be audited and reflected upon in the future without being biased by existing work?

**Disposition:** Split, promote, and route (2026-09-09).

The second statement is promoted verbatim to `USER-VISION.md`. Synapse and seer
are research references from the screenshot, not instructions or accepted
product designs. `research/ui-and-project-memory-proposal-2026-09-09.md` owns
the comparison, proposed UI scope, history surface, and evidence limits.
IL-20260909-01 through IL-20260909-05 retain the candidate routes.

### 2026-09-09: fresh evaluation of prior choices in future audits

> also note for future audits dont be swayed by prior choices cause it might have been the best at the time but there could always be better

**Disposition:** Promote and record as standing audit guidance (2026-09-09).

Promoted verbatim to `USER-VISION.md`. `AGENT-WORKFLOW.md` section 10 records
current-needs comparison, the distinction between design fitness and switching
cost, contrary evidence, and revisit conditions. Prior acceptance remains part
of the history rather than proof of current superiority.

### 2026-09-10: figure-derived questions, chapter tiers, source wisdom, and paper notes

> make question type that converts figures/tables from books into fill in the blank/drag and drop

> Combineing similar chapters into groups aand make them into tiers?

> Absorvbing words of wisdom(from emt books and stuff)&#x20;

> digitalizing paper notes?

**Disposition:** Promote, route, and duplicate (2026-09-10).

The first three statements are promoted verbatim to `USER-VISION.md` as new
product-direction ideas. Figure and table conversion routes to a reversible
item-format and authoring prototype. Chapter grouping and tiers route to course
and objective-graph research because the meaning of a tier is still open.
Source wisdom routes to source-grounded lesson and note treatment research.

The paper-note statement is promoted as a confirmation of the existing
2026-08-20 vision entry, not as a second source class. IL-20260820-01 and
IL-20260820-02 remain its implementation route. IL-20260910-01 through
IL-20260910-03 record the new proposals without scheduling them.

### 2026-09-10: reading prototype must match the accepted UI and project benchmark

> This prototype looks nothing like the new design style and more? Nothing UI com prejensive compared to the github projects and more

**Disposition:** Promote and route (2026-09-10).

Promoted verbatim to `USER-VISION.md`. This is a correction to the
source-to-reading prototype, not a request for surface polish. The replacement
must use the accepted greenfield learner identity and test a comprehensive
course experience against the capabilities already selected from public
project research. `SOURCE-TO-READING-IMPLEMENTATION-PLAN-2026-09-10.md` owns
the corrective implementation and verification.

### 2026-09-10: rebuilt reading prototype is fitting enough to continue

> alot better, room to improve in the future but this is more fitting accordingly

**Disposition:** Promote and route (2026-09-10).

Promoted verbatim to `USER-VISION.md`. This accepts the rebuilt direction as a
fitting continuation baseline. It does not certify final aesthetics,
accessibility, production integration, or every future UI detail. The
source-to-reading plan and handoff retain those open gates.

### 2026-09-11: source reproduction choice and deferred prototype review

> "does not reproduce the original figure, source dialog, or label-placement experience. " Reproducing is fine... but that should be something deferred to the user as a choice or osmething,&#x20;
>
> "Human touch, screen-reader, zoom, visual approval, real-course comparison, and format acceptance remain open."
>
> will be hard to test for now so just defer to future for the others accordingly, work on next part

**Disposition:** Split, promote, and route (2026-09-11).

Promoted to [the matching vision entry](USER-VISION.md#2026-09-11-source-reproduction-choice-and-deferred-prototype-review).
Reproduction is a permitted user choice within the source rights in force.
The named review legs are deferred for this prototype chain while further
synthetic work continues. IL-20260910-01 retains the interaction proposal and
the deferred review owner and trigger. The learning-treatment prototype owns
execution and reports what is tested separately from future acceptance.

### 2026-09-11: diagram placement and selectable answer banks

> for the diagram, drag and drop might be better, and also, always give option of word bank? Or at least, since NREMT stuff always have bank (I think) might need double check

**Disposition:** Promote and route (2026-09-11).

Promoted to [the matching vision entry](USER-VISION.md#2026-09-11-diagram-placement-and-selectable-answer-banks).
IL-20260910-01 retains diagram placement and optional teaching answer banks as
one prototype route. The uncertain NREMT premise routes to the
[exam-fit review](../prototypes/learning-treatments/runtime-candidate/EXAM-FIT-REVIEW.md).
It is not promoted as a fact about every credential or examination.

### 2026-09-11: orient learning and practice to the actual examination

> put into uservision accordingly as well, for stuff to be oriented accordingly to the exam and what will be tested and more?

**Disposition:** Promote as a clarification of existing direction (2026-09-11).

Promoted to [the matching vision entry](USER-VISION.md#2026-09-11-orient-learning-and-practice-to-the-actual-examination).
This confirms the August 24 examination-fidelity principle and existing
[assessment intake](../.claude/skills/ASSESSMENT-INTAKE.md).
Core objectives and necessary support guide the default path. Broader learning
and enrichment remain explicit choices. IL-20260910-01 applies that direction
to the current figure and table prototype without creating a second exam-policy
authority or a duplicate concept.

### 2026-09-12: thematic quiz environments and fluid interaction

> I had an idea that each quizzing enviorment can be thematic in a way, like the Code learner style for dode, and standard style for multiple choice and more? but more fluidity and better UI and UX

**Disposition:** Promote and route (2026-09-12).

Promoted verbatim to [the matching vision entry](USER-VISION.md#2026-09-12-thematic-quiz-environments-and-fluid-interaction).
[IL-20260912-02](IDEA-LEDGER.md#il-20260912-02-thematic-quiz-environments-and-fluid-interaction)
retains this as a Prototype proposal. Code Learner and standard multiple choice
are the user's examples. Other candidate environments and selection behavior
remain interpretations to compare. The route extends the existing presentation
and CS Dojo work without scheduling implementation or claiming UX acceptance.

### 2026-09-12: code boxes that reinforce syntax and structure

> also for stuff like "What does this code print? `temperature = 72; raining = True; if temperature >= 70 and not raining: print("walk"); else: print("bus")`"
>
> Mkae it show in a code box so I passively learn semantics and streucture as well, put that into uservision

**Disposition:** Promote as a concrete presentation preference (2026-09-12).

Promoted verbatim to [the matching vision entry](USER-VISION.md#2026-09-12-code-boxes-that-reinforce-syntax-and-structure).
The existing IL-20260912-02 route owns code boxes for prediction questions,
with valid syntax, indentation and line breaks. The vision entry records the
current CSCI snippet correction and renderer checks. This is a recorded
requirement, not a claim that the quiz or its content has been repaired.

## Disposition vocabulary

- **Promote:** add the verbatim statement and interpretation to `USER-VISION`.
- **Route:** preserve here and link to its research, decision, requirement, or
  operational owner.
- **Split:** promote the product-intent clauses and route the implementation or
  task clauses.
- **Hold:** keep unresolved until more ideaboarding or research changes its
  meaning.
- **Duplicate:** link to the earlier vision statement it restates without
  adding another authoritative copy.
