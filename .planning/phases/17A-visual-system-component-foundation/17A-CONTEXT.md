# Phase 17A: Visual System & Component Foundation - Context

**Gathered:** 2026-08-16
**Status:** Ready for UI-phase and planning

> Gathered under PLANNING-DIRECTIVES.md §2 (autonomy rule) in a non-interactive
> session: gray areas were resolved from the recorded research, specs, and code
> rather than by blocking questions. Every decision below cites its basis. The
> one decision the synthesis explicitly reserves for Weibao (default visual
> direction) is recorded as a checkpoint, not decided here.

<domain>
## Phase Boundary

17A delivers the visual system and component foundation: the token freeze
(color, type, spacing, radius, measure), typographic hierarchy, the responsive
shell, and accessible primitives for every component named by 16B and 16C. It
depends on 16B and 16C. Its freeze gate is the same-flow visual comparison
(one synthetic lesson-plus-practice flow rendered in three visual directions)
plus the accessibility QA pass (A11Y-01). Scope anchor: `ROADMAP.md:112` and
the subphase table at `ROADMAP.md:2268`.

Not in 17A: new runtime capability, new IA or navigation (frozen in 16B), new
strategies or note semantics (frozen in 16C), and the 17B production vertical
tracer. 17A styles and freezes what 16B/16C specified; it does not re-decide
their structure or copy. Voice assignment follows "who authored the string,
never visual preference" (`16B-UI-SPEC.md:48`).

</domain>

<decisions>
## Implementation Decisions

### Token freeze scope and proof

- **D-01:** The freeze covers the existing token layer as the base: the color
  tokens in `surfaces/theme.py` (BASE_TOKENS, SEMANTIC_TOKENS, accent
  derivation with enforced contrast) and the non-color tokens in
  `surfaces/presentation.py` SHARED_CSS (four vendored font faces,
  `--space-1..7`, `--measure-prose`/`--measure-wide`, `--r-1/2/3`), plus
  whatever tokens the winning visual direction adds. The freeze is proven on
  served bytes via fixtures, not on documentation promises.
  **Reversibility:** one-way once frozen; downstream 17B and every authored
  artifact renders against these names, so renaming after the freeze is a
  migration, which is exactly why the freeze gate exists.
- **D-02:** `surfaces/day.py` must be brought under
  `presentation.surface_shell` before the freeze gate closes. It is the one
  served route that bypasses the token layer (`surfaces/day.py:1462`,
  `STATE.md:562-566`, reported by `tests/stylesheet_roundtrip.py:110`). A
  route that declares zero of the four fonts makes the token freeze
  unprovable on served bytes. This migration is an in-scope 17A prerequisite,
  not deferred debt. **Reversibility:** costly; DAY_CSS duplicates layout
  the shell owns, and unwinding a half-migration touches every day-page test.
- **D-03:** Phase 13.5 waves 3 through 7 remain unstarted and overlap 17A
  (quiz size-scale collapse "twelve sizes to five", `--edge`, gloss
  placement, live regions; `STATE.md:531-541`). Ruling: token-touching 13.5
  items (the size-scale collapse and `--edge`) fold into 17A so the scale is
  frozen once, in one place. Non-token 13.5 items (gloss placement, scroll
  contract, wrong-answer surface, live regions) stay owned by 13.5. The 17A
  plans must state this ordering explicitly and must not silently duplicate a
  13.5 task.

### Three-direction prototype and direction choice

- **D-04:** Reversible prototypes of the same synthetic flow in all three
  directions (Structured Studio, Quiet Workbench, Guided Canvas) precede any
  token freeze. The flow is already specified: shelf resume, source-linked
  objective, long lesson with definition/warning/table/cited image/inline
  prediction/check, wrong answer with entitled feedback and retry, evidence
  review with sparse data and a pending prose mark, AI-proposed lesson change
  with citations and diff, agent and offline status
  (`.planning/research/phase-16/10-visual-experience-system.md:251-262`,
  VISUAL-01 fixture at `REQUIREMENTS.md:859-864`). All three must project the
  same semantic flow. **Reversibility:** the prototypes themselves are
  required to be reversible; skipping them makes the freeze one-way on an
  untested choice, which PLANNING-DIRECTIVES.md §3a forbids.
- **D-05 (user checkpoint, not decided):** The default visual direction is
  chosen by Weibao after seeing the three prototypes. The synthesis reserves
  this decision explicitly (`14-synthesis.md:1060-1061`). Working hypothesis
  for prototype effort allocation: Structured Studio with Quiet Workbench
  density and bounded Guided Canvas elements, per `UI-SPEC.md:786-793`, which
  supersedes research report 10's Quiet Workbench recommendation. The plans
  must place a `checkpoint:decision` between prototype completion and the
  token freeze; no plan may treat the UI-SPEC hypothesis as the frozen answer.
