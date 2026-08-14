# Remaining open decisions from synthesis 12.6

**Status:** framed 2026-08-14. The three 14A-gating decisions are resolved in
`DECISIONS-PRE-14A-2026-08-14.md`. The eight below are the rest of synthesis
section 12.6. None blocks the Phase 14A plan; each is framed here so it is
decided deliberately at its owning subphase rather than rediscovered mid-plan.

Four of the eight change the product and are held for Weibao's decision. The
other four are technical calibrations: a recommendation is recorded and the
owning subphase confirms or overturns it with evidence. Recommendations are not
decisions; record each resolution under "Resolved" when made.

---

## Held for Weibao (product-changing)

### D-12.6-4. Solo self-acceptance authority and personal completion policy

**Owning subphase:** 15B (acceptance), touches 14A operation protocol.

**Question:** In a one-learner product, Weibao is learner, course builder, and
reviewer at once. When an agent drafts an artifact, who accepts it, and may the
same person who requested a change accept it without a second look? And who
defines what "course complete" means for a personal course?

**Options:**

- **A. Full self-acceptance.** Any drafted artifact can be accepted by Weibao in
  one action. Fastest; matches a one-user tool. Risk: the review step in the
  operation protocol becomes a rubber stamp, and a bad generated artifact enters
  accepted truth with no friction.
- **B. Risk-tiered self-acceptance.** Low-risk artifacts (notes formatting, a
  cosmetic theme, a derived view) accept in one action. Assessment-bearing or
  keyed artifacts (items, answer keys, blueprints, objective edits) require a
  deliberate second step: a rendered diff must be opened before the accept
  control enables, and the acceptance records that the preview was shown.
- **C. Cooling-off review.** Assessment-bearing artifacts cannot be accepted in
  the same session that generated them. Strongest guard, but hostile to a solo
  workflow and easy to resent into disuse.

**Recommendation:** B. It keeps the operation protocol honest (the review step
is real, not ceremonial) without making a solo product nag its one user. The
risk tiers reuse the existing authority vocabulary: anything the runtime treats
as keyed or evidence-bearing is high tier; everything else is low. Personal
completion policy follows the same shape: Weibao defines the completion
predicate per course, the runtime only reports whether the predicate's
evidence conditions are currently met, and the predicate is stored as course
data, never inferred.

**Resolved:** pending.

### D-12.6-5. Notes default placement and Evidence default prominence

**Owning subphase:** 16B (IA and flow), touches 16C (notes).

**Question:** Where do learner notes live by default in the IA (beside the
lesson, in a course notes area, or in a global notes surface), and how
prominent is the Evidence view in the default navigation?

**Options for notes placement:**

- **A. Margin-first.** Notes render beside or beneath the anchored lesson block;
  a course-level notes list is a derived view. Keeps notes in context; weakest
  for review-across-lessons.
- **B. Course-notes-first.** Notes live in a course notes surface; the lesson
  shows anchor indicators that jump there. Better for review; adds a navigation
  hop at capture time.
- **C. Margin capture, course review.** Capture happens in place at the anchor;
  the course notes surface is the review home and the durable listing. The
  cross-course global destination stays backburner per synthesis 12.2.

**Options for Evidence prominence:** primary navigation item beside
Learn/Practice/Test, or one level down inside Review.

**Recommendation:** C for notes, and Evidence as a primary navigation item.
The honest-evidence stance is a product differentiator; burying the Evidence
view one level down contradicts the "improved by honest evidence" north star.
Weibao should confirm because both choices shape daily feel, not correctness.

**Resolved:** pending.

### D-12.6-6. Formal-test pause policy

**Owning subphase:** 16B storyboard, but the policy itself is a runtime
contract clause and must be stated in runtime terms (synthesis section 8 lists
formal-test pause under fixed runtime authority).

**Question:** During a formal (blueprint-bound, frozen) test sitting, what does
pausing do? Life interrupts a solo learner constantly; the policy decides what
a resumed sitting is worth.

**Options:**

- **A. No pause.** A formal sitting runs to completion or is abandoned and
  recorded as abandoned. Strictest fidelity to timed-exam simulation; brutal
  for a solo learner at home.
- **B. Pause allowed, disclosure sealed.** The sitting can pause and resume;
  while paused, the runtime serves nothing (no item text visible, no navigation,
  no reveal), the clock stops, and the evidence record carries the pause count
  and total paused duration. A report can then say "this sitting was paused
  twice for 40 minutes" rather than pretending it was continuous.
- **C. Mode-dependent.** Timed blueprint sittings use A; untimed formal sittings
  use B. Two behaviors to explain, but each is honest for its mode.

