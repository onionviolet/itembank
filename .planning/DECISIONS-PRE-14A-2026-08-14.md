# Gating decisions to resolve before Phase 14A

**Status:** teed up 2026-08-14. These three open decisions from synthesis
section 12.6 are 14A/14B schema choices, not implementation details. They must be
resolved before the Phase 14A plan, because 14A freezes the identity and graph
foundation everything else composes onto. The remaining 12.6 decisions can ride
their own subphase and are not blocking.

Each decision below records the framing, options, tradeoffs, and a recommendation.
The recommendation is not the decision; record the resolution under "Resolved"
when made.

---

## D-14A-1. Graph storage: Markdown-embedded vs. readable sidecar, and the minimal edge vocabulary

**Question:** Where do the typed graph records (objectives, prerequisites,
source/treatment bindings, typed relations) live, and what is the smallest edge
vocabulary Phase 14 needs?

**Why it gates 14A:** the identity, revision, and operation-journal work in 14A has
to know what object it is versioning and fingerprinting. If the graph is embedded
in lesson Markdown, edges move and fingerprint with the file; if it lives in a
sidecar, edges have their own identity and change-detection. This choice sets the
compare-and-swap unit.

**Options:**

- **A. Edges embedded in the canonical Markdown** (frontmatter or a fenced block
  per file). Pro: one file is the whole truth; portability is trivial; Obsidian
  reads it. Con: cross-file edges (prerequisite from lesson X to objective Y) have
  no single home; a graph query must parse every file; moving a file rewrites edge
  data.
- **B. Readable course sidecar holds the graph; files hold local metadata only.**
  Pro: cross-file edges have one home and one fingerprint; graph queries do not
  scan every file; matches the "course manifest composes existing contracts"
  rule. Con: two things to keep consistent; the sidecar must stay human-readable
  and never become the only understandable copy (hard-reject if it does).
