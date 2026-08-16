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
