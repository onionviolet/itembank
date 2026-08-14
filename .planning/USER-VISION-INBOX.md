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
