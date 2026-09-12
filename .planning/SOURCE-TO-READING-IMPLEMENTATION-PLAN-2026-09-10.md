# Source-to-reading implementation plan

Date: 2026-09-10
Status: active, prototype link authorized. Durable schema and evidence changes
remain review-gated.

## Outcome

One accepted local source range can appear as separate course activities, open
at its exact locator, return to the activity that launched it, and record an
explicit learner declaration without implying a score or mastery. The final
candidate must preserve source identity, rights, offline behavior, recovery,
plain-file usefulness, and the one evidence writer.

## Route and boundaries

Use one balanced implementation owner at medium reasoning because the source,
course, UI, and recovery seams share context. Add an independent reviewer only
for the durable contract delta or if a targeted gate exposes an authority
conflict. Do not split implementation across overlapping writers.

Authorized reads are this repository and disposable synthetic roots. Writes
for Link P1 are limited to this plan, `prototypes/course-preparation/`, its
focused test, and generated evidence outside the repository. Do not change
production routes, schemas, runtime, evidence, real course data, external
services, or the existing dirty vision-audit files. Do not commit or push.

## Work links

### P1: reversible occurrence prototype

Build a synthetic local course through the real course, journal, rights, source,
objective, and binding operations. Project two in-memory occurrences over one
accepted source and one direct-reading binding. Render Now and Resources views,
exact-range source opening, return context, distinct unavailable states, and a
visibly simulated Mark read action. The plain Markdown source remains the
fallback.

Correction accepted 2026-09-10: the first implementation reduced this to
generic cards and did not meet the product-experience gate. P1 must use the
accepted greenfield learner identity, not a neutral test harness. The review
surface includes the personal desk and persistent navigation, course and
objective context, editorial source reading, learner note space, activity
transitions, Resources, evidence limits, local-only status, recovery states,
and a focused narrow layout. Patterns from reviewed public projects are
absorbed only where they reinforce those jobs. The prototype remains one
coherent Itembank design rather than a gallery of borrowed interfaces.

Gate P1:

- The two occurrence IDs resolve the same source ID and identical bytes.
- Marking one occurrence does not complete the other or write to disk.
- Library is absent from Now. Rights denial, missing locator, divergent source
  revision, and remote-only offline content have distinct recovery copy.
- Back targets the launching occurrence. Keyboard structure and narrow reflow
  have deterministic checks. Human touch, screen-reader, zoom, and aesthetic
  acceptance remain owed unless actually performed.
- Before and after fingerprints for source, course graph, and evidence inventory
  are identical. No scorer, evidence writer, import, schema, or production route
  is invoked.
- Desktop and narrow layouts retain the adopted typography, navigation,
  source-object treatment, course path, action hierarchy, status language, and
  recovery affordances. The result must feel like a complete learning workspace,
  not a schema demonstration. Human visual acceptance remains required.

### P2: durable contract review

Present the smallest additive delta to `SOURCE-TO-COURSE.md`: occurrence
identity and revision, course and objective references, revision-scoped binding
reference, preparation mode, path role, activation, sequence evidence, source
locator, assignment provenance, assistance policy, and explicit unavailable
state. Decide LA-Q1, the learner label, and LA-Q2, permanent binding identity.

After Weibao accepts those choices, specify an additive course-graph section
and occurrence-scoped descriptive evidence event. Legacy graphs remain valid
and gain no inferred phase, role, activation, assistance, deadline, or
completion. Writes use expected fingerprints, atomic journal commits, and one
evidence writer. A self-report never becomes a response score or mastery fact.

Gate P2: parser and schema compatibility fixtures pass, repeated completion is
idempotent per occurrence revision, shared content does not share completion,
rights and revision changes produce explicit states, and export or restore
reports every occurrence and evidence loss. Independent review finds no second
parser, scorer, source identity, evidence store, or progress authority.

### P3: exact import recovery

Repair R1 through R3 before connecting reading activities to imports. Model
prior absence in journal undo. Make director reversal account for every durable
mutation. Treat derived Markdown and locator sidecars as one recoverable import
composition while preserving conflict refusal and raw source bytes.

Gate P3: creation, edit, divergent bytes, repeated undo, injected interruption,
sidecar pairing, registry reconstruction, and clean-machine offline restore all
pass. A partial reversal cannot return `complete: true`. Undo of creation
restores absence rather than a zero-byte file.

## Sequence and stop rules

Execute P1 first. Stop for review after its gate because P2 changes durable
formats and evidence. Execute P3 independently after the journal owner accepts
the recovery design. Stop immediately if an occurrence requires duplicate
content, completion crosses occurrence IDs, unavailable content appears done,
or the prototype must mutate accepted truth.

## Final acceptance

Run each link's focused tests, then quick preflight on the integrated candidate.
Run full preflight once after durable implementation. Review the actual diff.
Record human-only checks as owed. Reconcile the source-to-reading audit and
recovery findings before closing the chain.
