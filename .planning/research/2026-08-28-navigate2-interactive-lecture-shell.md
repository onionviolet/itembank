# The Interactive Lecture player, and what a slideshow-with-quiz treatment would owe

Date: 2026-08-28
Method: authenticated read-only inspection of the Interactive Lecture SCORM shell in
the learner's own browser, at the URL Weibao supplied
(`pluginfile.php/57822603/mod_scorm/content/7/Shell/main.html`), plus its
`imsmanifest.xml`, `launch.html`, `Shell/config.xml` and the shell's own script
manifest. Raw structural capture kept out of the repository at
`scratchpad/nav2/interactive-lecture-shell-2026-08-28.md`.

Status: **observation and interpretation**. Nothing here is an accepted product
clause. Section 3 is a recommendation only.

This extends `.planning/research/2026-08-26-navigate2-teardown.md`, which mapped the
course shell but never opened the one rung that carries a grade item. That rung is
this player.

## 1. What it is (fact)

SCORM 1.2, one SCO per chapter. The manifest declares a single organization `TOC1`
with a single item, `Module 01 - EMS Emergencies`, whose resource is `launch.html`.

`launch.html` is a gate page, not content. It sniffs the browser, loads an
SCORM API wrapper, reports course status as `notstarted`, `incomplete` or
`completed`, shows one launch button, opens the real player in a named popup, and
warns that closing the popup exits the course.

The player is `Shell/main.html`: a hand-rolled jQuery 1.11 application (Bootstrap,
jQuery UI with touch-punch, magnific-popup, mediaelement.js). Its own modules are
`models.js`, `render.js`, `events.js`, `mediamanager/media.js`, `compliance.js`,
`common/ui`, `common/notes`, `common/glossary`, `common/objectives`.

**The data model is three levels: module, chapter, page.** `models.js` loads
`config.xml`, sets module paths, loads a module `index.xml`, builds `Chapter` and
`Page` models, tracks per-page status, and serializes through a `DataStorage`
object. `main.js` loads one page at a time: page XML, then a named template, then
render, then a page-completed event, with `__onPageLockEnd` between render and
navigation. `compliance.js` is the only place SCORM is touched, and `models.js`
exposes exactly one assessment hook, `__onQuizComplete`.

**Observed controls** (the shell loaded outside a launch, so no deck was present):

| Region | Controls |
|---|---|
| Header | chapter title, notes, menu |
| Menu overlay | Help, My Notes, Glossary, Credits |
| Stage | full bleed slide |
| Footer left | narration audio: play, scrub, elapsed, total, mute, CC toggle, playback speed (1.00x) |
| Footer right | prev, slide counter "N of M" with a caret opening a table of contents, next |

**`config.xml` carries two settings that matter.** `<media type="remote" override="true"/>`,
so the deck's media is fetched from a vendor CDN and nothing works offline, and
`<slidelock enabled="true" time="5000"/>`, a five second timer that holds the learner
on a slide before advancing is permitted.

**Not obtained:** the deck itself. `index.xml`, the per-page XML and the template
vocabulary sit behind a module path passed in the launch query string and served
remotely. Probing sibling paths under the package root returned 404. No item
content, no lecture text, no audio and no captions were downloaded, and nothing
vendor authored was copied into this repository.

## 1a. The deck itself (fact, added later on 2026-08-28)

Weibao launched Chapter 1 and reached page 12, and the deck was then re-entered
through Moodle's preview mode, which loads the player without writing tracking
data. The module resolves to `Module/en/index.xml` inside the package.

**`index.xml` is a bare table of contents, nothing more.** One `module` with a
title, one `chapter type="content"`, one `objectives` element that is commented
out and whose `href` points at a remote file lookup service, and a `pages` list.
The only attributes anywhere in the file are `type`, `href` and `locked`.

**39 pages.** Each `page` carries a CDATA title and an empty `type` attribute, so
type is unused in this deck. Page content is not in this file; the player fetches
per-page XML and a named template at load time, and neither was obtainable
without a live SCORM session (the paths are not guessable and the shell stalls on
the API handshake). The template vocabulary therefore remains unknown.

**Four pages carry `locked="true"`: 12, 22, 32 and 38.** Page 12 is the page
Weibao's screenshot shows, and it is a Knowledge Check. So `locked` marks the
checkpoint pages, and the checkpoint is a gate on forward navigation rather than
a page like any other.

**The cadence, therefore, is measurable:** roughly one checkpoint per ten pages of
reading (12, then 22, then 32), with the fourth at 38 of 39, immediately before
the end. That is exactly the "quiz after a little reading" shape, made explicit.

**The observed checkpoint, structure only.** A page titled Knowledge Check, one
instruction line, and four numbered stems. Each stem is a sentence with a dropdown
embedded inside it, so the learner picks a term to complete a claim rather than
choosing from a lettered list beneath a question. One `Submit` and one `Clear`
serve the whole set of four, not each stem. A feedback panel sits below the set
and carries the instruction before submission. One stem was already answered and
held its value, so per-stem state persists within the page.