**Recommendation:** C, with B's sealed-pause mechanics as the shared
implementation and A simply being B with pause disabled by the blueprint's
timing policy. Either way the runtime owns it: no surface or model may pause,
resume, or peek. Weibao should decide because it defines what his own exam
simulations are worth as evidence.

**Resolved:** pending.

### D-12.6-7. Trust persistence for executable sources

**Owning subphase:** 16A capability contract (executable notebook preview is a
16-track prototype), enforced by the runtime and operation manifest.

**Question:** When Weibao approves executing an executable source (a notebook
cell, a code artifact), how long does that trust last: one run, this file, this
fingerprint, or this root?

**Options:**

- **A. One run.** Every execution is approved individually. Safest; noisy
  enough that approval becomes reflexive clicking, which is its own failure.
- **B. Per fingerprint.** Approval binds to the exact content hash; any edit
  invalidates trust. Safe and precise; re-approval after every edit of one's
  own notebook is friction exactly where iteration is fastest.
- **C. Per file identity.** Approval binds to the durable file ID across edits.
  Convenient; an agent-modified cell inherits trust it was never granted.
- **D. Per root.** A whole folder is trusted. Matches how editors do workspace
  trust; far too coarse for sources an agent may write into.

**Recommendation:** B with one carve-out: edits made in-session by Weibao
himself (through the app's own editor, recorded in the operation journal)
carry trust forward to the new fingerprint; any other change path (external
edit, agent write, import) drops back to untrusted. This keeps the security
boundary exactly at "content Weibao has not seen since it last changed."
Product-changing because it decides how annoying the notebook loop feels.

**Resolved:** pending.

---

## Technical calibrations (recommendation recorded, owning subphase confirms)

### D-12.6-8. Metadata threshold between local lesson fields and course registries

**Owning subphase:** 14B (course package), rule inherited from D-14A-1.

**Recommendation:** reuse the resolved hybrid-graph rule as the metadata rule:
a field lives in the lesson file when it describes only that file's content
(title, style, local terms, its own objective tags); it lives in a course
registry when two or more independently-identified objects must agree on it
(objective definitions, level vocabulary, blueprint weights, rights grants).
Duplicating a registry value into a file for readability is allowed only as a
derived, regenerable annotation, never the source of truth.

**Resolved:** pending confirmation at 14B plan time.

### D-12.6-9. Rights representation when the user does not know

**Owning subphase:** 14B (rights are bound at source-binding time).

**Recommendation:** an explicit `rights: unknown` state, distinct from any
granted or denied state, defaulting to the restrictive behavior synthesis
section 11 already requires (read yes; quote, transform, remote-process,
package, export, share all refused until stated). The binding UI offers a
small closed vocabulary (owned, licensed, fair-use-claimed, unknown) plus a
free-text provenance note, and never guesses from file location or filename.
Unknown-rights refusals must name the missing grant so the fix is one edit.

**Resolved:** pending confirmation at 14B plan time.

### D-12.6-10. Representative large-collection corpus and performance budgets

**Owning subphase:** 14A tracer (discovery must be bounded and cancellable from
the first prototype).

**Recommendation:** build one synthetic corpus generator (no real content, guard
stays green) producing three sizes: 1k files / 10k files / 100k files across
nested roots with symlinks, permission-denied pockets, and duplicate
fingerprints. Budgets to hold: first useful discovery results under 2 seconds
on the 10k corpus; full inventory under 60 seconds on 100k; cancel responds
under 500 ms; memory bounded (streaming, no whole-tree in RAM). Numbers are
starting budgets to be measured against on real hardware at 14A, not promises.

**Resolved:** pending measurement at 14A.

### D-12.6-11. Minimum packaged offline help and diagnostics bundle

**Owning subphase:** 16B (help and error states), packaged at 17B.

**Recommendation:** ship inside the package, readable fully offline: the
format spec (`itembank spec` output), the command reference, the first-run
walkthrough, the recovery playbook (interrupted write, conflict, denied path,
restore), and a redacted diagnostics exporter (versions, settings with secrets
stripped, last operation-journal entries, no bank content, no evidence values).
Nothing in the bundle may require network or a model backend to be readable.

**Resolved:** pending confirmation at 16B plan time.

---

## Bookkeeping

When any decision above is resolved, fold it into the standing contract-delta
patch, and mark the matching 12.6 bullet closed in the synthesis with a
citation to this file, without deleting the open-decision record (same
procedure as `DECISIONS-PRE-14A-2026-08-14.md`).
