# 16. Editor and reader product landscape (experience layer)

**Status:** research record, bounded wave, written 2026-08-14.
**Scope boundary:** the editor architecture is already decided and out of scope
here (CodeMirror 6 in-app, external-editor-in-place as a peer, server-textarea
floor). This file mines what shipping editor and reader products get right and
wrong as writing and reading experiences, and maps the transferable patterns to
itembank subphases. Nothing here reopens the architecture decision.

Labels used throughout: **[web]** for a claim sourced from web research (with a
URL), **[synthesis]** for this file's own interpretation or mapping.

---

## 1. Scope and method

Searched 2026-08-14 via web search and page fetches. Products studied: Ellipsus
(drafts, branching, version history), Notion (block model), Obsidian (live
preview versus source mode), iA Writer (focus modes, syntax highlight, style
check), Typora (seamless WYSIWYM rendering), Scrivener (snapshots and roll
back), Google Docs (suggesting mode), Bear (hybrid rendering, typography),
GitBook (change requests and diff view). Sources were vendor documentation,
vendor help centers, product reviews, and user-forum discussions. Marketing
claims were cross-checked against help documentation where possible; where only
the vendor's description exists, that is noted.

Binding frame carried from prior phase-16 work: reading scrolls and never
paginates; no compelled learner highlighting (author emphasis only); worked
example before definition as default lesson order; retrievability never shown as
a percentage; Socratic refusal renders as a locked card, not chat. The Ellipsus
pattern is evaluated strictly as a thin UI over the 14A revision and
operation-journal model, never as a second history system.

---

## 2. Per-product findings

### 2.1 Ellipsus

**What it gets right [web].** Ellipsus separates a document (the main version)
from drafts, which are "distinct branches contained inside of that document."
A draft is a full copy of the document at creation time; it does not
auto-update from the main document or from other drafts, and editing it never
touches the main document. Drafts never have to be merged back; they can live
forever as alternates. There is no limit on draft count. Version history shows
a timeline of writing sessions, grouped by date, expandable to timestamped
individual versions; viewing the main document's history also shows when
specific drafts were merged. Compare shows a draft alongside the main document
side by side before merging.
Sources: https://help.ellipsus.com/support/solutions/articles/205000067235-understanding-documents-and-drafts ,
https://help.ellipsus.com/support/solutions/articles/205000067329-version-history ,
https://ellipsus.com/features

**What it costs [web/synthesis].** A draft is a whole-document copy, so
divergence is coarse: two drafts that each change one different paragraph still
read as two full alternate documents, and the writer carries the merge burden
mentally. The help material documents that compare and merge exist but not how
conflicts inside a merge are resolved, which suggests the merge is
last-writer-chooses rather than structural [synthesis]. Sessions-as-versions
grouping is friendly but opaque about what counts as a session boundary.

**What transfers [synthesis].** The framing transfers almost perfectly to
itembank's accepted-file plus revision model: the accepted canonical file is
the "document," a pending revision is a "draft," acceptance is the "merge,"
and the operation journal is the "version history." What must not transfer is
the storage: Ellipsus owns its history in-app, and itembank must render its
existing journal instead. Section 4 details the requirements.

### 2.2 Notion

**What it gets right [web].** The block model gives a uniform manipulation
grammar: every unit of content (text, image, list item, database row) is a
block, and one slash menu inserts anything. This buys composability and a flat
learning surface for insertion.
Sources: https://www.educative.io/blog/why-is-notion-so-slow (system design
context), https://clickup.com/learn/topic/productivity/tools/notion/ ,
https://hackceleration.com/notion-review/

**What it costs [web].** Every block is its own stored row, and pages heavy
with blocks or embeds load slowly (reviewers report 3 to 5 seconds on pages
with many database blocks). The slash menu presents "a long scroll of options"
that confuses at first. Mobile editing of nested block layouts is described as
frustrating, with constant wrong-block taps.
Sources: https://falconer.com/guides/why-is-notion-slow/ ,
https://hackceleration.com/notion-review/ ,
https://thebusinessdive.com/notion-review

**What transfers and what does not [synthesis].** The lesson for itembank is
mostly negative and therefore valuable: long-form reading does not want a
block-per-paragraph object model. Itembank's D-14A-2 resolution (component IDs
only for cited, gated, or evidence-bearing blocks, not one ID per paragraph)
is independently validated by Notion's cost profile. What does transfer is the
single-entry-point insertion idea: one small, well-curated insert affordance
beats a toolbar, provided the menu stays short. A slash menu with seven
curated lesson roles is a different product from a slash menu with ninety
block types.