**After Submit** (second screenshot, all four answered correctly): each stem keeps
its chosen value, its dropdown goes disabled and greyed, and a feedback panel opens
directly beneath that stem containing a verdict word and one sentence. So Submit is
a batch action over the set, but **disclosure is per stem**. The sentence observed
in each of the four panels restates the stem's own claim back to the learner rather
than explaining a distinction or addressing a wrong choice.

Only the all-correct path was observed. What a wrong stem shows, whether a retry is
offered, and whether the key is revealed on failure are all unknown. No vendor item
text is reproduced here.

**An ordinary content page, for contrast (third screenshot).** Not every page is a
checkpoint. A content page observed later in the same deck is a collapsible panel:
a coloured header bar carrying one short concept name, a chevron that collapses it,
and inside it three or four top-level bullets, one of which nests a sub-list of
three items. That is the whole page. Roughly forty words of body text, one concept,
one level of nesting, and the panel can be closed.

## 2. Interpretation

**The good part is the page contract, and it is smaller than it looks.** Strip the
vendor and what remains is: an ordered sequence of pages; each page is data plus a
named template; each page emits a completion event; a narration track with captions
and a speed control runs beside the page; a table of contents can jump; and notes,
glossary and objectives are ambient services available on every page rather than
separate activities. That is a legitimate treatment shape and itembank has no
equivalent today. The 2026-08-26 teardown's proposed rung ladder has `teach` filled
by a lesson document, which is a continuous reading surface, not a paced one.

**One page type carries assessment, and it is the reason this rung is graded.**
`__onQuizComplete` is the single assessment hook in a player with a full page and
template system, and the gradebook confirmed that the Interactive Lecture is the
only activity of the 435 that carries a grade item at all. So the vendor's answer to
"how does a lecture produce evidence" is precisely the thing Weibao is naming: put
questions inside the slideshow. The idea is sound. The implementation puts the
verdict inside the vendor's own player and reports one aggregate number to SCORM,
which is exactly the split-evidence failure the teardown documented at TestPrep.

**"A quiz after a little reading" is the deck's actual structure, not a metaphor.**
The gate is worth separating from the timer rejected below. Holding a learner on a
page until five seconds elapse counts clock time as learning. Holding them until
they have attempted a checkpoint counts an attempt, which is real evidence and is
the runtime's to settle. The first is indefensible and the second is arguable, so
they should not be rejected or accepted together.

**The checkpoint item is a form itembank does not have, and that is informative
twice over.** An inline dropdown that completes a sentence is not one of the seven
shipped types, and it is also not one of the five NREMT types the 2026-08-24 vision
entry pinned practice to. It is a teaching form, useful for checking a distinction
mid-lesson and useless as examination fidelity, which is precisely the split
already registered as IL-20260826-10. If a paced lesson gets checkpoint forms of
its own, they belong in the teaching pool and must not leak into a blueprint
denominator.

**The batch Submit is not the "gambling" failure, and the feedback quality is the
real finding.** Submitting four stems at once looked at first like the case Weibao
named on 2026-08-24, where a wrong answer tells you nothing about which part was
wrong. The post-submit screenshot corrects that: disclosure is per stem, so the
specimen already does the thing he asked for, at least on the correct path. What it
does badly is the content of the disclosure. Each panel restates the stem's own
claim, which confirms without teaching, and confirmation is worth least exactly
where the learner needed it least. itembank's authored per-option rationale (`DA:`)
is strictly richer than this, so the design target here is not to catch up with the
specimen but to spend the panel on the distinction the stem was testing. The
unobserved wrong-answer path is the one that matters and it should not be guessed
at: whether the specimen names which stems are wrong, permits a retry, or reveals
the key is unknown.

**Two mechanisms should not be copied.** The slide lock is a timer that treats
elapsed seconds as engagement, and it is presentation state pretending to be
evidence in the same way `Mark as done` is, only without the learner's consent.
Remote media with `override="true"` means the treatment cannot run unplugged, which
the degrade-never-block rule forbids for anything on the core loop.

**The captions and the speed control are not decoration.** Together with a keyboard
reachable table of contents they are most of what makes a narrated deck usable at
all, and they land inside the existing `UI-SPEC.md` accessibility gates rather than
beside them.

## 3. Proposal for itembank (recommendation, not accepted)

### 3.1 A `paced` presentation of an existing lesson, not a new artifact

The durable object stays the lesson document. A slideshow is a **presentation mode**
over an already authored lesson: the same Markdown that reads as a continuous
document in Obsidian is projected as an ordered sequence of steps, one per section
boundary or explicit break. This is the dual-form rule in the course artifact
workflow, applied to pacing rather than to hover definitions. It also answers the
open question already recorded in the style work, whether a style is a semantic
transformation or a cosmetic theme: this one is a projection, so it is neither, and
it must not be authored as a second parallel file.

### 3.2 Checkpoint items are ordinary bank items, scored by the one scorer

