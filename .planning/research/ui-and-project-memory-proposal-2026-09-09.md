# UI scope and an auditable project history

Date: 2026-09-09. Status: research and proposed design.
Owner: Weibao for product choices. Existing phase owners retain implementation
and audit closure. This document accepts no new UI, schema, or infrastructure.

## Outcome and evidence boundary

The proposed next design exercise is one complete study session, compared over
identical content. A project-history workspace would connect the original
ideas, alternatives, decisions, changes, and observations behind that session.
Past investment contributes switching cost, not evidence of present quality.

User intent is preserved in `../USER-VISION.md` under "UI scope and an auditable
project history" and "fresh evaluation of prior choices in future audits".
The latter is also recorded in `../AGENT-WORKFLOW.md` section 10 as standing
audit guidance. The workspace and UI comparisons remain proposals.

This pass sampled the relevant September 6 through 8 vision entries, the
current state summary, Phase 20 audit routing, recent UI evidence, the existing
idea ledger, and `scripts/vision_audit.py`. It did not inspect the entire vision
history, exercise the live UI, or measure learner outcomes. Source acquisition's
concurrent combined audit was read but not changed. Only public project names
and public research queries were used on the web.

## P1 through P5: what Synapse and seer contribute

Thomas Havlik's [portfolio](https://thavlik.dev/#projects) matches the projects
in the screenshot. Both are closed source. Its descriptions are evidence of
what the author claims, not independent correctness, performance, privacy, or
learning-effect verification. The screenshot describes seer with Kafka, while
the current page names NATS JetStream. Preserve both source versions without
inventing a migration history.

| Ref | Transferable idea | Smallest useful itembank interpretation | Disposition proposed here |
|---|---|---|---|
| P1 | Assistance understands the curriculum | Scope source help by the selected course, objective, accepted material, and current activity. Let the learner open the supporting passage without losing their place. | Prototype refinement of existing source and reader work |
| P2 | Hybrid retrieval across media | Combine exact terminology and conceptual matching over the same source identities. Return a page, slide, image region, or timestamp with its extraction limits. | Prototype on a bounded corpus |
| P3 | Traceable, restartable processing | Reuse existing operation and source owners to show extraction state, failed stage, accepted revision, and what a changed source affects. | Prototype composition where a learner journey is missing |
| P4 | Formal checks around defined claims | Evaluate formal specification for one narrow invariant only when ordinary tests leave a consequential gap. | Backburner pending a named target |
| P5 | Institution-scale streaming and distributed services | Retain as future infrastructure options when measured load or an institutional use case justifies operational cost. | Backburner pending demand and measurement |

