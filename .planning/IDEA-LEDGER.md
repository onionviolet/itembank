# Idea ledger

Append-only intake and disposition ledger for substantial ideas that arrive
outside a phase. Dispositions follow `AGENT-WORKFLOW.md` section 5 (core,
registered, prototype, backburner, deferred, superseded, rejected). Rejected
and superseded entries are never deleted; each records evidence, exact reason,
conflicting rule, retained alternative, date, and reconsideration condition.
Hard rejections should also be mirrored into the permanent ledger in the Phase
16 synthesis section 12.4 when that document is next amended.

Entry IDs are `IL-YYYYMMDD-NN`. New entries go at the bottom of their section.
Amendments to an existing entry are additive notes under the entry, dated.

## Open and registered

### IL-20260815-01: Evidence records the full model-visible payload

- **Proposal:** Adopt the deepseek-harness runtime invariant "model-visible
  means logged": anything included in a request to a hosted or local model must
  be reconstructable from the on-disk evidence store. For any tutoring
  exchange, the question "exactly what did the model see about this item and
  this learner" is answerable from disk.
- **Origin:** deepseek-ai/deepseek-harness `docs/architecture.md` (fetched
  2026-08-15); raised by Weibao in chat 2026-08-15.
- **Evidence considered:** itembank already gates what a model may reveal
  (session mode, hint tier) but does not guarantee the outbound payload is
  reconstructable. The accepted risk "hosted models see item text" (2026-08-05)
  is currently unauditable after the fact.
- **Fit:** Uses the existing single evidence store; no second store. Aligns
  with "evidence and banks stay on disk" and with the operation journal
  pattern.
- **Cost driver:** evidence volume per tutoring exchange; a redaction or
  reference scheme (store item id plus disclosure tier rather than full text)
  may be enough and is part of the design question.
- **Disposition:** Registered.
- **Revisit trigger:** first phase that implements or revises the tutoring
  request path.

### IL-20260815-02: Named capability seams where variability is real

- **Proposal:** Adopt the deepseek-harness seam discipline (service
  definition, provider, consumer) explicitly, but only at layers where
  variation is a product goal: the model backend (hosted vs local), teaching
  surfaces, and source-discovery roots for the source-to-course milestone.
  One provider swap changes the whole product at that seam.
- **Origin:** deepseek-ai/deepseek-harness architecture docs (2026-08-15).
- **Evidence considered:** the model backend is already built this way
  ("hosted and local are the same code path", a config change; the 7900 XTX
  local path is a provider swap). This registers the pattern by name so future
  seams are designed rather than accreted.
- **Boundary:** seams are for layers whose variation is wanted. The scorer,
  parser, and evidence store are explicitly not seams; see IL-20260815-04.
- **Disposition:** Registered.
- **Revisit trigger:** any phase adding a second implementation of an existing
  capability.