### 2.3 Obsidian

**What it gets right [web].** Three explicit modes: source mode (raw Markdown,
fastest typing), live preview (rendered text with syntax revealed only around
the cursor), and reading mode (fully rendered, no editing affordances). Live
preview is positioned as "preview your notes in the same view that you're
writing them in." The file on disk stays plain Markdown regardless of mode, so
the document survives every mode and every other tool.
Sources: https://help.obsidian.md (via forum summaries),
https://forum.obsidian.md/t/live-preview-and-reading-mode-are-very-different/87552 ,
https://huggingface.co/spaces/anpigon/obsidian-qa-bot/blob/main/docs/obsidian-help/Live%20preview%20update.md

**What it costs [web].** Users report real confusion about how the three modes
and their UI toggles relate, and that live preview and reading mode can render
the same note visibly differently, which undermines trust in "what will the
reader see."
Sources: https://forum.obsidian.md/t/i-totally-get-source-mode-view-mode-live-preview-i-totally-don-t-get-the-corresponding-ui-elements-and-how-they-work-together/76293 ,
https://forum.obsidian.md/t/live-preview-and-reading-mode-are-very-different/87552

**What transfers [synthesis].** Itembank already commits to dual-form lessons
(coherent plain Markdown plus a richer itembank presentation), which is the
same shape as Obsidian's source versus reading split. The transferable
warning: the two renderings must not drift. Itembank's advantage is that the
rich presentation is server-rendered from the same parse, so drift is a bug
class the roundtrip tests can catch, where Obsidian structurally cannot. The
transferable positive: name the modes plainly, keep the toggle in one place,
and make the learner-facing default reading mode, with editing modes reachable
but never ambient.

### 2.4 iA Writer

**What it gets right [web].** Focus mode highlights the current sentence or
paragraph and fades everything else, with sentence, paragraph, and typewriter
variants. Syntax highlight marks parts of speech (adjectives, adverbs, fillers)
to expose style habits. Style check flags fillers, cliches, and redundancies
but deliberately does not auto-correct: "Style Check doesn't tell you what's
right; it encourages you to rethink your choice of words, and you decide."
Typography is a single, opinionated, excellent default rather than a theme
gallery.
Sources: https://ia.net/writer ,
https://ia.net/writer/support/editor/syntax-highlight ,
https://ia.net/writer/how-to/edit-and-polish

**What it costs [synthesis].** The discipline is the product: no layout
control, minimal structure tooling, weak fit for reference documents with
tables, callouts, and figures. It optimizes drafting flow over document
assembly.

**What transfers [synthesis].** Two things. First, the advisory-not-corrective
stance of style check is exactly the relationship itembank's linter already has
with authors (actionable messages, author decides), and it should stay the
stance for any future prose-quality signals in lesson authoring. Second, one
excellent reading typography beats configurable theming for a one-learner
product; this is a 17A input. Focus mode itself is an authoring nicety, not a
learner-surface need, and rides the CodeMirror decision at near-zero cost if
ever wanted.

### 2.5 Typora

**What it gets right [web].** The single-pane WYSIWYM model: Markdown syntax
disappears as you type, headers render as headers, no mode switcher, no
preview pane. Reviewers consistently call it the most seamless Markdown
writing experience available and note it "makes Markdown feel like a word
processor."
Sources: https://typora.io/ ,
https://www.markdown-to-word.online/markdown-editors-comparison/ ,
https://www.technary.com/software/typora-review-a-minimalist-markdown-editor-that-just-works/

