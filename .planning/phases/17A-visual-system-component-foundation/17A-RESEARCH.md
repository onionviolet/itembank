# Phase 17A Research: Visual System and Component Foundation

**Researched:** 2026-08-16
**Scope:** implementation approach, sequencing, risks, and verification

## Recommendation

Build one reversible served prototype route containing the complete VISUAL-01
flow, render it through three direction stylesheets over identical semantic
HTML, and place the user direction checkpoint before any production token
freeze. After selection, land the shared type and density tokens, migrate the
day surface through `presentation.surface_shell`, style the inherited 16B and
16C primitives, then close with browser evidence and human A11Y-01 review.

This preserves one browser-served shell, one semantic component tree, and one
token owner. The packaged app continues to wrap the same pages.

## Existing foundation

- `surfaces/theme.py` owns light and dark base and semantic colors, accent
  derivation, 4.5:1 text contrast, 3:1 focus contrast, and `--edge`.
- `surfaces/presentation.py` owns the four vendored font faces, spacing,
  measure, radius, voice, and the shared `surface_shell`.
- `tests/stylesheet_roundtrip.py` already checks served stylesheet bytes,
  token resolution, font routes, and semantic contrast. Extend this proof
  rather than creating another stylesheet parser.
- `surfaces/day.py` is the remaining shell bypass. Its `theme_css + DAY_CSS`
  assembly must be replaced with shared-shell composition before freeze.
- Phase 13.5 is now executed through plan 09. Its token work is therefore a
  baseline to verify, not an unstarted body of work to duplicate. The 17A
  context's older status statement is superseded by the on-disk summaries.

## Plan shape

1. Tracer and preconditions: verify upstream freeze inputs, inventory current
   served bytes, add the synthetic VISUAL-01 route and deterministic fixture.
2. Three-direction comparison: implement direction-only CSS variants, all
   direction-neutral overflow and disclosure rules, visual snapshots, and a
   blocking choice by Weibao.
3. Token and shell freeze candidate: apply the selected direction, freeze five
   type tokens and bounded density tokens, migrate `day.py`, and prove every
   served route consumes the same token layer.
4. Accessible primitives: style the inherited 16B and 16C component inventory
   with fixed state meaning, 44px targets, keyboard order, wrapping, reflow,
   reduced motion, and static fallbacks.
5. QA and freeze: run the driven-browser matrix at 1280, 768, and 375 pixels,
   run the deliberately failing hover-only case, require scripted human review,
   and write a freeze record only when Phase 13.9 and every gate are green.

## Tooling decision

Use a pinned dev-only Playwright harness only if no already-pinned layout
driver exists when execution begins. Record version, checksum, license, and
non-shipping status before installation. If supply-chain approval is not
available, stop at that task rather than replacing layout checks with DOM-only
claims. Python unit and served-byte checks remain stdlib-only.

## Risks and mitigations

- Direction styles can drift semantically. One HTML fixture and a structural
  fingerprint across all directions makes this a test failure.
- A prototype can accidentally become production. Keep it under a synthetic
  fixture route and require the direction checkpoint before promotion.
- Token freeze can hide literal CSS. Scan served bytes and source for forbidden
  raw sizes/colors outside the token owners, with explicit allowlists.
- Day migration is costly. Isolate it in its own task and preserve route,
  content, and behavioral tests before changing composition.
- Browser automation cannot certify accessibility. It supplies repeatable
  evidence; the human checkpoint owns A11Y-01 acceptance.
- Upstream phases are planned but may not be executed. Every implementation
  plan names its upstream artifact preconditions and degrades synthetic
  components when real backing modules are absent.

## Verification strategy

The freeze evidence bundle contains served-byte token tests, structural parity
hashes for three prototypes, responsive screenshots, keyboard traversal logs,
contrast and target-size reports, reduced-motion and 200 percent zoom results,
the expected failure of the hover-only fixture, human review sign-off, and a
guard result proving no real bank entered the repository.

## Planning constraints

- Requirements: VISUAL-01, VISUAL-02, A11Y-01.
- Decisions D-01 through D-12 in `17A-CONTEXT.md` are binding.
- The visual direction decision is one-way at freeze and therefore requires a
  blocking checkpoint.
- No new runtime authority, IA, note semantics, strategy semantics, icon set,
  native shell, or non-token Phase 13.5 behavior belongs in this phase.