- **D-06:** The roughly fifteen rendering decisions 16B and 16C deferred to
  17A (CourseShelf scroll-vs-clip, ActivityView long job lists,
  FirstLaunchWalkthrough narrow copy, SettingsPanel long root paths without
  mid-path ellipsis, NoteCapturePanel scroll-vs-grow, NotesPanelEvidence
  grouping, ProgressComprehensionDisplay long lists, NoteOutputTrio node
  labels, anchor-state chips, fill-state glyphs) are decided as
  direction-neutral rules applied identically across all three prototypes, so
  they cannot contaminate the direction comparison. Each gets an explicit
  written ruling in the 17A plans; none is left to executor judgment
  (lesser-model executor bar, PLANNING-DIRECTIVES.md §5).
- **D-07:** The token-abuse fixture (VISUAL-02, `REQUIREMENTS.md:865-878`) is
  part of the freeze gate: out-of-bounds density, measure, and palette tokens
  applied over the same-flow comparison must clamp to safe ranges with every
  fixed rule holding.

### Shell target

- **D-08:** The browser-served UI is the single canonical shell. The packaged
  desktop app wraps the same served pages in a frameless window (the Phase 13
  packaging path); there is no second UI codebase. This resolves the open
  question ROADMAP.md:114 routed to 16B/17A planning. Basis: directive §3
  (a second presentation is a registration behind one interface, never a
  fork), the surface-parity rule (route plus CLI, one runtime), and the
  existing daemon architecture. **Reversibility:** costly; a native second
  shell would re-implement every component and re-run every accessibility
  gate, which is the two-parsers shape the directives reject.

### Accessibility QA mechanism

- **D-09:** A layout-capable verification mechanism is a prerequisite for the
  freeze gate, because jsdom does no layout and gates 4, 5, 10, 11 need a
  driven browser or a human (`STATE.md`). Ruling: a dev-only driven-browser
  harness is permitted under the 2026-08-09 constraint relaxation (dev
  dependency, pinned and vendor-reviewed per the supply-chain rule, never
  shipped in the runtime), paired with a scripted human QA pass. AI never
  self-certifies accessibility; Weibao is the acceptance authority for
  A11Y-01, including the deliberately hover-only variant that must fail
  equivalence review (`REQUIREMENTS.md:719-730`).
- **D-10:** The configurable-versus-fixed split at `UI-SPEC.md:796-802`
  carries forward locked and is not reopened: configurable is palette,
  density, measure within safe bounds, approved local fonts, modest surface
  treatment, optional motion; fixed is hierarchy, status meaning, focus
  visibility, contrast, keyboard order, target size, zoom and reflow, reduced
  motion, non-color cues, source and acceptance visibility, and semantic
  equivalence across widths. Authors select semantic roles, never raw colors,
  shadows, coordinates, arbitrary icons, or animation.

### Sequencing constraints

- **D-11:** The standing halt condition holds: no 14B-or-later freeze closes
  before the Phase 13.9 walking skeleton has been walked (`ROADMAP.md:104`).
  17A's freeze gate is subject to it. The plans may build everything up to
  the gate, but the gate itself waits.
- **D-12:** 17A introduces learner-facing visual surfaces, so
  `/gsd-ui-phase 17A` is owed before `/gsd-plan-phase 17A`
  (PLANNING-DIRECTIVES.md §6 and §8).

### Claude's Discretion

- Exact token names for anything the winning direction adds, provided they
  extend the existing `--space-*`/`--measure-*`/`--r-*`/semantic-color naming
  rather than introducing a parallel scheme.
- Prototype implementation vehicle (static fixture pages versus served
  routes), provided prototypes stay reversible and are not accepted as
  production components without review.
- Choice of driven-browser harness tool, within the supply-chain rule
  (pinned version, recorded checksum, named license review, dev-only).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Scope and governance
- `.planning/ROADMAP.md` §Phase 17A (line 112), subphase table (line 2268), shell-target note (line 114), standing halt (line 104), Extensibility Rules (lines 1094-1140)
- `.planning/PLANNING-DIRECTIVES.md` §2, §3, §3a (prototype mandate, line 177), §5 (lesser-model executor bar), §8 (subphase table)
- `.planning/SOURCE-TO-COURSE.md` (binding milestone scope)
- `.planning/PLAN-TEMPLATE.md` (plans start from this template)