- **Note 2026-08-15:** embedded into planning at Weibao's direction as a
  standing rule in `PLAN-TEMPLATE.md` ("Name the seam before adding a
  provider"). The discipline is planned in from now on; plugin machinery
  (registry, loader, mounts) stays out until a second provider exists. The
  six ready 15A plans and 15B were not retrofitted; the rule applies from the
  next planning session onward.

### IL-20260815-03: Event taxonomy vocabulary

- **Proposal:** Borrow the three-way event vocabulary from deepseek-harness:
  durable facts (appended, never rewritten), live state (ephemeral,
  reconstructable), and policy attachment (rules applied without entangling
  the core loop). Use it as naming discipline in design docs.
- **Origin:** deepseek-ai/deepseek-harness architecture docs (2026-08-15).
- **Evidence considered:** matches the existing "separate state axes" rule
  (synthesis 2.3, 4.1). Adds vocabulary, not machinery.
- **Disposition:** Backburner (naming aid, no build cost until a doc uses it).
- **Revisit trigger:** next architecture or spec document that describes
  evidence events alongside UI state.

### IL-20260815-05: Audit the one-scorer rule wording

- **Proposal:** Reword the runtime invariant so it cannot be misread as a
  feature blocker. Raised by Weibao 2026-08-15: "if a feature requires a
  second scorer, parser, or evidence store, the feature is wrong" should not
  impede quality features.
- **Analysis:** the rule bans a second scoring *authority*, not new scoring
  *capability*. Quality features (partial credit, semantic matching for short
  answers, AI-proposed marks, new item types) belong inside the one scorer as
  additive extensions, or enter as advisory inputs the runtime or the human
  marker accepts. The rule blocks duplication and authority transfer, not
  improvement.
- **Concrete audit items:**
  1. Clarify wording along the lines of: "exactly one scoring authority;
     scoring capabilities are added inside it additively; advisory graders may
     propose a mark but never settle one."
  2. When scorer behavior changes (new partial-credit model, changed
     canonicalization), stamp a scorer version into evidence records so old
     and new attempts stay comparable. Today nothing versions the scorer.
  3. Confirm the short-answer path already models this correctly: the scorer
     returns None (pending), a human sets MARK. An AI-proposed mark is the
     same pattern with a machine proposer.
- **Disposition:** Registered (rule audit, documentation change plus the
  evidence versioning question).
- **Revisit trigger:** next CLAUDE.md or AGENTS.md maintenance pass, or the
  first phase that extends `score_response`.

### IL-20260815-06: Rule audit, rules that could block quality features when misread

- **Proposal:** Sweep the binding rules in CLAUDE.md, AGENTS.md, and the
  synthesis summary for wording that, read literally, blocks a quality feature
  the rule was never meant to block. Companion to IL-20260815-05, requested by
  Weibao 2026-08-15 after the one-scorer reword.
- **Status of IL-20260815-05:** applied 2026-08-15. CLAUDE.md "Runtime
  invariant" paragraph and AGENTS.md non-negotiable rule 1 now state one
  scoring authority, additive capability growth inside `score_response`, and
  advisory graders that propose but never settle. The scorer-version-in-
  evidence question (audit item 2 of IL-20260815-05) remains open.
- **Findings, ranked by risk of blocking a wanted feature:**
  1. *"Never auto-grade prose"* (AGENTS rule 3). Misreading: no AI feedback on
     short answers at all, which kills instant formative feedback. Intended
     reading: the settled mark stays pending; a labeled, provisional AI
     assessment is an advisory grade and is allowed. Fix: one clarifying
     sentence in rule 3 mirroring the rule 1 clarification.
  2. *"Every interactive feature needs a useful static representation"*
     (AGENTS rule 11). Misreading: bans inherently interactive treatments
     (simulations, manipulatives) whose static form is necessarily weaker.
     Fix: define the static bar as "conveys the core meaning and remains
     study-usable", not "equivalent experience".
  3. *"An agent never self-certifies accessibility"* (synthesis 11.4).
     Misreading: every authored artifact waits on human accessibility review,
     a throughput bottleneck when a course generates hundreds of artifacts.
     "Representative" is the intended escape hatch but is undefined. Fix:
     define representative sampling per template or capability profile, with
     full review when a template changes.
  4. *"Every capability has both a route in the daemon and a command in the
     CLI"* (CLAUDE.md Surfaces). Misreading: doubles the cost of every
     feature, and presentation-only behaviors (hover definitions, focus
     disclosure) have no meaningful CLI form. Fix: scope the rule to runtime
     capabilities; presentation behaviors need an accessible equivalent, not
     a CLI command.
  5. *"Format changes must be additive"* plus the LESSON-absence
     compatibility guarantee. Misreading: a format mistake can never be
     corrected and the format accretes cruft forever. Fix: allow additive
     change plus a documented deprecation and a `migrate` operation, which
     the mutation vocabulary already names.
- **Later, lower risk:** "evidence and banks stay on disk, no cloud sync"
  should distinguish telemetry (banned) from learner-initiated export, backup,
  or device sync (a rights grant; Phase 18 friend installs will strain this).
  The preserve-breadth ledger rules impose process weight with no pruning
  path; cost is agent time, not product harm.
- **Disposition:** Registered (documentation clarifications; findings 1
  through 5 are each a bounded wording edit, none changes runtime behavior).
- **Revisit trigger:** next maintenance pass on CLAUDE.md or AGENTS.md, or the
  first phase a finding actually blocks.
- **Note 2026-08-15:** all five findings applied at Weibao's direction.
  Finding 1 in AGENTS.md rule 3; finding 2 in AGENTS.md rule 11; finding 3 in
  the authored-output accessibility bullet of both AGENTS.md and CLAUDE.md;
  finding 4 in the CLAUDE.md Surfaces constraint; finding 5 in the CLAUDE.md
  Compatibility constraint. The synthesis document itself
  (`.planning/research/phase-16/14-synthesis.md` 11.4) was not edited; the
  binding mirrors carry the clarification. The "later" items (telemetry vs
  learner-owned sync, ledger pruning) remain unapplied.
- **Note 2026-08-15 (later same day):** the two "later" items are now also
  applied at Weibao's direction: data-residency clarification in AGENTS.md
  rule 5 and the CLAUDE.md Data residency constraint; append-only-ledger
  maintenance clarification in AGENTS.md rule 14 and the CLAUDE.md
  preserve-breadth bullet. A full audit pass covering every binding rule,
  every past pitched feature, and a replanning gate is planned in
  `.planning/RULE-AUDIT-PLAN-2026-08-15.md`.

### IL-20260815-07: Re-open PDF and DOCX source intake (constraint audit F4)

- **Proposal:** Re-decide PDF and DOCX parsing on merit. Originally rejected
  under stdlib-only, which was relaxed to a preference on 2026-08-09; the
  constraint audit (`research/2026-08-10-constraint-audit.md` F4) judged the
  citation cargo-culted and marked it revisit.
- **Why now:** it directly gates the source-to-course milestone. Books,
  syllabi, and exam blueprints arrive as PDF and DOCX; today they fail
  explicitly (BLOCKER-AUDIT class 4, "Markdown/plain UTF-8 only").
- **What a merit decision needs:** candidate libraries with real cost
  (install size, maintenance, extraction fidelity on the learner's actual
  sources), locator fidelity for citations (the original Phase 11 concern),
  and the supply-chain policy from IL-20260815-09 in place first.
- **Disposition:** Registered (needs one bounded research pass; do not adopt
  a dependency before IL-20260815-09 resolves).
- **Revisit trigger:** first source-discovery or absorb-book phase that meets
  a real PDF or DOCX source.

### IL-20260815-08: Re-open pytest and test-runner adoption (F17)

- **Proposal:** Re-decide the test-runner question on merit. Rejected under
  stdlib-only; the constraint audit judged the citation cargo-culted and
  noted the rejection "is costing verification coverage" (fixtures,
  parametrization, coverage reporting the bespoke scripts do not give).
- **Evidence considered:** the `tests/*_roundtrip.py` scripts work and stay;
  the question is whether a runner on top earns its cost, not a rewrite.
- **Disposition:** Registered.
- **Revisit trigger:** next phase that adds a test file, or the first flaky
  or missed-regression incident the bespoke scripts fail to catch.

### IL-20260815-09: Real supply-chain policy to replace dependency-count (F5)

- **Proposal:** Write an actual supply-chain policy: pinning, hash
  verification, vendoring rules, update cadence, and review requirements per
  dependency. The constraint audit found the zero-dependency preference
  "standing in as a security control" (erosion-by-omission); with the
  preference relaxed, no control stands in its place.
- **Ordering constraint:** this precedes any new runtime dependency,
  including IL-20260815-07's candidates.
- **Disposition:** Registered, blocking for dependency adoption.
- **Revisit trigger:** the first plan that proposes a non-vendored
  dependency.

### IL-20260815-10: Re-open non-stdlib Anki import (F3)

- **Proposal:** Re-decide Anki `.apkg`/collection import on merit. Rejected
  under stdlib-only ("stdlib ZIP+SQLite reads alone"); the audit judged the
  citation cargo-culted and suspects the stdlib path may be unmeetable.
- **Disposition:** Registered.
- **Revisit trigger:** first phase that needs to read Anki data deeper than
  AnkiConnect provides.

### IL-20260815-11: Reconcile the packaging conflict (F15, F9)

- **Proposal:** Resolve the open conflict between "no build step" history,
  the miscited DEL-02 ground against PyInstaller (F9), and the compiled or
  frozen packaging question (F15), before Phase 18 external installs. The
  V2-DEL-01 signing trigger has already fired (second-user amendment,
  2026-08-14).
- **Disposition:** Deferred to Phase 18 planning; recorded here so the
  conflict is not rediscovered.
- **Revisit trigger:** Phase 18 planning session.
- **Related, lower priority:** F7 (third-party markdown or table renderer,
  "not evaluated further" at the time) and F10 (pywebview, now a
  reversal-cost question) stay revisit-marked in the constraint audit and the
  2026-08-15 tally; no entry until a phase needs them.

### IL-20260815-12: Three-tier process record shape

- **Proposal:** Scale planning record shape to consequence: tier 1 for
  reversible low-stakes work (intent, owner, next action, undo), tier 2 for
  consequential proposals and durable writes (existing disposition and
  operation controls), tier 3 for binding formats, authority, rights, hard
  rejections, and scope (full evidence, prototype, ledger, and user-decision
  gates). Companion rule: a rejection must quote the currently binding rule
  text it relies on.
- **Origin:** `RULE-AUDIT-2026-08-15.md` friction verdict and
  `RULE-AUDIT-ROADMAP-DELTA-2026-08-15.md` proposal 1; approved by Weibao
  2026-08-15.
- **Evidence considered:** the audit's finding that uniform sixteen-field
  records duplicate recording on low-stakes work, and that stale-authority
  drift (about twenty vetoes by a retired preference) was the measured rule
  failure the quoting requirement addresses.
- **Disposition:** Core (binding in `AGENT-WORKFLOW.md` section 5, pointed to
  from `PLANNING-DIRECTIVES.md` section 3a). Verification run recorded in the
  delta file; failure condition did not fire.
- **Reconsideration condition:** the delta's failure condition, two readers
  classifying the same operation into different tiers in practice, or the low
  tier permitting an irreversible or externally visible change.

### IL-20260816-01: Plugins as the feature-delivery mechanism at named seams

- **Proposal:** Use a plugin mechanism as the way features are added and
  iterated, scoped to the seams where variation is a product goal. This is
  the surviving half of the plugin-first idea: plugin as delivery vehicle for
  registered capabilities (lesson styles, treatments, teaching surfaces,
  exporters, model backends, discovery providers, schedulers), never plugin
  as authority transfer. Raised by Weibao 2026-08-16 as a reconsideration of
  IL-20260815-04: "consider the plugin-first core as a way to add or work on
  features instead" (verbatim in `USER-VISION-INBOX.md`, 2026-08-16 entry).
- **Origin:** deepseek-ai/deepseek-harness plugin architecture, rescoped;
  builds directly on IL-20260815-02 (named seams) rather than reopening
  IL-20260815-04.
- **Evidence considered:** IL-20260815-02 already registers the seam
  discipline and its note keeps plugin machinery (registry, loader, mounts)
  out "until a second provider exists". The conflict rule in
  `PLANNING-DIRECTIVES.md` section 3 ("build both, let the learner pick")
  already assumes registration-not-fork; a plugin mechanism is the concrete
  machinery that makes a registration cheap. What changes here is intent:
  when a second provider does arrive at any seam, the answer is a small
  registry at that seam, designed once and reused, not per-seam ad hoc
  wiring.
- **Boundary (unchanged from IL-20260815-04's rejection):** the scorer,
  parser, and evidence store are not plugins and never load from
  configuration. New scoring capability grows additively inside the one
  scorer (IL-20260815-05 wording). Presentation of a new item type may be
  pluggable; its scoring is not.
- **Cost driver:** registry and loader machinery, a manifest format, and a
  compatibility story per seam; also the supply-chain policy
  (IL-20260815-09) if third-party plugins are ever loaded, which is not
  proposed here.
- **Disposition:** Registered.
- **Revisit trigger:** the first phase where a second provider lands behind
  any named seam; that phase designs the shared registry shape instead of a
  one-off.

### IL-20260816-02: One runtime, two shells (web and installed app)

- **Proposal:** Deliver the product through two shells: a web-based surface
  reached in a browser and an installed app. Raised by Weibao 2026-08-16:
  "Also, a digital web based runtime and also a app based runtime too,
  readjust accordingly?" (verbatim in `USER-VISION-INBOX.md`).
- **Naming correction, applied before planning:** these are shells, not
  runtimes. The runtime invariant (one runtime, one scorer, one evidence
  store) does not bend; the web surface and the app surface are both clients
  of the same runtime, exactly as the CLI, the loopback graded sitting, the
  offline HTML quiz, and the JSON agent sessions are today. Any plan that
  writes "web runtime" as a second scoring authority is wrong on its face.
- **Evidence considered:** the packaged desktop app is already the recorded
  end goal (2026-08-09 amendment). The web shell has shipped ground: the
  daemon and loopback server already serve browser surfaces, so the local
  web path is an extension of existing architecture, not new architecture.
  Phase 18 (external installs) and IL-20260815-11 (packaging conflict:
  build-step history, PyInstaller citation, signing trigger) already own the
  app-shell packaging question.
- **Boundary:** a hosted multi-tenant web service is out of scope under the
  no-accounts rule and the data-residency rule (evidence and banks stay on
  disk). The web shell means the learner's own runtime reached through a
  browser: loopback today, self-hosted LAN or tunnel as a rights-gated
  future question. If a genuinely hosted variant is ever wanted, it is a new
  ledger entry against those rules, not an interpretation of this one.
- **Cost driver:** the app shell carries the IL-20260815-11 packaging work.
  The web shell's cost is mostly UI completeness (the 16B/16C/17A contracts)
  plus whatever remote-access hardening a non-loopback bind would need;
  today's server binds loopback only.
- **Disposition:** Registered.
- **Revisit trigger:** Phase 18 planning (app shell), and the first 16B/17A
  session that must choose whether the comprehensive learning UI targets the
  browser shell, the packaged shell, or one codebase for both.

## Rejected

### IL-20260815-04: Plugin-first core (no privileged core; swappable scorer)

- **Proposal:** Adopt the central deepseek-harness thesis: everything is a
  plugin, there is no privileged core, and every capability including the
  scorer, session log, and agent loop is replaceable from configuration.
- **Origin:** deepseek-ai/deepseek-harness README and architecture docs
  (2026-08-15); considered at Weibao's request.
- **Evidence considered:** harness targets a multi-tenant developer ecosystem
  where third parties ship competing providers; replaceability is its product.
  itembank is one learner, one installation, where every surface (CLI, graded
  browser sitting, offline HTML quiz, JSON agent sessions) must reach the same
  verdict on the same response, and longitudinal evidence must stay comparable
  across months.
- **Exact reason:** a swappable scorer makes correctness a configuration
  value. Consequences: (1) surfaces can bind different providers and disagree
  silently, with no error raised; (2) evidence loses comparability, because a
  score's meaning depends on which provider produced it; (3) the disclosure
  gate weakens, since agents author artifacts and configuration in this
  system, and a model that cannot argue the runtime into revealing could
  instead supply or select a scorer that reveals or grades leniently. The
  invariant is an authority boundary, not a code-organization preference.
- **Conflicting rule:** Runtime invariant ("one runtime, one scorer, one
  evidence store; the runtime, not the model, settles scoring, disclosure,
  and evidence") and synthesis 2.1 (deterministic runtime is sole authority
  for assessment state).
- **Retained alternatives:** IL-20260815-01 (log invariant), IL-20260815-02
  (seams at genuinely variable layers), IL-20260815-05 (rule wording audit so
  the invariant never blocks capability growth inside the one scorer).
- **Date:** 2026-08-15.
- **Reconsideration condition:** itembank becomes a multi-implementation
  platform with third-party runtimes, or the rule audit in IL-20260815-05
  concludes the authority boundary can be held by some mechanism other than a
  single scorer implementation.
- **Note 2026-08-16:** Weibao asked to reconsider this as "a way to add or
  work on features instead". The rejection stands unchanged for the scorer,
  parser, and evidence store; the feature-mechanism half is registered
  separately as IL-20260816-01 (plugins as delivery machinery at the named
  seams of IL-20260815-02). This note is additive; nothing above is
  reopened.
