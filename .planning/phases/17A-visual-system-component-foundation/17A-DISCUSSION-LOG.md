# Phase 17A: Visual System & Component Foundation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md; this log preserves the alternatives considered.

**Date:** 2026-08-16
**Phase:** 17A-visual-system-component-foundation
**Areas discussed:** Token freeze scope and proof, Three-direction prototype and direction choice, Shell target, Accessibility QA mechanism, Sequencing (13.5 overlap and standing halt)
**Mode:** Autonomous under PLANNING-DIRECTIVES.md §2. The session was
non-interactive; no AskUserQuestion calls were made. All areas were selected
and resolved from recorded research, specs, and code, with assumptions
recorded. The one decision the synthesis reserves for Weibao (default visual
direction) was left open as a plan checkpoint rather than decided.

---

## Token freeze scope and proof

| Option | Description | Selected |
|--------|-------------|----------|
| Freeze on documentation | Declare the token set in UI-SPEC and call it frozen | |
| Freeze proven on served bytes | Fixtures assert every served route consumes the token layer; day.py migrates first | ✓ |
| Freeze with day.py waived | Freeze while /day/sample_plan stays outside surface_shell | |

**Basis:** STATE.md records the day-page bypass as "needs an owning plan," and
a freeze that a served route violates on day one is not a freeze. Fixture
pattern already exists in tests/stylesheet_roundtrip.py.
**Notes:** 13.5 waves 3-7 partitioned: token-touching items fold into 17A,
the rest stay in 13.5 (D-03).

---

## Three-direction prototype and direction choice

| Option | Description | Selected |
|--------|-------------|----------|
| Skip prototypes, adopt Structured Studio now | UI-SPEC 9.3 already names a hypothesis | |
| Reversible three-direction prototypes, then Weibao chooses | Mandated by directives §3a, synthesis line 945, VISUAL-01; direction choice reserved at synthesis 1060-1061 | ✓ |
| Build all three as permanent registered directions | Directive §3 conflict rule | |

**Basis:** The prototype mandate is binding. Building all three permanently
was not chosen now because the synthesis reserves a default choice for the
user first; registration of a second direction stays possible later under §3.
**Notes:** The ~15 deferred rendering decisions from 16B/16C are decided as
direction-neutral rules so the comparison stays fair (D-06).

---

## Shell target

| Option | Description | Selected |
|--------|-------------|----------|
| Browser-served UI, packaged app wraps the same pages | One codebase, one accessibility surface, matches daemon architecture and Phase 13 packaging | ✓ |
| Native packaged UI first | Second component implementation, second QA surface | |
| Two shells maintained in parallel | The two-parsers shape directives reject | |

**Basis:** ROADMAP.md:114 routed this to 16B/17A planning; 16B closed without
it. Directive §3 qualification: a design that cannot share the contracts is
picked, not doubled. A native shell re-runs every gate for no product gain at
one user.

---

## Accessibility QA mechanism

| Option | Description | Selected |
|--------|-------------|----------|
| jsdom-only assertions | Cannot do layout; gates 4, 5, 10, 11 unreachable | |
| Dev-only driven-browser harness plus scripted human QA | Permitted under 2026-08-09 relaxation; supply-chain rule applies; Weibao is acceptance authority | ✓ |
| Human-only QA | Works but unrepeatable per commit; kept as the acceptance layer on top | |

**Basis:** STATE.md records the layout-gate limitation. A11Y-01 forbids AI
self-certification either way, so the harness informs and the human accepts.

---

## Sequencing

| Option | Description | Selected |
|--------|-------------|----------|
| Ignore 13.5 and the 13.9 halt | Risks duplicate work and an invalid freeze | |
| Record both as binding constraints in CONTEXT.md | D-03 partitions 13.5; D-11 subjects the gate to the 13.9 walking-skeleton halt | ✓ |

---

## Claude's Discretion

- New token naming (extend existing schemes only)
- Prototype vehicle (static fixtures versus served routes), reversibility required
- Driven-browser tool choice within the supply-chain rule

## Deferred Ideas

- Interactive concept-map graphic beyond the keyboard-traversable structure (16C marks it "17A and later")
- Non-token 13.5 items remain in 13.5
- Stale UI-SPEC.md:485 vendored-font status line to be corrected when §7 is touched