### Visual and accessibility contracts
- `.planning/UI-SPEC.md` §7 (theming), §8 lines 580-601 (LOCKED responsive contract and the nine accessibility gates), §9.3 lines 786-793 (direction hypothesis), lines 796-802 (configurable versus fixed, LOCKED), §11 lines 634-641 (verification gates, responsive snapshots at 1280/768/375)
- `.planning/REQUIREMENTS.md` VISUAL-01 (lines 859-864), VISUAL-02 (lines 865-878), A11Y-01 (lines 719-730)
- `.planning/research/phase-16/10-visual-experience-system.md` lines 251-262 (the specified comparison flow), line 739 (superseded Quiet Workbench recommendation, kept for the ledger)
- `.planning/research/phase-16/14-synthesis.md` sections 9.3, 15, line 945 (prototype mandate), lines 1060-1061 (the reserved user decision), line 968 (gate mapping G8/G4/G11)

### Inherited component contracts
- `.planning/phases/16B-ia-modes-recovery-contract/16B-UI-SPEC.md` (structural and copy contract; deferral table at line 593; held-out visual tests at lines 495, 503, 529, 535-536)
- `.planning/phases/16C-strategies-notes-prototype-convergence/16C-UI-SPEC.md` (deferrals at lines 404, 587, 592, 610, 615, 670, 676)
- `.planning/phases/16B-ia-modes-recovery-contract/16B-VALIDATION.md` line 142 (open items 17A owns)

### Code and state
- `surfaces/theme.py` (the color token layer, contrast enforcement, theme_css)
- `surfaces/presentation.py` (SHARED_CSS non-color tokens, surface_shell, primitives)
- `surfaces/day.py` line 1462 (the token-layer bypass D-02 removes)
- `tests/stylesheet_roundtrip.py` line 110 (REPORTED_FONT_ROUTES)
- `.planning/STATE.md` (13.5 waves 3-7 status lines 531-541, day-page debt lines 562-566, vendored-font record line 450)
- `.planning/phases/13.5-reading-teaching-surface-quality-pass/` (unstarted waves that D-03 partitions)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `surfaces/theme.py`: complete light/dark color token system with
  code-enforced contrast (TEXT_CONTRAST 4.5, FOCUS_CONTRAST 3.0), accent
  derivation, settings surface with preview. 17A extends it; it does not
  rebuild it.
- `surfaces/presentation.py` SHARED_CSS: fonts, spacing scale, measures,
  radii already exist as CSS custom properties; `surface_shell` composes
  theme plus shared CSS and is the shell every route should pass through.
- Vendored fonts (Source Serif 4, iA Writer Quattro) and KaTeX under
  `vendor/`, OFL/pinned/checksummed per the supply-chain rule; the
  nested-route `@font-face` URL defect is already fixed.

### Established Patterns
- One palette owner: literal hexes exist only in `surfaces/theme.py` (plus
  one in `surfaces/cli.py`); every surface must consume tokens.
- Registry-over-if-chain (Extensibility rule 2) and stub-proven extension
  points (rule 6) apply to any renderer or direction registry 17A adds.
- Surface parity: every capability keeps a daemon route and a CLI command;
  presentation-only behaviors need an accessible equivalent, not a command.

### Integration Points
- `surface_shell` is where the responsive shell lands; the day page is the
  one route not yet behind it (D-02).
- `tests/stylesheet_roundtrip.py` already asserts served-bytes font/token
  coverage; the freeze fixtures extend this pattern.
- The 16B/16C component inventory (CourseShelf, ActivityView, SettingsPanel,
  FirstLaunchWalkthrough, StatusNotice, NoteCapturePanel, NotesPanelEvidence,
  StrategyPicker, ProgressComprehensionDisplay, NoteOutputTrio) is the
  component list 17A styles.

</code_context>

<specifics>
## Specific Ideas

- The three directions have names and definitions already: Structured Studio,
  Quiet Workbench, Guided Canvas (research report 10, synthesis 9.3). The
  prototypes must render the one specified flow, not three arbitrary demos.
- `UI-SPEC.md:485` still reads "Status: NOT ADOPTED" for vendored fonts while
  the code has both faces vendored and shipped; the doc is stale relative to
  the repo and should be corrected when §7 is touched during 17A.

</specifics>

<deferred>
## Deferred Ideas

- Interactive graphic rendering of the concept map beyond the
  keyboard-traversable structure: 16C marks it "Phase 17A and later"
  (`16C-UI-SPEC.md:676`). 17A owes only the accessible textual adjacency
  structure and whatever the winning direction affords cheaply; a full
  interactive graph canvas may extend past 17A without failing the gate.
- Non-token Phase 13.5 items (gloss placement, scroll contract, wrong-answer
  surface, live regions) stay in 13.5 per D-03.
- Signed binaries, compiled shells, and any native second UI remain out of
  scope per PROJECT.md and D-08.

</deferred>

---

*Phase: 17A-Visual System & Component Foundation*
*Context gathered: 2026-08-16*
