# Style discipline: semantic transformation vs cosmetic theme

**Status:** resolved 2026-08-14 as planning input to 16A (capability contract)
and 16C (notes and output modes). Sources: synthesis 12.2 registered output
modes, `research/phase-16/06-feature-style-atlas.md` sections 4.3, 5.1 to 5.3,
`research/2026-08-10-lesson-style-catalogue.md`, and the shipped Phase 03.1
style registry.

**The rule (binding for 16A):** a style is a **semantic transformation** when it
changes required structure or the learner's action, and it then must declare its
own validator profile and compose from the shared note schema and semantic
relations. A style is a **cosmetic theme** when it changes look only, and it
then ships as design tokens with no validator and no new parsed structure.
Nothing may sit between: a "theme" that quietly requires structure is a
misclassified semantic style, and the atlas warning stands that two-column
styling alone does not make Cornell notes.

A corollary from the shipped architecture: a semantic style is a validator plus
a projection over the one parsed content model. It never introduces a second
parser, second renderer, or second content truth (Planning Directives 4.2, the
runtime non-negotiables).

## Classification

### Note output modes (synthesis 12.2): all ten are SEMANTIC

Every note output in atlas 4.3 has its own primary job, required structure,
learner action, and validation focus, so all ten are semantic transformations:

| Output mode | Validator focus (from atlas 4.3) |
|---|---|
| Notebook page | ownership, anchors, provenance |
| Hierarchical outline | coverage and hierarchy |
| Cornell notes | every cue maps to notes; linear degradation |
| Concept map | every edge typed; textual adjacency fallback |
| Glossary | unique identity, collisions, citation |
| Formula sheet | units, domains, symbol collisions, source |
| Timeline | date precision, disputed dates, no false causation |
| Comparison table | same criteria, explicit unknown cells, citations |
| Study guide | blueprint alignment and omissions |
| Source-extracted notes | text fidelity, locator, source version |

### Lesson styles

The shipped Phase 03.1 registry styles are semantic (each already carries style
checks): `expository`, `worked-example`, `checked-prose`, `artifact-first`,
`case-narrative`. The four recorded rejections (Feynman, cookbook, written
Socratic, explorable explanations) stay rejected per ROADMAP; this document
does not reopen them.

The genre-inspired conventions in atlas 5.1 classify as follows:

| Genre style | Class | Route |
|---|---|---|
| Beginner plain-language guide | Cosmetic register over `expository` | voice/register tokens plus existing style checks; no new validator |
| Reference handbook | Semantic | entry-template validator; register only when a real course needs it |
| Visual explainer | Semantic | figure, caption-inference, text-alternative validator; composes with media policy (16A) |
| Field guide | Semantic | cue/look-alike/uncertainty validator; register on demand |
| Casebook | Semantic, composes from `case-narrative` | no separate canonical type unless validation differs (12.3 rule) |
| Worked textbook | Already shipped as `worked-example` | no action |
| Socratic dialogue | Rejected as a written style (stands) | Socratic remains a runtime-gated tutoring mode, refusal rendered as a locked card |
| Exam-review book | Semantic, composes study guide + practice + blueprint | register after 15B blueprint exists |
| Formula/reference sheet | Same object as the formula-sheet note mode | one validator, not two |
| Timeline or atlas | Same object as the timeline note mode | one validator, not two |

### Cosmetic themes (tokens only, no validator, learner-controlled)

From atlas 5.2/5.3: reading density (spacious/standard/compact), color theme
(light/dark/high-contrast/low-stimulation), typographic theme, voice within
house constraints, navigation view (continuous/guided/outline rail), and
explanatory register among author-approved variants. Fixed regardless of theme:
semantics, order, citations, non-color meaning, target sizes, reflow, and every
accessibility gate. A cosmetic theme that needs a schema field has crossed the
line and must re-enter as semantic.

## Prototype before the long tail (binding order)

Do not build all styles up front. Before registering any output mode beyond the
trio, prototype exactly three representative semantic styles, chosen to span
free structure, fixed scaffold, and graph structure:

1. **Notebook page** (free sections, anchors, provenance),
2. **Cornell notes** (cue/note/summary scaffold with cue-driven review),
3. **Concept map** (typed edges with textual fallback).

The prototype must prove, from **one parsed content instance** (one lesson plus
its terms and relations, parsed once by the one parser):

- all three outputs are projections of that single parse, with zero
  re-parsing and zero per-style content forks;
- each output's validator runs and can fail meaningfully on a deliberately
  broken fixture (a cue without notes, an unlabelled edge, an anchor to a
  moved block);
- each output degrades to coherent plain Markdown (the atlas linear-degradation
  and textual-fallback requirements);
- provenance and anchors survive round-trip through the 14A identity model
  (component IDs from D-14A-2 are the anchor targets).

This trio satisfies the synthesis 12.2 revisit trigger ("note-mode trio and
output-specific validators pass"). The remaining seven modes and the on-demand
genre styles register only after the trio passes, one validator and one
representative fixture each, per the backburner rule in synthesis 12.5.

**Ownership:** the semantic-vs-cosmetic rule and the composition contract land
in 16A. The trio prototype executes in 16C (notes own the note modes), against
the 16A contract, before the strategy/output registry freezes at 16C's gate.
Cosmetic tokens belong to 17A's visual system.