- **C. Hybrid: local edges (this lesson's terms, its objective tag) inline;
  cross-object edges (prerequisites, source bindings) in the sidecar.** Pro:
  keeps each edge where its identity naturally lives. Con: two edge locations to
  reason about; the split rule must be unambiguous.

**Recommendation:** C (hybrid), with the sidecar in a readable, diffable format
and an explicit rule: an edge lives inline when it is wholly owned by one file's
content, and in the sidecar when it relates two independently-identified objects.
This satisfies portability (each file still means something alone) and the
manifest-is-an-index rule (cross-object graph has one queryable, fingerprintable
home), and it avoids the "derived index is the only readable copy" hard-reject.

**Minimal 14 edge vocabulary to confirm:** `prerequisite-of`, `covers-objective`,
`source-supports`, `treatment-of`. Everything else (alternate-path, cross-lists,
supersedes) is registered later, not frozen in 14.

**Resolved (2026-08-14):** Option C, hybrid. An edge lives inline when it is
wholly owned by one file's content; it lives in the readable course sidecar when
it relates two independently-identified objects. Sidecar stays diffable and never
becomes the only readable copy. Minimal 14 edge vocabulary as listed above; other
relations register later, not frozen in 14.

---

## D-14A-2. Durable identity granularity and fingerprint normalization

**Question:** What is the smallest object that gets a stable opaque ID, and how is
the change-detection fingerprint normalized?

**Why it gates 14A:** identity is the floor. The rejection ledger hard-rejects
hash/path/display-name as durable identity and ambiguous auto-merge. The research
independently found that content-hash-as-ID silently orphans a learner's evidence
history on every edit. So the ID must be opaque and assigned once; the content
hash is stored alongside as a change field, never as the key. What remains open is
the granularity and the normalization rule.

**Options for granularity:**

- **A. Object-level IDs only** (course, objective, source, lesson, bank, item).
  Simple; matches shipped item identity. Con: a lesson-internal block (a
  callout, a worked example) cannot be addressed, linked, or independently
  revised.
- **B. Object-level plus addressable component IDs for blocks that carry
  evidence or citations** (items already have IDs; add IDs to lesson blocks that
  are cited, gated, or evidence-bearing). Con: more IDs to mint and migrate.

**Options for fingerprint normalization:** decide what is normalized out before
hashing so that a meaningless reformat does not read as a content change:
trailing whitespace, line-ending style, and (open question) Markdown-insignificant
reflow. Keyed assessment content is never normalized in a way that could mask a
scoring-relevant change.

**Recommendation:** B, but bounded: mint component IDs only for blocks that are
cited, gated, or evidence-bearing, not for every paragraph. Normalize trailing
whitespace and line endings only for the first cut; defer reflow normalization to
the 14A file-fault tracer, where a real diff corpus shows whether it is needed.
Keep the opaque-ID-plus-fingerprint-plus-revision shape from the ledger exactly.

**Resolved (2026-08-14):** Option B, bounded. Object-level opaque IDs for
course/objective/source/lesson/bank/item, plus component IDs only for lesson
blocks that are cited, gated, or evidence-bearing (not one ID per paragraph).
Fingerprint normalizes trailing whitespace and line endings for the first cut;
reflow normalization is deferred to the 14A file-fault tracer where a real diff
corpus decides. Keyed assessment content is never normalized in a way that could
mask a scoring-relevant change.

---

## D-14A-3. Rename the `mastered` evidence field

**Question:** The shipped evidence support currently called `mastered` implies a
mastery claim the honest-progress model forbids. What replaces it?

**Why it gates 14A (lightly):** it is a naming/migration decision that touches the
evidence contract, and the honest-progress display (16B) should not inherit a
field named for a claim it is not allowed to make. Deciding now avoids a rename
migration mid-flight and a fake "mastery" leaking into the UI. One aggregate
mastery score is hard-rejected; a recall-probability surfaced as a percentage is
also rejected.

**Options:**

- **A. `evidence_support`** — neutral, names what it is (accumulated valid
  response evidence for an objective), makes no readiness claim.
- **B. `retrieval_evidence`** — ties it to the retrieval construct; risks being
  read as FSRS retrievability, which must not surface as a percentage.
- **C. Keep `mastered` internally, forbid surfacing it** — least migration, but
  leaves a misleading name in the contract that a future surface may leak.

**Recommendation:** A (`evidence_support`), with a recorded migration mapping old
`mastered` reads to the new field and a note that the shipped evidence tests must
stay byte-compatible where required (audit item A6). Reject C: the ledger's own
logic is that a misleading name eventually leaks.

**Resolved (2026-08-14, user redirect):** The decision is not a single neutral
rename; adopt a Khan-Academy-style model. Progress is a **per-objective,
self-adjustable fill state** shown as filled-in blocks (completed / filled in /
done), able to move up and down as evidence and retention change. It is not a
permanent knowledge claim.

The exact field token is low-stakes ("call it whatever"); the semantics are the
decision. Default working name `evidence_support` for the stored field, with a
display-layer concept of a filled/completed unit. Rename remains cheap because it
is not surfaced as its own claim.

**Boundary that keeps this compatible with the honest-progress hard-reject:** the
hard-reject (synthesis 12.4) bans **one aggregate mastery/completion score** and
bans participation-as-mastery. A Khan-style filled block is allowed because it is
(1) **per objective**, not one rolled-up number; (2) driven by **valid response
evidence**, not clicks/time/streaks; and (3) **adjustable, can un-fill**, so it
never asserts false permanence. A "100%" or fully-filled unit therefore means
"this objective's evidence bar is currently full," never "the learner has
mastered the field." Retrievability still must not surface as a raw percentage
(D display uses the fill metaphor, not a probability number).

**Open sub-question routed to 16B:** the fill thresholds and how many evidence
levels a block shows (Khan uses Attempted / Familiar / Proficient / Mastered).
Decide the level vocabulary during the honest-progress display work, not now.

---

## After all three are resolved

- Fold the resolutions into the contract-delta patch produced by the readiness
  audit (`READINESS-AUDIT-14A.md`).
- Update synthesis section 12.6 to mark these three decisions closed, citing this
  file, without deleting the open-decision record.
- Then, and only then, plan Phase 14A.
