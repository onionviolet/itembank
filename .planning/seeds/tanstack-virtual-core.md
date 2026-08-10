---
title: Vendor @tanstack/virtual-core for long-list virtualization
trigger_condition: A real list in a real surface exceeds 1000 rows AND scroll or first-paint is measured slow on the target machine
planted_date: 2026-08-10
status: planted
---

# Seed: vendor `@tanstack/virtual-core`

## The idea

Vendor one 23 KB file to virtualize a long list, rendering only the visible window
of rows instead of the whole set.

## Measured facts, 2026-08-10 (jsDelivr)

- `@tanstack/virtual-core` **3.17.7**, **23 KB minified, zero imports**.
- Ships as ready ESM via jsDelivr `/+esm`. **One vendorable file. No bundler, no
  npm at runtime, no React.**
- This is the only TanStack package that survives §4a merit review. See
  `.planning/notes/2026-08-10-tanstack-verdict.md` §5.

## The trigger, and why it is measured rather than guessed

Candidate long lists, none of which exist yet:

- Phase 11 curriculum auditor coverage output (one row per objective).
- Phase 1 evidence history for one objective over a full term.
- Phase 3.1 long lesson reader with many rich blocks.

**Do not adopt pre-emptively.** Their real sizes are unknown, and a browser renders
a plain 1000-row semantic table faster than most people expect. The trigger is a
measurement on the target machine, not an anticipation.

## Cheaper things to try first, in order

1. Paginate or scope the list (an auditor report for one subject, not all three).
2. `content-visibility: auto` plus `contain-intrinsic-size`, which is pure CSS,
   zero bytes, and often sufficient.
3. Only then virtualize.

## The cost that is not the file size

Virtualization removes rows from the DOM. That breaks browser find-in-page, breaks
screen-reader sequential navigation unless `aria-setsize` and `aria-posinset` are
set correctly on every rendered row, and interacts badly with `UI-SPEC.md` §8's
keyboard gates. **The accessibility work is the real cost, not the 23 KB.** Any
plan adopting this ships the ARIA attributes in the same commit or does not ship.

## Vendoring terms

Follow the KaTeX precedent (`09-03-PLAN.md`) exactly, per Directive §4a's
supply-chain rule: pinned version, recorded checksum, named license review,
committed file. No CDN reference at runtime.

## Related

- `.planning/notes/2026-08-10-tanstack-verdict.md`
- `UI-SPEC.md` §8 Responsive, Offline, and Accessibility Contract
- `ROADMAP.md` Phase 10, Phase 11