The quiz inside the deck is not a quiz. It is a checkpoint item drawn from the bank,
answered through the runtime, producing an ordinary attempt in the one evidence
store, disclosed under the session mode and hint tier the runtime already gates.
Nothing about being embedded in a slide changes who settles the verdict. This is
what makes the treatment evidence-bearing without inventing a second authority, and
it is the only part of the vendor's design that itembank must implement differently
rather than better.

### 3.3 What the mode owes

- Narration is optional. When present it needs captions and a speed control, and the
  deck must be fully usable with audio off, which is also the offline path.
- Every step is reachable by keyboard and by the table of contents, and the table of
  contents is a jump, not a gate.
- No timed lock. Advancing is the learner's call. If a step must be attempted before
  moving on, that is a checkpoint item and its verdict is the runtime's.
- A step that emits no evidence says so, per the purpose taxonomy in the teardown
  section 4.3 and IL-20260826-02.
- Position in the deck is presentation state. It is resumable and it never counts as
  progress, coverage or mastery.

## 4. Open questions

1. Where do step boundaries come from. Left open on 2026-08-28: Weibao's answer was
   that there are several possibilities and probably more than were listed, so the
   candidates are preserved rather than narrowed. See section 4a.
2. Is a checkpoint inside a paced lesson the same session object as a sitting, or a
   distinct evidence kind that must not be mixed into a blueprint denominator.
3. Does the paced mode belong to the lesson renderer or to a fourth surface, and how
   does it reach the CLI, which has no slides. The surfaces rule as clarified on
   2026-08-15 says a presentation-only behavior owes an accessible equivalent rather
   than a command, and a paced deck looks like exactly that case, but the checkpoint
   items inside it are runtime capabilities and do owe both.
4. Whether narration is ever authored by this project or is only ever the learner's
   own recording, given rights and cost.

## 4a. Step boundaries, the option space (open, not decided)

Recorded 2026-08-28. This enumerates candidates and their consequences. It does not
choose, and it is explicitly non-exhaustive: the list is open and a candidate not
written here is not thereby rejected.

**The discriminator that is not a matter of taste.** A step needs a stable identity,
because position in a paced lesson is resumable, because a checkpoint has to say
which step it sits in, and because a lesson gets edited after the learner has already
been through part of it. Candidates that derive boundaries from authored content have
identity that survives editing elsewhere in the document. Candidates that compute
boundaries at render time do not: insert a paragraph and every later step silently
becomes a different step, so a resumed position and any recorded reference to a step
both point somewhere else. That is a correctness property, not a preference, and it
orders the candidates without settling which one wins.

| # | Candidate | What it costs | What it buys |
|---|-----------|---------------|--------------|
| A | Explicit authored marker (a thematic break, or a named line) | new format surface, and the author has to think about pacing while writing | exact control, stable identity, still reads as a plain document in Obsidian |
| B | Heading level, configurable per lesson | couples document outline to pacing, so a long section becomes an unreadable step | zero new syntax, works on every lesson already written |
| C | Per-lesson setting choosing among the others | one more knob, and a default that has to be right | different sources and subjects can pace differently without a format fight |
| D | Semantic block boundary, one block per step | far too fine for reading prose | natural fit if narration is ever synced to content |
| E | Checkpoint-anchored, steps fall where the questions are | pacing follows assessment rather than teaching, which is backwards when a lesson has two questions | guarantees every step ends in something that emits evidence |
| F | Renderer-computed to a length budget | unstable identity, see above; also non-deterministic across viewports | no authoring cost at all, works on imported and legacy material |
| G | Learner-chosen granularity at view time (whole document, by heading, by step) | needs a defined interaction with whatever the authored answer is | pacing becomes a reading preference, which is where it arguably belongs |
| H | Agent-proposed markers, author-accepted as a bounded diff | needs the review path, which already exists | makes A cheap on legacy material without making the machine the author |

**Two observations, offered as interpretation and not as a decision.**

These are mostly not rivals. A, B and F answer "what does the renderer do when it is
handed a lesson", and the natural shape is a precedence ladder rather than a single
winner: an explicit marker if the author left one, else the configured heading level,
else the whole document as one step, which degrades to exactly today's behavior. C is
the knob that ladder needs; H is a way to get A onto material nobody wants to hand
edit; G sits on top of whatever the ladder produced and is a separate question about
who controls granularity, the author or the reader.

The one genuine fork is whether pacing is an authored property of the lesson or a
view preference of the reader. That fork decides whether a step is a thing that can
be cited and resumed, or a thing that only exists while someone is looking at it, and
it should be settled before the boundary syntax is, because the syntax question only
matters on the authored side of it.

## 5. Rights and provenance note

Structure only: manifest fields, file names, function names, configuration keys, and
the visible control set. No deck content, no lecture text, no audio, no captions and
no assessment items were extracted or stored, and none entered this repository. The
player is vendor code and is not vendored, quoted or adapted; anything itembank
builds here is clean-room derived from the shape described above. AAOS 12e content
remains under its publisher's terms and the `guard` rule is unaffected.
