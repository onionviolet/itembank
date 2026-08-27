# Proposal: the workspace, the named set of courses

Drafted 2026-08-27 by an agent session, against `IDEA-LEDGER.md` IL-20260826-01
as narrowed on 2026-08-26. It proposes one new requirement, `FILE-04`, and
recommends one of three shapes for it. **Nothing here is accepted.** No phase is
opened, `REQUIREMENTS.md` is not edited, and no code is written. Two calls at
the end are Weibao's.

This packet does not invent the option set. The three shapes are the three
`.planning/COURSE-SHELL-TEMPLATE.md` line 117 already names: "what names the set
of courses, whether it is a file at all or just a directory scan, and how it
relates to the discovery roots. That is the whole gap." The packet states the
cost of each against the shipped tree and recommends one.

**Why an agent is not deciding this.** The choice fixes a durable object's
source of truth, which is tier 3 under `AGENT-WORKFLOW.md` section 5 (binding
formats and milestone scope, direct-user-decision gate). The prompt that
commissioned this work also says: do not open a phase and do not edit
`REQUIREMENTS.md` without Weibao's word.

**How to answer.** One line is enough, for example
`FILE-04 yes / shape c` or `FILE-04 yes / shape a` or `FILE-04 no`.
Each shape's exact consequence is listed under it, so no answer is more work to
give than another.

---

## 1. What was checked before anything below was written

This section exists because two documents this week claimed a blocker that one
command disproved. Everything below was read from the tree on 2026-08-27, not
from memory of it.

**Nothing in the shipped tree names a set of courses.** Confirmed by grep across
`*.py`, `schemas/`, and `itembank.json`. The three near misses are all something
else:

- `itembank.json` carries `"home": "shelf"`, but `surfaces/home.py:34` defines
  `MODES = ("shelf", "next-action", "agent", "split")`. That is a render mode,
  not a container.
- `surfaces/home.py:31` sets `HOME_UNIT = "bank"`, and the module docstring at
  line 19 says so in as many words: "This is a shelf of BANKS until phase 14B
  lands a course object. The word 'course' on a screen that cannot parse a
  course is the kind of lie this project has rules against. `HOME_UNIT` names
  that seam: 14B swaps the noun and the grouping without touching the modes."
  **This proposal is about the grouping half of that seam.** The noun half is
  already answered by `course.py`.
- `fixtures/visual_system_flow.json:472` has a `courses` key. It is mock data
  for a mockup with no writer.

**A course is a directory holding one sidecar.** `course.py:33` sets
`COURSE_SIDECAR_FILENAME = "course-graph.md"`. Its identity is a minted
`course_object_id` read back out of the sidecar's own header
(`course.py:94-105`), never derived from the path or the directory name
(`identity.py:98-107`, decision D-14A-2).

**Discovery roots are a bare function argument and are persisted nowhere.**
`discovery.inventory(roots, ...)` at `discovery.py:128` takes an iterable of
path strings. A root has no id, no title, no rights, and no fingerprint. The
docstring at `discovery.py:174-177` already refers to a thing that does not
exist: "a caller who has already screened `roots` against an approved-root
registry need pass nothing else". **That absent registry is half of this
proposal.**

**A consequence worth naming: FILE-01 cannot be honoured today.** FILE-01's
degraded clause reads "an unreachable root reports unavailable and the course
opens over the last valid index." There is no last valid index, because
discovery writes nothing and `home_state(root)` rebuilds from a live scan every
request (`surfaces/home.py:254-258`). A root that is offline today does not
report unavailable; its courses simply vanish from the page. So this gap is not
only the mockup's top line. It is a shipped requirement with no object to stand
on.

**Plan 16B-04 will invent one, and the prompt is right about that.** The plan
never names an object. It assumes the set of courses is the daemon root's
subdirectory listing, at `16B-04-PLAN.md:382-384`: "Otherwise list `root`'s
immediate subdirectories, sorted, and keep those containing a file named
`course.COURSE_SIDECAR_FILENAME`." The daemon root arrives at line 507 as
`ia.course_shelf_state(handler.root)`. The plan's own flagged-assumptions block
at lines 695 to 702 lists only the sidecar filename and the `read_course`
signature. **The assumption that the daemon root is the workspace is not flagged
at all**, which is exactly how an invented object ships without a decision.

## 2. The reconciliation with the scope object, which is the real design question

IL-20260826-01's boundary clause requires this, and it is the question most
likely to produce a duplicate: IL-20260817-01 already registers a recursive,
authored, versioned **scope** object that answers boundedness and progress
rollup. If the workspace also rolls up progress, there are two answers to one
question.

**The proposed line is that they answer different questions, and the workspace
has no curricular authority whatsoever.**

| | scope (IL-20260817-01) | workspace (this proposal) |
|---|---|---|
| Question answered | what must be learned, and may it report complete | which courses exist on this machine, and where are their bytes |
| Members | objectives and child scopes | course roots |
| Authored by | the course builder, versioned | the learner, by approving a root |
| Travels in a package | yes, it is curricular truth | **no, it is machine-local** |
| Reports progress | yes, through GRAPH-03 tuples and two rollup models | **no, never** |
| Nests | recursively, unlimited | not at all, one flat level |

