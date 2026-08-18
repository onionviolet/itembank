# Ideaboard: what counts as "an entire field"

- **Created:** 2026-08-17 (this session closes discussion A1 from
  `PROMPT-plan-the-rest-2026-08-17.md`)
- **Vision origin:** Weibao, 2026-08-13, verbatim in `USER-VISION.md` ("files,
  hierarchy, onboarding, packaging, and future audit"): courses "can have
  subcourses/semester/conecpts that builds up a field or course... maybe can
  show completion, and like a progress on 'completing' the entire frield, but
  that could be implemented but what counts as an entire field and more will
  need more ideaboarding."
- **Status:** ideaboard complete; recorded model below is binding for 17B
  tracer scope and 16C/17B progress surfaces. Ledger entry IL-20260817-01.
- **Record tier:** 3 (scope and format-shaping), `AGENT-WORKFLOW.md` section 5.

## 1. What is already decided and not reopened

Three prior decisions bound this ideaboard; each is quoted so nothing is
re-derived from memory:

1. `REQUIREMENTS.md` GRAPH-01/GRAPH-02 supersession note (2026-08-13): "any
   reading of COURSE-01's 'objective hierarchy' as a universal hierarchy or
   fixed prerequisite tree is superseded by the constrained typed graph plus
   authored outline projection." A field is therefore not a new tree schema;
   it is authored structure over the one typed graph.
2. GRAPH-03: "the seven dimensions (design coverage, participation, settled
   evidence, current retention, formal completion, selected enrichment,
   uncertainty) stay separate and no single aggregate completion, mastery, or
   readiness score is produced... A bounded, versioned course may truthfully
   report complete under its named predicate; an open field has no universal
   completion percentage; formal completion persists while retention may
   decay." Retrievability is never surfaced as a percentage (bake-in
   2026-08-14).
3. GRAPH-03: "Required, required-choice, and enrichment memberships keep
   separate denominators, and adding enrichment can never lower completion."

So the open questions were never "can a field be complete as one number"
(settled: no) but: how deep does structure nest, what object a "field" is,
and how progress rolls up across nesting without collapsing into an
aggregate.

## 2. Possibility space considered

Candidate answers to "what is a field", with disposition:

- **F-a. Fixed level vocabulary** (field > course > semester > unit >
  concept, schema-enforced). Rejected for this milestone's model: real
  subjects disagree on depth (EMT has modules; Math 1400 has chapters; a
  whole-mathematics field has open depth), and the vision asks for "further
  and further more". Conflicts with the GRAPH-01/02 supersession quoted
  above (a universal hierarchy reading). Retained alternative: level LABELS
  (see recorded model). Reconsideration: a future standards-alignment
  feature that needs interoperable level names.
- **F-b. Field as an external authority's scope** (e.g. "mathematics" as
  defined by some canonical taxonomy). Backburner: importable as an authored
  scope version with provenance when a real standard arrives (NREMT
  blueprint is the near case, already covered by blueprint requirements).
  Not the definition of field; an instance of one.
- **F-c. Field as emergent cluster of the graph** (whatever is transitively
  linked counts as the field). Rejected: makes the completion denominator a
  side effect of link density, so adding one cross-link silently changes
  what "the field" means. Conflicts with GRAPH-03's honest-denominator rule
  (a denominator nobody authored is not a claim anyone owns). Retained
  alternative: graph neighborhood views stay a derived, disposable
  visualization.
- **F-d. Field as an authored, versioned scope object** over the typed
  graph. Adopted; recorded model below.

## 3. Recorded model (binding)

### 3.1 The object: scope

A **scope** is an authored, versioned membership object over the one typed
graph. One recursive object serves every level of the vision's nesting:

- A scope names: id, title, optional level label (free vocabulary: "field",
  "course", "semester", "unit", "concept group", or anything else; labels
  are display metadata, never schema), owner, version, and boundedness (see
  3.2).
- A scope's members are objectives and child scopes, each tagged required,
  required-choice (choose N of M), or enrichment, reusing GRAPH-03's three
  membership classes with their separate denominators.
- Depth is unlimited because scopes nest; there is no field-specific object.
  "An entire field" is simply the largest scope somebody authored, and its
  honesty comes from its boundedness declaration, not from its size.