**What it costs [web/synthesis].** No sync, no organization layer, no mobile
[web: https://makerstack.co/reviews/typora-review/ ]. More fundamentally for
itembank, fully hiding syntax hides the contract: an author of keyed
assessment content needs to see exactly what the parser will see, because an
invisible formatting character can change scoring-relevant bytes [synthesis].

**What transfers [synthesis].** Seamlessness as a target for the lesson
reading surface, not the authoring surface. The learner reading a lesson
should never see Markdown; the author editing keyed content should always be
able to. That is Obsidian's mode split with Typora's polish target, and it is
already compatible with the decided CodeMirror architecture.

### 2.6 Scrivener

**What it gets right [web].** Snapshots are per-document, cheap, and manual: a
writer takes a named snapshot before a risky revision. Compare highlights
changes between snapshot and current text at three levels of granularity.
Roll Back restores a snapshot, and before destroying the current text
Scrivener offers to snapshot it first, so roll back is itself non-destructive
by default.
Sources: https://www.literatureandlatte.com/blog/how-to-manage-compare-and-restore-snapshots-in-your-scrivener-projects ,
https://www.literatureandlatte.com/blog/use-snapshots-in-scrivener-to-save-versions-of-your-projects

**What transfers [synthesis].** The "snapshot before destructive action, offer
to snapshot the thing you are about to destroy" reflex is exactly itembank's
compare-and-swap plus journal contract expressed as UX. The transferable
detail is the prompt shape: the safe path is the default and the destructive
path narrates its own escape hatch. Per-document (not per-project) granularity
also matches itembank's per-artifact revision unit.

### 2.7 Google Docs suggesting mode

**What it gets right [web].** Proposed changes render inline in the document,
in a distinct color, with each suggestion carrying a margin card and a binary
accept (check) or reject (x) control; bulk accept and reject exist but
per-suggestion review is the primary flow. The document owner, not the
suggester, controls incorporation.
Sources: https://support.google.com/docs/answer/6033474 ,
https://pupuweb.com/google-docs-suggested-edits-changes-mode-accept-reject/

**What transfers [synthesis].** This is the reviewer-acceptance interaction
itembank's 15B accepted-revision step needs: an agent's proposed revision
should render as inline-visible proposed changes with per-change accept and
reject, not as a wall-of-text replacement to eyeball. The bounded-diff
requirement in the operation protocol already demands the data; suggesting
mode shows the interaction that makes a bounded diff reviewable. What does not
transfer: real-time co-editing and comment threads as chat; itembank review is
asynchronous and single-reviewer.

### 2.8 Bear

**What it gets right [web].** A hybrid editor that shows Markdown syntax and
its rendered effect simultaneously (syntax stays visible but styled), praised
for the best default typography in the category and for notes that are "easy
to scan, revise, and reuse."
Sources: https://www.markdownguide.org/tools/bear/ ,
https://saas-tools.medium.com/best-mac-markdown-editors-2026-i-tested-9-ive-already-switched-twice-8f915221644c ,
https://randsinrepose.com/archives/bear-an-elegant-combination-of-design-whimsy-and-voice/

**What transfers [synthesis].** Bear demonstrates a third rendering point
between Obsidian's source mode and Typora's full concealment: syntax visible
but typographically subordinated. For itembank's authoring surface over keyed
content, this is the right default: the contract characters stay on screen,
styled quiet, so what the parser sees is never hidden. A 17A typography
concern and a CodeMirror decoration concern, both cheap.

### 2.9 GitBook change requests

**What it gets right [web].** A change request "creates a copy of your content
at that specific moment in time, sometimes called a branch"; changes stay out
of main content until merged; diff view "highlights everything that's new,
changed or deleted"; concurrent change requests are guided through conflict
resolution before merge; merging creates "a new entry in the space's version
history."
Sources: https://gitbook.com/docs/collaboration/change-requests ,
https://www.gitbook.com/blog/what-is-diff-mode ,
https://www.gitbook.com/blog/make-your-documentation-process-more-collaborative-with-change-requests

**What transfers [synthesis].** GitBook proves the Ellipsus pattern scales to
structured documentation with an explicit diff and an explicit merge-conflict
gate, which is closer to itembank's needs than Ellipsus's fiction-oriented
side-by-side. The conflict gate maps directly to itembank's rule that a
same-ID, divergent-bytes case is a conflict and never a silent overwrite. What
does not transfer: GitBook's team-review ceremony (approvals, reviewers,
notifications) is multi-tenant weight a one-learner product does not carry.

---

## 3. Cross-cutting patterns ranked by transfer value

Ranked highest transfer value first. All entries are [synthesis], built on the
sourced findings above. Owner subphases: 14A revision UI, 15B acceptance, 16A
lesson capability, 16B IA and flow, 16C notes and strategies, 17A visual
system.

1. **Draft-as-branch over an accepted document, with named drafts, side-by-side
   compare, explicit merge, and merges visible in history** (Ellipsus, GitBook).
   Owner: 14A revision UI for the model surface, 15B for acceptance semantics.
   The single highest-value pattern; detailed as requirements in section 4.
2. **Per-change accept and reject over an inline-rendered proposed revision**
   (Google Docs suggesting mode, GitBook diff view). Owner: 15B, with the
   rendering owned by the 14A revision UI. This is the shape the operation
   protocol's "present a bounded diff, pass configured review" step should
   take on screen.