The one rule that keeps them from competing, stated once so it can be quoted
later: **the workspace is a locator set, not a membership set.** It says where a
course is, not what belongs in it. Every question about completeness,
denominators, required versus enrichment membership, and rollup stays with
scope and GRAPH-03. A workspace that started answering "how complete is my
degree" would be the second-authority mistake, and the same one the 2026-08-26
template made three times before section 0.1 withdrew it.

That is also why the recommended requirement id sits in the **FILE** family
rather than GRAPH. FILE-01 through FILE-03 are about roots, read-only
discovery, and the distinct link, import, copy, move, supersede and migrate
operations. The workspace is about locating bytes. Filing it there carries the
no-curricular-authority argument in the id itself.

## 3. The three shapes

### Shape A: no file, a directory scan

The set of courses is whatever a scan of one root finds. This is what 16B-04
would ship by default.

| | Effect |
|---|---|
| Cost to build | none, it is already written in 16B-04 |
| Multiple roots | **impossible.** Every course must live under one directory, which contradicts FILE-01's "multiple approved roots (vault, source, bank, note directories)" |
| Unreachable root | **cannot report unavailable.** No index persists, so the course silently disappears. FILE-01's degraded clause stays unimplementable |
| Moved or renamed course | reads as a delete plus an add. Identity is taken from the directory basename at `16B-04-PLAN.md:386-395`, which is the name-based identity FILE-03 forbids and synthesis 12.4 rejected |
| Ordering | in-code only, `ATTENTION_ORDER` then course id (D-16B-10) |
| Recovery | trivial, there is nothing to lose |

### Shape B: an authored Markdown workspace manifest

A hand-written file listing the courses, in the plain-Markdown dual-form style
of the rest of the product.

| | Effect |
|---|---|
| Cost to build | a parser, a linter rule, and a compare-and-swap lineage |
| Reads in Obsidian | yes, which is the case for it |
| Risk | it is the shape IL-20260826-01 **already withdrew** at course level on 2026-08-26: "a second authored manifest would put two object kinds in competition for the same bytes, which `course.py` refuses by design." The withdrawal was about the course manifest, so it does not automatically bind here, but the reasoning transfers: a hand-edited list of courses drifts from the sidecars it names, and then something has to decide which is right |
| Recovery | a hand-repairable file, but its content is not reconstructible if lost, because membership was authored rather than derived |

### Shape C, recommended: a registry of approved roots, plus a derived course index

Two objects with a clean split, matching how the tree already stores machine
state.

1. **Durable and small: the workspace record.** A name, an ordered list of
   approved roots, and one member entry per course keyed by `course_object_id`
   with its last known root and relative path, how it entered, and when. Format
   JSON, validated by a schema in `schemas/`, alongside the existing
   `settings.schema.json` and the journal's `_journal/objects.json`.
2. **Derived and disposable: the course index.** What discovery finds when it
   walks those roots for `course-graph.md`. Rebuildable at any time, and never
   the only understandable copy, per the standing derived-view rule.

**Membership is granted by root approval, not curated by hand.** A course found
under an approved root is a member. Approving the root is the consent, so there
is no per-course add step and no friction. What the durable entry buys is
identity: on first sight the minted `course_object_id` is pinned to a path, so a
later move or rename is reconciled against the id rather than read as a new
course. A pinned id whose sidecar at that path now reports a different id is a
**conflict**, surfaced, never silently overwritten.

| | Effect |
|---|---|
| Cost to build | one small schema, one reader and writer through `journal.commit_operation`, and the root list threaded into the existing `discovery.inventory` call. No new parser, no new scorer, no new evidence store |
| Multiple roots | yes, which is what FILE-01 already requires |
| Unreachable root | reports `unavailable`, and the shelf opens over the last valid index with those cards marked. **This is the first time FILE-01's degraded clause becomes implementable** |
| Moved or renamed course | reconciled by pinned id, per FILE-03. Name similarity stays a search hint |
| Ordering | the record carries an explicit order, so D-16B-10's attention rank has something stable to break ties against |
| Recovery | **the strong point.** Because membership is root-granted rather than authored, total loss of the file is recovered by re-running discovery over the roots. Only the pinned-id history and the ordering are lost, and both are re-derivable or re-chooseable. Nothing irreplaceable lives here |
| Egress | none. The file is machine-local and must be excluded from `course_package`, which today carries exactly one course sidecar and nothing else (`course_package.py:123-129`) |