- Scopes are course-package records (14B owns storage shape); they carry
  provenance (who authored the scope: learner, course builder, or imported
  authority per F-b) and are versioned like any accepted artifact. A scope
  version change never rewrites evidence; GRAPH-04 migration rules apply to
  membership changes exactly as to objective changes.

### 3.2 Boundedness and completion semantics

Every scope declares one of two boundedness values. This is one axis on one
object, not two parsers or two stores.

- **bounded:** the scope pins a membership version and names its completion
  predicate (per GRAPH-03: "complete under its named predicate", e.g. "all
  required members settled, 2 of 3 required-choice groups settled"). A
  bounded scope may truthfully report complete; formal completion persists
  while current retention decays separately.
- **open:** the scope declares that its membership is a growing frontier
  (a whole field, a lifelong subject). An open scope never reports
  complete and never shows a universal percentage. Its progress claims are
  always relative to the current scope version and say so ("as of scope
  v7, 41 of 55 required objectives settled; scope is open and may grow").

Nesting mixes freely: an open field may contain bounded courses. The
bounded child reports complete; the open parent reports its dimensions with
the child's completion as one settled fact, and remains uncompletable.

### 3.3 Progress rollup across nesting: two registered display models

Both models read the same GRAPH-03 tuples; neither introduces new stored
state or authority. They are display strategies behind one interface, so
per PLANNING-DIRECTIVES section 3 both are registered and the choice is a
setting (per-scope, with a global default), for Weibao to pick from real
screens rather than descriptions.

- **ROLLUP-DIM (dimension-wise rollup).** Each of the seven GRAPH-03
  dimensions aggregates up the scope tree separately, with the denominator
  stated at every level and membership classes kept apart. A parent scope
  shows a compact vector (e.g. coverage 12/19 objectives designed,
  participation 9/19 attempted, settled 7/19, retention band per the
  D-14A-3 fill state, formal completion 1 of 3 child courses complete,
  enrichment 4 explored, uncertainty: 2 objectives unmapped). Strength:
  one glance answers "how far into the field am I". Cost: deep trees
  weight a huge subcourse and a tiny one by raw counts; the stated
  denominator keeps it honest but not proportionate.
- **ROLLUP-MAP (one-level map view).** A parent scope never sums across
  grandchildren. It shows each direct child as its own card carrying that
  child's own tuple summary and boundedness, plus the parent's directly
  held objectives. Strength: no cross-scale distortion, matches the
  "map of the field" mental model, mirrors how Khan-style trees actually
  read. Cost: no single at-a-glance field figure, by design.

Shared contract both must satisfy (the section 3 qualification): same scope
and tuple objects, no aggregate single score anywhere, retrievability never
a percentage, denominators always visible or explicitly indeterminate,
keyboard and screen-reader access per UI-SPEC section 8, offline identical
(all inputs are local), evidence effects none (display only), skip and
resume not applicable, tests named in the 17B plan set.

### 3.4 What counts as "an entire field", answered

An entire field is an authored open scope at the top of a scope tree. The
product never decides what mathematics is; it gives the learner and course
builder the scope object to declare a field, the boundedness axis to be
honest about whether it can be finished, versioning to let the declaration
grow, and rollup displays that report progress without inventing a
percentage of an unbounded thing. Weibao's "completing the entire field"
is served two honest ways: bound a scope edition and complete it, or keep
the field open and watch the seven dimensions advance against a named,
growing scope version.

## 4. Effects on planning

- **17B tracer:** the tracer's unit gains a minimal scope tree (one open
  field scope containing one bounded course scope containing the unit) and
  must render both rollup models over real evidence; this is gate G7 in the
  17B details block written this session.
- **14B:** scope storage lands inside the course-package schema 14B already
  owns; this ideaboard adds the boundedness field and membership classes to
  its checklist, additively.
- **16C:** progress comprehension surfaces (GRAPH-03 owner phase) gain the
  two registered rollup models; 16C plans already carry the tuple work.
- **Ledger:** IL-20260817-01 records the model and the two registered
  rollups; F-a and F-c above are recorded rejections with reconsideration
  conditions; F-b is backburner.

## 5. What this does not decide

Storage bytes (14B), the exact card and vector layouts (17A/17B UI work),
level-label suggestions in the UI, and whether an imported standard (F-b)
ever ships. No em dash characters are used in this file.