For P2, exact terms and conceptual paraphrases serve different retrieval jobs.
[Microsoft's hybrid-search documentation](https://learn.microsoft.com/en-us/azure/search/hybrid-search-overview)
describes full-text and vector queries with rank fusion. This supports the
pattern, not a need to adopt Azure. Test lexical retrieval alone, vector
retrieval alone, and hybrid on the same judged questions. Include exact names,
paraphrases, missing answers, changed sources, and access restrictions. Record
relevant-passage retrieval, citation location, failure behavior, latency, and
resource cost before choosing a backend.

For P4, [Lean's reference](https://lean-lang.org/doc/reference/latest/Introduction/)
describes a small proof-checking kernel. A formal proof establishes a formalized
claim under its assumptions. It does not independently establish that a medical
source is true or that prose was translated into the right proposition. Keep
retrieval relevance, citation validity, source support, formal validity, and
assessment correctness distinct.

The screenshot offers too little learner interaction evidence to copy a UI.
The strongest UI hypothesis is source context available beside the current
learning task. The strongest architecture hypothesis is retrieval and processing
that can explain their provenance. See the linked
[primary-source review](synapse-seer-primary-source-review-2026-09-09.md).

## U1: scope the UI around one study session

Use this proposed task: return to a populated course, understand the next
useful activity, open its assigned material, consult a definition or source,
make a note, practice, understand feedback, leave, and resume later. Choose a
source and activity that already exist. Record missing capabilities explicitly.

This task exposes hierarchy, navigation, reading comfort, interaction,
feedback, and recovery in one bounded comparison. It follows the principle of
testing believable tasks with clear goals and neutral instructions in the
[GOV.UK usability-testing guidance](https://www.gov.uk/service-manual/user-research/using-moderated-usability-testing).

| Ref | Review lens | Evidence to capture |
|---|---|---|
| U1a | Orientation and hierarchy | What the learner thinks this screen is for, their first action, and where they hesitate |
| U1b | Reading and doing | Comfort with real-length content, use of space and typography, source access, notes, and whether context is lost |
| U1c | Transitions and feedback | Committed response, permitted help, feedback understanding, Back, exit, and exact resume |
| U1d | Desktop and phone | A desktop study workspace with relevant adjacent material, and a phone flow with one clear task and reachable contextual controls |
| U1e | Missing and degraded states | Empty course, long job, missing source, stale link, offline use, interruption, and the next supported action |

Compare the current UI with two materially different proposals over the same
content and state: a reading-centered workspace with context beside the page,
and a session-centered flow organized around the current learning sequence.
These are candidate compositions, not three permanent themes. They may share
components, combine, or be dropped after comparison. Match prototype fidelity
so polished art does not compete against unfinished controls.

Record task success, wrong turns, unnecessary context switches, recovery,
reading comfort, and the user's visual preference separately. Aesthetic
preference is valid evidence about desired experience. Neither aesthetics nor
task completion alone proves learning efficacy. Human acceptance remains human.

The [existing evidence inventory](ui-review-evidence-inventory-2026-09-09.md)
identifies useful dated observations. Phase 20 reports deterministic coverage
and human acceptance owed. Its current routing remains
`../phases/20-extensible-ui-foundation-and-interaction-clarity-pass/20-AUDIT-CROSSWALK.md`.
A September 8 walkthrough reported misleading resume wording. Reproduce it
before treating it as a current defect. Older profile alternatives must also be
reconciled with the September 8 selected product identity before reuse.

## V1: one project workspace, three synchronized views

Place this in project development and review space. Whether it belongs inside
the packaged learner app remains unresolved. That avoids assuming every learner
needs the maintainer's project history.

| View | What it answers | Suggested interaction |
|---|---|---|
| Timeline | What did we believe, choose, build, and learn at each point? | Zoom from a period to one decision, open its original evidence, and compare knowledge then with knowledge now |
| Ideaboard | Which needs and alternatives are still worth exploring? | Group cards by learner job or open question, preserve competing branches, attach evidence, and switch to a keyboard-accessible list |
| Review | What needs another look, and what changed our minds? | Show contradictions, unsupported closure, missing ownership, changed assumptions, overdue evidence, and decisions whose revisit trigger fired |

The same selection should persist across all three views. A shared detail panel
shows the exact source, interpretation, evidence, related alternatives, current
disposition, and history. The board should not default to Done versus Not done.
Group by the problem being solved so implemented ideas do not dominate the
layout. A chronological timeline records events without implying every idea
must advance through one irreversible pipeline.

### Reuse the existing owners

| Existing record | What the surface reads |
|---|---|
| `../USER-VISION-INBOX.md` and `../USER-VISION.md` | Original request, promoted intent, dated interpretation, relationship to earlier intent |
| `../IDEA-LEDGER.md` | Stable IL identifiers, proposal, disposition, alternatives and revisit condition |
| Existing research and audit files | Claims, observations, evidence limitations, source dates and original finding locators |
| Owning contracts, decisions, plans, crosswalk and Git revisions | Accepted choices, implementation references, owners, rationale and changes |
| Verification and later feedback | What was tested, on which revision, passed/failed/unavailable/owed, expected outcome versus actual outcome |

Build a disposable index over those files. Use existing identifiers and exact
document anchors first. Add a small reviewed relationship overlay only where
the originals cannot express a connection. It must not become a second editable
copy of status or acceptance. Candidate relationships include supports,
contradicts, addresses, depends-on, supersedes, and reopens. Similar wording
only suggests a match and cannot merge two records automatically.

Preserve event date, recording date, observed revision, and source fingerprint
separately. Unknown dates remain unknown. A file modification time is not proof
of when a decision was made. A historical view needs the actual retained
revision. If it is missing, show a partial reconstruction. A hash detects a
change but does not restore missing bytes or prove a claim true.

Keep acceptance, implementation, verification, confidence, and freshness as
separate fields. A card may correctly say accepted, implemented, deterministic
checks passed, human review owed. An old verified observation stays valid about
its original revision while its applicability to today's UI requires recheck.

### A real initial history thread

Use the September 6 request for a better-fitting replaceable UI, the September
7 home comparisons, the September 8 selected interface, the integration and
verification records, and today's dissatisfaction. Link these by their recorded
relationships. Today's concern reopens evaluation of fitness. It does not imply
that the earlier choice was irrational or that all of its work must be removed.

A future reviewer should be able to ask: what need did the decision serve, what
alternatives were considered, what was actually checked, what remained unknown,
and what later observation changed the recommendation?

## B1 through B5: make bias visible and contestable

No interface or AI review can guarantee freedom from bias. These are proposed
review mechanics that make assumptions and contrary evidence inspectable.

| Ref | Mechanism | Concrete behavior |
|---|---|---|
| B1 | Start with current needs | Define the learner task and comparison criteria before reading old solution rationales. Then reconcile with the history and current obligations. |
| B2 | Compare alternatives fairly | Include a credible alternative and, where useful, doing nothing. Initially hide incumbent labels in design comparison. Reveal implementation state before feasibility and migration decisions. |
| B3 | Separate fitness from cost | Record which option best serves the task, then switching cost, compatibility, maintenance, and reversibility. Do not count money or effort already spent as current quality. |
| B4 | Preserve contrary evidence | Keep failed prototypes, user dissatisfaction, missing samples, and conflicting observations. Ten summaries of one test are still one test. |
| B5 | State what would change the answer | Record expected benefit, falsifying evidence, evidence date, and a concrete revisit trigger. Later reflection compares expected and observed outcomes before changing disposition. |

This is compatible with the [Design Council's iterative discovery and testing
framework](https://www.designcouncil.org.uk/resources/framework-for-innovation/).
An accepted decision remains the operating choice until explicitly revised,
but acceptance does not exempt it from evaluation. Cite current authority when
a boundary limits implementation. Record a proposed change to that boundary
when justified rather than silently treating it as permanent design truth.

AI may suggest themes, links, contradictions, and candidate alternatives with
source references and confidence. It cannot silently merge ideas, delete
history, promote its own summary to user intent, or declare a successful user
outcome. Semantic search must not hide low-ranked contrary evidence from the
review view.

## N1: smallest concrete next packet

Prototype a read-only project-history surface using one real UI decision thread
and roughly 20 to 30 linked records. Include Timeline, Ideaboard, Review, and
the shared source detail panel. Keep current files in place. Start with local
metadata and text search. Add semantic retrieval only if a measured retrieval
gap warrants it. This is a proposed packet, not a build performed in this pass.

Its acceptance exercise has five tasks:

1. Trace one current UI choice back to the exact user concern and alternatives.
2. Reconstruct what evidence existed then without silently using later facts.
3. Find a superseded or deferred alternative and explain its revisit condition.
4. Distinguish implementation proof from human acceptance and expose a conflict.
5. Rebuild the index after a source change, marking stale links and preserving
   the original records. Report every unindexed or unresolved input.

Then use that same history thread to scope the one-session UI comparison.
Expand the importer to other idea and audit families only after the trace works.
Archive, cross-project reuse, editable board actions, automatic reflection,
and semantic retrieval need separate follow-on evidence.

## Verification and record integrity

Baseline `python3 scripts/vision_audit.py` exited successfully. It reported 51
vision entries, 37 inbox entries, seven pointer-only interpretations and ten
missing relationship fields. These are the script's structural observations,
not proof of semantic completeness. In `main`, path checking accepts matching
basenames anywhere, and the orphan check accepts a matching date anywhere in
the planning corpus. Therefore its zero missing-path and orphan counts cannot
establish exact causal links or audit independence. No script change was made.

Future indexing should validate exact targets, accepted relationships, source
versions, and unresolved coverage explicitly. This pass does not claim all
prior ideas were indexed or all prior audits reconciled. The proposal's routes
are recorded under IL-20260909-01 through IL-20260909-05.

After capture, the vision checker exited successfully with 53 vision and 39
inbox entries. Its seven pointer-only and ten missing-relationship counts were
unchanged. `git diff --check` passed. `python3 scripts/preflight.py --quick`
passed every executed gate, including the path and mirrored-skill checks. As
documented by that command, full Python tests, JavaScript tests and the clean
tree gate were skipped. Human UI review was not performed.

No application code, source material, scores, evidence, or existing audit
closure was changed. No commit or deployment was performed. Recovery is removal
of this pass's three new research files and only its additive capture, ledger,
and workflow entries after reviewing the diff. Preserve concurrent edits and
the pre-existing source-to-reading audit change.

## Issue publication, 2026-09-09

The user requested publication of these findings as GitHub issues. Existing
open and closed issues were checked, including the narrower historical UI
issues 6, 17 and 18. The public issue bodies are self-contained and omit private
paths and learner data. New local research and capture records remain
uncommitted, so the issues cite available pinned sources and summarize the
new findings directly.

| Issue | Published scope |
|---|---|
| [20](https://github.com/onionviolet/itembank/issues/20) | Compare a complete study session across UI alternatives, including the founding Albert and Brilliant intent |
| [21](https://github.com/onionviolet/itembank/issues/21) | Prototype the project timeline, ideaboard and review surface |
| [22](https://github.com/onionviolet/itembank/issues/22) | Evaluate prior decisions against current needs and evidence |
| [23](https://github.com/onionviolet/itembank/issues/23) | Fix vision-audit false positives from unrelated basenames and shared dates |
| [24](https://github.com/onionviolet/itembank/issues/24) | Evaluate course-scoped source context and hybrid retrieval, with formal methods and institutional infrastructure retained as future leads |

All five issues were read back as open, with the intended labels and exact
body matches. Publishing the issues did not commit or push repository changes.

The issue 23 behavior was also reproduced with the unmodified current script
in isolated synthetic directories. An unrelated same-basename file and a shared
date produced zero missing files and zero orphans for an unlinked entry. The
control, without the basename collision or shared date, produced one missing
file and one orphan. Both runs exited zero under the current reporting behavior.
The production script was not modified.

## Fresh architecture evaluation demonstration, 2026-09-09

Scope: [issue 22](https://github.com/onionviolet/itembank/issues/22), read live
on 2026-09-09. The decision is how the vision audit establishes structural
references. This review uses the existing workflow section 10 and this research
owner. It does not accept a new architecture or certify absence of bias.

### Present need and criteria, recorded before inspecting historical code

The reviewer needs to distinguish an exact source reference from a plausible
text match without changing the original records. Criteria are: avoid false
verification, expose ambiguous and unsupported inputs, reproduce results from
local files, preserve those files, and make the result understandable enough
to support later history review. Broad recall is useful only when candidates
remain separate from verified links. Latency and maintenance matter separately
from reference correctness.

The current packet and issue 23 diff were already visible when these criteria
were recorded. This is not a blind review or proof that prior choices had no
influence. It precedes inspection of historical code and final ranking, not all
exposure to the incumbent. This architecture exercise has no visual comparison.
Withholding incumbent labels is therefore not tested here and remains a
proposed method for issue 20.

### Historical evidence and current authority

The historical implementation was inspected at repository revision
`5f3aaf33b1896657f5a52bd6136a5ac1fbb616fa` using
`git show HEAD:scripts/vision_audit.py`. Its last file commit was `7e56886`,
dated 2026-09-04. The module's stated purpose was checking whether vision
entries reach a plan. It acknowledged title-based orphan detection as a soft
check, but called its first three checks exact. Its actual path check searched
the whole tree by basename, and a matching date could suppress an orphan.
That establishes the earlier behavior and stated rationale, not why its author
selected those shortcuts. No contemporaneous alternatives experiment was found
in the sources sampled here.

The exact September 9 user statements are in `../USER-VISION.md` under
"UI scope and an auditable project history" and "fresh evaluation of prior
choices in future audits". The requests include a surface that can be
"audited and reflected upon" and the instruction "dont be swayed by prior
choices". These originals support inspectable history and reconsideration.
They do not require an index, embeddings, or replacement of the operating tool.

What changed on September 9 is the reproduced false verification described
above and the uncommitted Link 1 repair. The current operating candidate is
the working-tree exact resolver, not a published release. The earlier
"production script was not modified" statements describe the preceding
research pass and must not be read as current status after Link 1.

Current authority in `../AGENT-WORKFLOW.md` section 6 states: "Derived HTML,
caches, and indexes are not canonical truth." Section 7 states: "Discovery
never grants mutation or remote-upload authority." Those boundaries permit a
local disposable index but rule out treating inferred matches as accepted
relationships. `../SOURCE-TO-COURSE.md` keeps accepted files and local runtime
authority in place. This packet excludes new durable schemas and production
redesign. A later proposal may justify a schema change through the existing
owner and acceptance process. No boundary change is needed for this review.

### Concrete comparison

| Option | Present fitness against the criteria | Switching, compatibility, maintenance and recovery |
| --- | --- | --- |
| A: retain the working-tree exact resolver | Five synthetic tests pass for false matches, explicit roots, ambiguity, distinct same-date links, wrong targets and duplicate headings. It exposes unsupported coverage. The live corpus has zero verified downstream links, so it is a structural checker with weak legacy recall. | No additional switch for this checkout. Existing labels and zero exit status remain, but the downstream count has a narrower meaning. Plain-heading and inline-link parsing remain maintenance limits. Input bytes are checked unchanged in every synthetic case. |
| B: build a disposable local reference index with exact targets plus separately labeled prose candidates | Credible alternative for the requested history surface: each result would retain source path, location, fingerprint and match class. It could support navigation and broader candidate recall without granting prose matches authority. This is a design inference, not measured superiority. Exact resolution still needs A's safety properties. | Requires an extractor, invalidation, rebuild and coverage reporting. No new canonical relationship store is necessary. Source changes must invalidate derived results. Recovery would delete and rebuild the index. Implementation effort and latency are unmeasured. |
| C: restore the historical basename/date heuristic and make no further architecture change | Finds loose legacy mentions, but the inspected algorithm can mark an unrelated basename or shared date as verification. It fails the first criterion by construction. Its broad apparent coverage cannot establish exact relationships. | Retains the old report meaning and avoids index upkeep. Restoring it would discard Link 1's correctness repair. Low switching effort does not compensate for misleading verification. |

Expected benefit of A is fewer false assurances in structural audits, not more
complete history or improved learning. Expected benefit of B is navigable
legacy evidence with explicit uncertainty. C remains a historical comparator,
not a recommendation to undo the authorized repair. Past code effort and prior
acceptance contribute no quality score in this comparison.

### Contrary evidence, recommendation and revision path

Retain A for structural verification. Keep B as the already proposed issue 21
prototype, with no production adoption here. Do not restore C as a verifier.
This is a review recommendation owned by Weibao, not a new product commitment.

The strongest contrary observation is A's zero verified downstream links among
53 current vision entries. Ten paths are unresolved under its roots and four
are ambiguous. Eight title-text matches remain candidates. These counts do
not prove missing ideas or missing implementation. One local vision link is
unresolved and no planning files were unreadable in this run. The narrow parser
does not cover remote links, reference-style links or formatted headings.
Consequently A alone cannot satisfy the requested history experience.

The earlier isolated reproduction is inherited evidence from the preceding
pass, not a second independent experiment. The five-test rerun here is fresh
execution of the same fixtures. No index prototype, judged legacy recall
benchmark, latency comparison, unreadable-file failure injection, semantic
traceability review or human navigation exercise was performed. A failed
network attempt to read GitHub succeeded on the authorized read-only retry.
It is not evidence about any architecture option.

Revisit when issue 21's first real decision thread is assembled, before choosing
its retrieval or relationship representation. On that thread, judge exact
links and prose candidates separately, include same-date and same-basename
decoys, and modify one synthetic source to test invalidation and rebuild.
Evidence that would change this recommendation is B finding useful references
that A misses while preserving every false-match rejection and exposing stale
inputs. If A verifies an incorrect exact target, repair that defect before
using its result as evidence. If the history exercise gains nothing from B,
retain A plus manual source navigation and defer the index.

Revision path: the history owner records the measured comparison here or in
issue 21's existing owner, presents a bounded proposed change, and obtains
Weibao's acceptance before changing the operating representation. Preserve the
historical evidence and original files. Automated checks cannot establish
causal completeness, freedom from bias, human usability or aesthetic acceptance.

### Acceptance reconciliation

| Issue 22 criterion | Demonstration evidence and limit |
| --- | --- |
| Present needs first, then intent and authority | Criteria recorded before historical code inspection and ranking. Prior packet exposure is disclosed. Exact September 9 originals and current boundaries reconciled above. |
| Credible alternative and doing nothing | A, B and C compared. B is unbuilt. Visual label withholding is not applicable to this architecture exercise and remains untested. |
| Fitness separate from future cost | Separate table columns. No sunk effort counted as quality. |
| Contrary observations, dates and reconsideration | Zero verified legacy links, unsupported formats, inherited reproduction, fresh test rerun, unknowns and issue 21 revisit gate retained. |
| Real decision with explicit revision path | Historical heuristic and current exact resolver inspected. Retain recommendation is provisional and preserves the local operating choice. |

Verification on 2026-09-09: `python3 tests/vision_audit_roundtrip.py` passed all
five tests. `python3 scripts/vision_audit.py` exited zero with the counts above.
These checks verify the inspected implementation boundary, not option B or
human outcomes. The comparison is a local documentation deliverable. Publication
and GitHub closure remain outside this chain's authority.