**Recommended: shape C.** It is the only one of the three that makes an already
shipped requirement (FILE-01's degraded clause) true rather than aspirational,
and it is the only one that survives a course being moved. Its extra cost over
shape A is one schema and one small module, and it deletes the invented
assumption at `16B-04-PLAN.md:382`.

**Where the recommendation is shaky, stated plainly.** If Weibao intends to keep
every course under one folder forever, on one machine, shape A is honest and
shape C is over-built. Shape C earns its cost the moment a course lives in the
Obsidian vault while another lives beside the banks, which is the arrangement
FILE-01 was written for.

## 4. The drafted requirement, if shape C is accepted

House form, for `REQUIREMENTS.md` under `#### FILE: files, roots, and
operations`. **Not yet inserted.**

> - [ ] **FILE-04**: A workspace names the learner's set of courses as an
>   ordered set of approved roots plus one durable member entry per course,
>   pinned by `course_object_id` rather than by directory name; the course index
>   built by walking those roots is derived and disposable. The workspace is a
>   locator set and not a membership set: it carries no objective, no
>   completion predicate, and no progress claim, and every question of
>   curricular membership, boundedness, and rollup stays with the scope object
>   and GRAPH-03. It is machine-local and never travels in a course package.
>   Owner: the learner. Durable object: workspace record. Authority: root
>   approval by the learner, mutated only through the operation journal.
>   Degraded: an unreachable root reports unavailable and its courses open over
>   the last valid index, marked unavailable rather than dropped; a pinned id
>   that disagrees with the sidecar found at its path is a conflict, surfaced
>   and never merged. Gate: G3. (per synthesis section 6; makes FILE-01's
>   degraded clause implementable, and supersedes the daemon-root-is-the-
>   workspace assumption at `16B-04-PLAN.md:382`.) Fixture: a synthetic
>   two-root workspace holding three courses, one root made unreachable, one
>   course moved between roots, and one path whose sidecar reports a different
>   `course_object_id`, asserting the unreachable root's courses render from the
>   last valid index as unavailable, the moved course reconciles by id to one
>   card rather than two, and the id disagreement reports a conflict without
>   writing.

## 5. The thirteen fields, per `.claude/CLAUDE.md` lines 95 to 97

| Field | Answer |
|---|---|
| Actor | the learner, approving roots. Not the course builder, which owns scope |
| Durable object | the workspace record: name, ordered roots, member entries |
| Source of truth | one machine-local JSON file for the record. The filesystem for what is actually there. The sidecar for what a course is |
| Authority | the learner for membership and order. The workspace has no authority over objectives, evidence, scoring, or completion |
| State axes | root availability (available, unavailable, denied) and member state (present, missing, moved, conflicting) are separate from each other and from the course's own accepted-content, validation, and rights state |
| Provenance | each member entry records the root it was found under, the date, and the journal operation id that added it |
| Rights | approving a root is a **read** grant only. It never confers transform, remote-process, package, export, or share, per RIGHTS-01 and FILE-02 |
| Egress | none. Machine-local, excluded from `course_package` |
| Degraded behavior | as in the FILE-04 draft above: unavailable rather than absent, conflict rather than merge |
| Accessibility | the workspace is data. Its rendering is the shelf, already under 16B-04 and A11Y-01 |
| Validation | schema validation plus `itembank guard`; a member whose pinned id disagrees with the sidecar at its path fails validation as a conflict |
| Recovery | re-derivable from the roots, because membership is root-granted. Loss costs the pin history and the chosen order, nothing else |
| Maintenance owner | whoever owns the home and shelf surface: `surfaces/home.py` today, plan 16B-04 next |

## 6. What happens on yes

1. `FILE-04` is inserted into `REQUIREMENTS.md` under the FILE family, and a
   row is added to the traceability table.
2. `IDEA-LEDGER.md` IL-20260826-01 gets a dated note moving its disposition
   from Registered to Core, naming FILE-04 as where the workspace level landed.
   The 2026-08-26 narrowing note stays exactly as written, per append-only.
3. `FILE-01` gets a dated pointer noting that its degraded clause becomes
   implementable under FILE-04. Its text is not rewritten.
4. Plan `16B-04-PLAN.md` lines 382 to 395 and its flagged-assumptions block get
   an amendment naming FILE-04 as the source of the course set, so the plan
   stops inventing one. This is an amendment to an unexecuted plan, in the same
   shape as the 2026-08-27 percent amendments.
5. A phase assignment is proposed separately. The natural home is 14B or a
   small addition to it, because 14B owns the course object and 16B-04 consumes
   this. **That sequencing question is not settled here** and interacts with the
   14B freeze gate, which is itself one of the eight open decisions.

## 7. What happens on no

This packet becomes the reconsideration record. IL-20260826-01 gets a dated note
recording that the workspace level was proposed as FILE-04 and declined, with
the reason, so the 16B-04 assumption at line 382 is then a **recorded and
accepted** choice rather than an unflagged one. That is a materially better
state than today even if the answer is no, because the invented object stops
being invisible.

## 8. What this proposal does not do

It does not open a phase, does not edit `REQUIREMENTS.md`, does not touch
`16B-04-PLAN.md`, does not stand in for any of the eight decisions in
`NEXT-2026-08-27.md`, and does not reopen the 2026-08-27 percent ruling. It
proposes one requirement and recommends one of three shapes the template already
named.
