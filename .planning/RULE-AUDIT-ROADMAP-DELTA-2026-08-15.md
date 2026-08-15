# Proposed roadmap delta from the 2026-08-15 rule audit

**Status:** proposal for Weibao's scope decision. This file does not amend
ROADMAP.md.

## Proposal 1: add a three-tier process rule

Add a planning-governance clause that scales record shape to consequence:

1. Reversible, low-stakes work records intent, owner, next action, and undo for
   mutations. It does not require a permanent disposition row or full operation
   manifest.
2. Consequential proposals and durable writes use the existing disposition,
   authority, rights, validation, recovery, and accepted-revision controls.
3. Binding formats, assessment authority, rights or egress changes, hard
   rejections, and milestone scope use the full evidence, prototype, ledger,
   readiness, and direct-user-decision gates.

The tier changes documentation burden only. It does not relax one-parser and
one-scorer authority, accessibility, data residency, rights, compare-and-swap,
validation, or recovery rules.

**Suggested owner:** planning governance before the next large research wave.

**Verification:** apply the three tiers to one trivial maintenance task, one
durable file operation, and one schema or roadmap decision. Confirm the low
tier loses no recovery information and the other two preserve current gates.

**Failure condition:** two reviewers classify the same operation into different
tiers, or the low tier permits an irreversible or externally visible change.

## Proposal 2: route reopened dependency decisions without changing sequence

- Place IL-20260815-09's supply-chain policy before the first plan that adopts a
  new runtime dependency.
- Evaluate IL-20260815-07's PDF and DOCX intake candidates in the first source
  intake phase that encounters those formats. Keep locator fidelity and rights
  behavior as gates.
- Evaluate IL-20260815-08 when the next phase adds tests.
- Leave IL-20260815-10 trigger-based on deeper Anki import need.
- Resolve IL-20260815-11 during Phase 18 planning.

These are gates or bounded research tasks, not a request for a new top-level
phase. The current milestone sequence need not change unless dependency or
locator research fails.

## Decision requested

Approve, revise, or reject Proposal 1. Proposal 2 can be accepted as routing
within existing phases unless Weibao prefers explicit roadmap rows.