3. **Snapshot-before-destruction as the default prompt shape** (Scrivener).
   Owner: 14A revision UI, and 16B for the recovery-state storyboard. Every
   destructive-looking action narrates the safe path first and offers to
   preserve what it replaces; itembank's journal makes this nearly free.
4. **Reader mode is fully rendered and mode switching is explicit, named, and
   in one place** (Obsidian's clarity failure as the cautionary case, Typora's
   seamlessness as the reading target). Owner: 16B for the mode model and
   routes, 17A for the rendering polish. Learner default is reading mode;
   editing modes are reachable, never ambient.
5. **Syntax visible but typographically subordinated when editing keyed
   content** (Bear). Owner: 17A tokens plus the already-decided CodeMirror
   layer. Never fully conceal contract characters in assessment-bearing files.
6. **One short, curated insert menu instead of a toolbar or a long block
   gallery** (Notion's slash menu, minus its overload). Owner: 16A defines the
   short list (lesson roles, callout, worked example, figure, term), 16B
   places the affordance.
7. **Advisory style signals that never auto-correct** (iA Writer style check).
   Owner: 16A for any lesson-prose quality signals; consistent with the
   existing linter stance. The tool points, the author decides.
8. **One excellent reading typography rather than a theme gallery** (iA
   Writer, Bear). Owner: 17A. A one-learner product spends its budget on one
   superb default plus the accessibility-mandated variants (contrast, zoom,
   reduced motion), not on theming.
9. **Focus and typewriter modes for drafting** (iA Writer). Owner: none now;
   rides the CodeMirror decision as a cheap registered extension if authoring
   in-app ever becomes a primary flow. Low value while most authoring is
   agent-drafted and human-reviewed.

---

## 4. The Ellipsus pattern in depth: requirements on the 14A model

Frame [synthesis]: the branching-drafts, history, and diff experience is a
THIN UI over the already-planned 14A objects (opaque durable IDs with
fingerprints per D-14A-2, compare-and-swap writes, the append-only operation
journal, accepted-revision objects per 15B). The UI reads those objects and
issues those operations. It must not mint its own version numbers, keep its
own edit log, or store draft state anywhere the journal and revision objects
cannot reconstruct. If the UI needs a fact the model cannot answer, the fix is
a model requirement, not a UI-side cache of history. These are the
requirements the experience imposes on the model, checked against
DECISIONS-PRE-14A-2026-08-14.md and the 14A row of ROADMAP.md:

- **R1. Draft is a first-class pending revision of one identified object.** A
  draft is a revision object carrying the parent object's opaque ID, the base
  fingerprint it was copied from, a human-assigned name, and a created
  timestamp. Ellipsus shows names and independence matter; GitBook shows the
  base-point matters. 14A's link/import/copy/move/supersede vocabulary needs
  "open draft revision" to be one of its distinguishable states, not a loose
  file copy.
- **R2. The base fingerprint makes staleness computable.** The UI must be able
  to say "the accepted document changed after this draft was taken" by
  comparing the draft's base fingerprint with the current accepted
  fingerprint. This is already implied by compare-and-swap; the requirement is
  that the base fingerprint is stored on the draft, not recomputed from
  history.
- **R3. Accepting a draft is one compare-and-swap commit that the journal
  records as a merge.** Ellipsus surfaces "when specific drafts were merged"
  in history; that display exists only if the journal entry for the accept
  operation names the draft revision that was merged, not just the resulting
  bytes. Journal entries need an operation type and an object-plus-revision
  reference, which the 14A operation-journal deliverable should already carry;
  this confirms it cannot be a bare bytes log.
- **R4. Divergent accept is a conflict state, never an auto-merge.** If the
  accepted document moved past a draft's base fingerprint, accept must fail
  into a visible conflict flow (GitBook's gate; itembank's same-ID
  divergent-bytes rule). The prior rejection of ambiguous auto-merge stands.
  The UI needs the model to report the conflict with both fingerprints so it
  can offer re-base or side-by-side resolution.
- **R5. Diff is computed from canonical bytes on demand, never stored.** The
  compare view (side by side or inline) derives from the draft bytes and the
  accepted bytes. Storing rendered diffs would create a second history. The
  model owes stable canonical bytes per revision; fingerprint normalization
  (trailing whitespace, line endings per D-14A-2) must be applied identically
  on both sides before diffing, and never in a way that masks scoring-relevant
  changes in keyed content.
- **R6. History view is a projection of the journal.** Ellipsus's
  sessions-grouped timeline is a rendering choice over timestamps; itembank's
  equivalent groups journal entries per object by day and operation type. The
  journal therefore needs efficient per-object filtering (entries keyed by
  object ID), which the D-14A-1 hybrid decision supports since objects have
  their own IDs regardless of where edges live.
- **R7. Restore is a new forward operation, never a rewind.** Scrivener's
  roll-back-with-snapshot and the append-only journal agree: restoring an old
  revision writes a new revision whose content equals the old one, journaled
  as a restore naming its source revision. The journal never truncates.
- **R8. Component-level diff labeling rides D-14A-2 component IDs.** For
  lesson blocks that carry component IDs (cited, gated, or evidence-bearing),
  the diff view should be able to say "this change touches keyed or
  evidence-bearing content" by intersecting changed spans with component
  boundaries. This requires component IDs to be locatable in the canonical
  bytes (anchored markers), which is a constraint on how 14A serializes them.
- **R9. External edits appear as journal-visible events, not silent drift.**
  The external-editor-in-place peer means the accepted file can change outside
  the UI. The 14A external-edit tracer already gates this; the experience
  requirement is that the history view renders an external-edit event
  distinctly (detected fingerprint change without a journaled operation
  producing it) so the learner sees an honest timeline.
- **R10. Drafts never gate the runtime.** A pending draft of a bank or lesson
  must be invisible to sitting, scoring, and evidence. Only the accepted
  revision feeds the runtime. This keeps the one-runtime invariant untouched
  by the entire drafting layer.

What the UI then is [synthesis]: a draft list on an artifact page, a compare
view, an accept button that runs the normal operation protocol, and a history
tab that renders the journal. No new nouns, no new store.

---

## 5. Non-adoptions (append-only disposition record)

Each line records an observed idea deliberately not adopted, with the reason.
Reconsideration requires new evidence against the stated reason.

- **Notion-style block-per-paragraph object model:** rejected for long-form
  reading; per-block storage costs load time and mobile usability, and
  D-14A-2 already bounds component IDs to cited, gated, or evidence-bearing
  blocks. Reconsider only if block-level evidence attachment is ever needed on
  arbitrary prose.
- **Notion-style database-backed pages as the lesson substrate:** rejected;
  the canonical file must stay coherent plain Markdown, and a derived view
  must never be the only understandable copy.
- **Typora-style full syntax concealment while editing keyed content:**
  rejected; hiding contract characters can hide scoring-relevant bytes.
  Concealment stays acceptable for the learner reading surface only.
- **Obsidian-style plugin-driven reading experience:** rejected as a learner
  surface strategy; the reading experience is a product responsibility with
  accessibility gates, not an extension marketplace. Agent skills, not UI
  plugins, are the extensibility story.
- **Theme gallery (Bear's 20-plus themes):** not adopted; one excellent 17A
  default plus accessibility-mandated variants. Reconsider only if a real
  accessibility need is not expressible as a variant.
- **Real-time collaborative cursors and presence (Ellipsus, Google Docs):**
  not adopted; one learner, asynchronous agent proposals, no co-editing actor
  exists. Reconsider if a human collaborator actor is ever accepted.
- **In-document chat-style comment threads:** not adopted for learner
  surfaces; feedback flows through review of bounded diffs and through notes,
  and Socratic interaction renders as a locked card, not chat.
- **GitBook-style multi-reviewer approval ceremony:** not adopted; 15B review
  is single-reviewer with configured strictness. The interaction (diff plus
  per-change accept) is adopted without the team workflow.
- **Sessions-as-versions as the stored history unit (Ellipsus):** not adopted
  as storage; the journal stores operations, and session-like grouping is a
  display projection only (R6).
- **Style check as auto-correction:** never observed in iA Writer and not
  adopted here either; recorded to fix the stance: prose-quality signals stay
  advisory, matching the linter's contract with authors.
- **Focus and typewriter drafting modes:** deferred, not rejected; near-zero
  cost on CodeMirror, low value while authoring is mostly agent-drafted and
  human-reviewed. Promotion trigger: sustained in-app human drafting.

---

## 6. Pointer for planners

Section 4's R1 through R10 are candidate inputs for the 14A readiness audit's
requirement mapping (each already names its owner). Section 3's ranked list
feeds 16A, 16B, and 17A scoping. Nothing in this file freezes anything; it is
evidence for the normal planning sequence.
