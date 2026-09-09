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
- **Note 2026-08-17:** the bounded research pass ran; findings in
  `research/2026-08-17-pdf-docx-intake.md`, judged against the locator gold
  cases in `fixtures/audit/locator_fidelity_cases.py`. Verdict: primary PDF
  path is pdfplumber pinned with pdfminer.six as its engine (both MIT, pure
  Python, page numbers plus word and table-cell geometry); primary DOCX path
  is python-docx (MIT) with stdlib zipfile plus xml.etree reads for
  footnotes, headers, comments, and tracked changes; pypdf (BSD-3, zero
  deps) is the recorded fallback for page-level extraction. PyMuPDF is
  parked, not rejected: technically strongest but AGPL, which
  `SUPPLY-CHAIN-POLICY.md` section 2.4 routes to an explicit Weibao
  decision. docling (torch-scale dependency weight) and markitdown and
  mammoth (no locator output) are cut for import. OCR is deferred to the
  existing local-Ollama ocr skill; scanned PDFs return the unsupported
  result the gold manifest requires. The importer emits Markdown plus a
  JSON locator sidecar, both plain UTF-8, so the one-parser rule is
  untouched and the removal path leaves imported data readable.
  IL-20260815-09 resolved the same day, so the ordering constraint is
  satisfied. Disposition stays Registered with adoption ready: the first
  plan that meets a real PDF or DOCX source adopts through the
  `SUPPLY-CHAIN-POLICY.md` section 3 gate, citing the research file, and
  owns the sidecar schema design it deliberately left open.

- **Note 2026-08-21:** promoted to a phase. Phase 14C (Source Adapter Registry &
  Remote Intake) owns the adoption and the sidecar schema this entry left open,
  generalized from PDF and DOCX to one adapter contract covering PPTX, EPUB, web
  capture, transcripts, audio and video, and OCR. Context:
  `.planning/phases/14C-source-adapter-registry/14C-CONTEXT.md`. Disposition moves
  from Registered to Scheduled.

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
- **Note 2026-08-17: settled.** The policy is written:
  `.planning/SUPPLY-CHAIN-POLICY.md` (scope, vendoring and pinning rules,
  SHA-256 recorded and CI-verified via a `VENDORED.md` table, license
  review with copyleft routed to Weibao, per-plan adoption gate, update
  cadence, threat-table language, plugin interaction). Disposition moves to
  Core: binding on every plan that introduces, updates, or removes a
  third-party artifact. The blocking condition on IL-20260815-07 and
  IL-20260816-01 is discharged. Failure condition: a dependency lands
  without its `VENDORED.md` row or with an unreviewed license; owner: any
  planning session that reviews a dependency-introducing plan; verification:
  the CI checksum step the first vendoring plan adds.

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
- **Note 2026-08-17: settled as a standing pattern.** The open question was
  bounded to seams that never touch the scorer, parser, or evidence store
  (IL-20260815-04 stays rejected and is not reopened). Decision: plugins as
  the delivery mechanism at named seams is adopted as the standing pattern,
  disposition Core at the planning-rule level, with machinery still deferred
  exactly as IL-20260815-02's note states: no registry, loader, manifest, or
  mount code exists until a second provider actually lands at a seam. When
  that first second provider arrives, its phase designs one shared registry
  shape (name, version, capability declaration, accessible-degradation
  statement, tests) that every later seam reuses; per-seam ad hoc wiring is
  refused from that point. Third-party plugin loading is not proposed and
  would be a new ledger entry under `SUPPLY-CHAIN-POLICY.md` sections 1 and
  6; no plugin loader may fetch code at runtime. Eligible seams today, from
  IL-20260815-02 and the registered-strategy work: model backend, lesson
  output modes and styles, treatment policies, teaching surfaces, exporters,
  source-discovery providers, schedulers. Nearest expected trigger: the
  local model backend landing beside the hosted one, or a second lesson
  output mode registering in 16C. Owner: the planning session of that
  triggering phase; verification: the registry-shape design appears in that
  phase's plan set; failure condition: a second provider lands as an
  `if`-chain branch (Extensibility Rule 2 already fails that in review).

- **Note 2026-09-06: bounded implementation route.** The user revisited DSH
  and requested plans for a less capable executor if they improve the product.
  The second-provider trigger is already present: source adapters have ten
  registrations and model transports already prove a synthetic third provider.
  `EXTENSION-DELIVERY-2026-09-06.md` owns the conditional benefit assessment and
  follow-on seeds. `EXT-01-PLAN.md` owns a reversible source-declaration pilot.
  The standing pattern remains Core. The pilot is Prototype until its gates
  prove compatibility and useful metadata validation. The owner is the
  extension maintainer. Evidence is code inspection and a recommendation,
  not measured efficiency gains. Cost is one helper, metadata maintenance,
  and regression checks. This adds no Reach capability or published schema.
- **Future breadth 2026-09-06:** external installable packages are Deferred,
  owned by supply-chain and runtime-maintenance maintainers. Unblock with a
  concrete package need and accepted isolation, pinned acquisition,
  compatibility, grants, atomic activation, rollback, and offline recovery.
  Cost includes package review, isolation, dependency support, and updates.
  Evidence class is a design possibility, not a shipped capability. Live
  reload is Backburner, owned by the extension maintainer. Revisit only when
  restart-based activation measurably obstructs a real workflow and session
  pinning is proven. Cost is lifetime management and recovery under concurrent
  operations. Neither idea is rejected or promised by the current packet.

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

### IL-20260817-01: Field, scope object, boundedness, and progress rollup

- **Proposal:** Answer Weibao's 2026-08-13 open question "what counts as an
  entire field" with a recorded model: one recursive, authored, versioned
  **scope** object over the one typed graph (members are objectives and
  child scopes, tagged required, required-choice, or enrichment); free-text
  level labels instead of a fixed level schema; a **boundedness** axis
  (bounded scopes pin a membership version and may truthfully report
  complete under their named predicate; open scopes never report complete
  and state their scope version on every claim); and two registered rollup
  display models over unchanged GRAPH-03 tuples, ROLLUP-DIM (dimension-wise
  aggregation up the tree with stated denominators) and ROLLUP-MAP
  (one-level map view, no aggregation past direct children).
- **Origin:** `USER-VISION.md` 2026-08-13 "files, hierarchy, onboarding,
  packaging, and future audit" entry; ideaboard
  `.planning/IDEABOARD-FIELD-2026-08-17.md` (this session, closing
  discussion A1 of `PROMPT-plan-the-rest-2026-08-17.md`).
- **Evidence considered:** GRAPH-01 (structural containment nodes with local
  labels, no universal hierarchy), GRAPH-02 (typed edges), GRAPH-03 (seven
  separate dimensions, bounded-course completion predicate, open-field
  no-percentage rule), GRAPH-04 (membership migration), D-14A-3 fill state.
- **Disposition:** Core for the scope object and boundedness axis (14B owns
  storage shape, additively); Registered for both rollup models, choice is
  a per-scope setting with a global default, Weibao picks from the rendered
  17B tracer screens. Rejected within the ideaboard, with full records
  there: F-a fixed level vocabulary (conflicts with the GRAPH-01/02
  supersession text quoted in the ideaboard) and F-c emergent-cluster
  fields (conflicts with GRAPH-03's honest-denominator rule). Backburner:
  F-b imported authority scopes (revisit when a real standard framework is
  imported).
- **Revisit trigger:** the 17B tracer rendering both rollups (the
  scope-and-rollup check under gate G5 in the 17B details block), or 14B's
  course-package schema work meeting the scope object.
- **Amendment 2026-08-17 (same session):** the first write of this entry
  cited "gate G7" for the rollup check; G7 is the synthesis 16.1
  course-quality gate, and the rollup check belongs under G5 (evidence
  honesty). Corrected here and in the ideaboard and USER-VISION note.

### IL-20260817-02: Backlog 999.2 bilingual reader, post-reframe review

- **Proposal:** Re-argue backlog phase 999.2 (bilingual reader) against the
  source-to-course scope, as its last review (2026-08-10) predates the
  reframe.
- **Evidence considered:** the 2026-08-10 verdict (a correctly parked entry
  with a sharp trigger: un-authored prose tappable with tracked word
  status needs tokenization, lemmatization, and a per-word state store,
  which is a second product); the reframe's direct-source-reading
  treatment (SOURCE-TO-COURSE step 4), which puts un-authored running
  prose in front of the learner as a first-class treatment.
- **Disposition:** Keep (backburner, unchanged), with one addition: the
  reframe makes the trigger more reachable, because direct source reading
  gives the prose surface such a reader would sit on. The trigger itself
  stands unchanged; nothing is built until per-word tracked status is
  actually wanted over that surface. The `zh=` TERMS meta field remains
  the shipped cheap alternative.
- **Revisit trigger (sharpened):** a recorded learner request for per-word
  lookup or tracked word status over a source-reading treatment, or any
  language-learning course entering the course shelf.

### IL-20260817-03: Backlog 999.3 MCP surface, promotion per its own trigger

- **Proposal:** Re-argue backlog phase 999.3 (MCP surface) against current
  scope.
- **Evidence considered:** the entry's own recorded promotion trigger
  ("promote when Phase 8 is verified and either an AI tutor is being used
  against itembank often enough that shelling out to the CLI is the
  friction, or V1 reaches /gsd-complete-milestone. Whichever comes
  first."): Phase 8 is verified (6/6 complete) and the v1.0 milestone
  completed 2026-08-11, so the disjunct fired. The source-to-course
  reframe strengthens the case: agents are first-class clients of the
  runtime, and Phase 18's agent-facing capability disclosure manifest is
  the natural payload of an MCP `server/discover` surface. Extensibility
  Rule 9 has been reserving MCP tool names on every new API route since
  2026-08-10, so the promotion cost has been prepaid.
- **Disposition:** Promote. 999.3 leaves the backlog and enters the active
  runway sequenced after 17B, beside Phase 18: it may run parallel to 18,
  and 18's capability disclosure manifest work should name the MCP surface
  as a consumer. It does not interrupt the 14A through 17B milestone
  spine; nothing in that spine depends on it. Scope, criteria, and named
  unknowns are unchanged from the 999.3 entry.
- **Revisit trigger:** Phase 18 planning already accounts for it (this
  session's 18-CONTEXT names the interaction); the promotion is recorded
  in the ROADMAP sequencing note of the same date.
### IL-20260820-01: Re-open image and paper-note intake (B9), scoped as an enhancement path

- **Proposal:** Treat the learner's existing paper notes, photographed or
  scanned, as a first-class source class that feeds the course. Intake produces
  an image asset plus a derived transcription, and the value is what follows:
  expanding a thin note, adding depth from a bound source, correcting an error
  in the learner's own wording, and checking whether the learner understands
  what they wrote. Digitization alone is not the feature.
- **Origin:** Weibao, 2026-08-20, recorded verbatim in `USER-VISION-INBOX.md`
  under "paper-note OCR, AI annotation, and note aesthetics".
- **Prior disposition being reopened:** B9 (image ingestion and OCR) was
  deferred to backlog in
  `RESEARCH-BRIEF-learning-platform-2026-08-09.md` line 336, with the reason
  recorded in `ROADMAP.md` line 2458: the photograph to model to draft loop
  would later ride Phase 3.2's generation path. That reason was sequencing, not
  a rejection, and the generation path it waited on now exists.
- **Evidence considered:** the local vision-model path is already available
  through the existing `ocr` skill, so intake is a seam consumer rather than
  new architecture. Stream 12 (`research/phase-16/12-active-annotation-notes.md`)
  already supplies note identity, ownership, privacy, provenance, and the rule
  that a learner note is never keyed truth. `media-intake` exists as a skill
  stub and already owns rights, credit, accessible alternatives, and derivation
  records for images. IL-20260815-07 (PDF and DOCX intake) reopened an adjacent
  intake question on similar grounds.
- **Fit:** no second parser, scorer, or evidence store. A scan is a source; a
  transcription is a derived artifact; anything the model adds is labeled
  synthesis under the existing citation rule.
- **Boundary:** the scan image is the record and the transcription is derived
  and re-runnable, so a better model later can re-transcribe without touching
  what was photographed. Transcribe, clean, and expand are three different
  truth claims and must stay visibly distinct in the artifact, because
  collapsing them is how a model's guess becomes the learner's note and then a
  question and then a key. Transcription confidence is surfaced per line.
  Rights differ between the learner's own handwriting and a photographed
  copyrighted page; unknown rights stay restrictive. The CSCI 1100 AI-use ban
  applies to OCR-plus-expansion on that course's notes.
- **Degraded behavior:** handwriting is currently the clearest case where a
  hosted model outperforms a local one, so intake must degrade rather than
  block. Offline, the image attaches and remains readable and bindable, and
  transcription is deferred.
- **Cost driver:** transcription accuracy on cursive and on subject notation,
  the correction interface, and reconciliation when the same page is scanned
  twice.
- **Disposition:** Registered.
- **Revisit trigger:** the first phase that plans learner-note artifacts or
  media intake, whichever lands first; or a decision to make note intake a
  named phase of its own.

### IL-20260820-02: Re-open handwriting and stylus input (B10), narrowed to recognition of existing paper

- **Proposal:** Reopen the recorded descope of handwriting and stylus, narrowed.
  What is reopened is recognition of handwriting that already exists on paper,
  including subject notation such as handwritten mathematics, because
  IL-20260820-01 depends on it. What is not reopened is live stylus authoring
  inside itembank: ink capture, an ink canvas, pressure and palm rejection, ink
  beautification, and drawing as a primary response mode.
- **Origin:** Weibao, 2026-08-20, same inbox entry as IL-20260820-01.
- **Prior disposition being reopened:** B10 was an explicit descope of
  handwriting and stylus in
  `RESEARCH-BRIEF-learning-platform-2026-08-09.md` line 337, and stream 12
  section 10.3 parked handwriting recognition alongside diagram canvases and
  card scheduling as items that should not land merely because a shared
  contract can name them.
- **Evidence considered:** the descope bundled two different costs. Ink
  authoring carries a device, canvas, and accessibility surface that itembank
  does not need. Recognition of an already-written page carries only model
  accuracy and a correction interface, and it is the enabling half of paper
  intake.
- **Boundary:** handwriting stays an input for producing text, never a stored
  response format the runtime must interpret. Any drawing-as-response question
  remains descoped and keeps the alternatives listed in stream 12 section 11.1
  (labeled relationships, ordered steps, coordinate entry, uploaded image with
  description, oral explanation). Handwriting attachment also remains available
  as an accessibility alternative, which section 11.1 already permits.
- **Disposition:** Registered, narrowed. The stylus-authoring half of B10
  remains descoped and is not reopened by this entry.
- **Revisit trigger:** IL-20260820-01 planning; or a device change that makes
  ink authoring the learner's actual working method rather than a hypothetical.

### IL-20260822-01: An item type that is never scored, for pre-instruction commitment

- **Proposal:** Add a selected-response type whose responses are recorded and
  never scored, used to capture the learner's judgment before instruction so
  the taught answer can be contrasted with it afterwards.
- **Origin:** Weibao supplied photographs of four worked paper assessments on
  2026-08-22 as a fit check on the shipped types. One handout instructs the
  learner to judge each case and, in its own words, go with the initial
  instinct for now. Recorded in `USER-VISION.md`, entry 2026-08-22 on paper
  item formats. No item text from those handouts is in this repository; they
  are third-party published material and the content rule covers them.
- **Evidence considered:** all eight shipped types score dichotomously except
  `short`, which is pending-review rather than unscored. There is no way to ask
  a question whose answer must not become a score. This is the same object as
  the diagnostic named in the 2026-08-22 answer to the notes-to-quiz scope
  question, where checking understanding against a learner's own note must not
  be scored either. One type serves both.
- **Fit:** does not touch the scorer. The runtime keeps owning correctness; this
  type simply has none to own. The recording path is the existing evidence
  store, and the contrast view is presentation.
- **Risks:** an unscored response sitting in the same store as scored ones can
  be mistaken for a miss by anything that counts. The type needs a distinct
  state, not a null score, and every count that reports a denominator must
  exclude it explicitly.
- **Disposition:** registered, unscheduled. Scope it with the paper-note intake
  phase recommended in the same vision entry, since both halves of that entry
  ask for it.

### IL-20260822-02: Capture elimination marks as response data

- **Proposal:** Record which options the learner ruled out, and in what order,
  alongside the option they chose.
- **Origin:** same 2026-08-22 fit check. The photographed quizzes carry crosses
  through rejected options and circles around finalists, on paper, unprompted.
  That is the learner's own reasoning, produced without being asked for.
- **Evidence considered:** the runtime records the chosen option and nothing
  else, so an answer reached by eliminating three options is indistinguishable
  from a guess that happened to land. That distinction is exactly what
  remediation needs and cannot currently see. It is also cheap: the marks are
  produced anyway on paper, so the surface is capturing something that already
  exists rather than adding work for the learner.
- **Fit:** additive to the response record, changes no key and no score. What
  remediation may say changes; what scoring may claim does not.
- **Risks:** eliminations are optional and must stay optional, or the interface
  starts grading process. An empty elimination set means nothing and must not
  be read as a guess.
- **Disposition:** registered, unscheduled.

### IL-20260822-03: Calibrate the bank checks at shared-taxonomy scale

- **Proposal:** Check that the answer-position balance and item-mix warnings
  behave sensibly on a block of roughly twenty stems classified against roughly
  seven shared categories, which is the shape the 2026-08-22 fit check supplied.
- **Evidence considered:** `[TYPE: table]` and `[TYPE: dnd]` support the shape
  structurally, and nobody has run the linter against one at that size. A
  position-balance warning tuned for four-option multiple choice may fire
  constantly or never on a seven-category block, and either way it is noise.
- **Disposition:** registered, small. A fixture and a lint run, not a feature.

### IL-20260822-04: A lint code for the paraphrase rule

- **Proposal:** Add a `lint` check that reports runs of N or more consecutive
  words shared between a bank or lesson and the source files its `## SOURCES`
  registry names.
- **Origin:** executing 13.9-02 on 2026-08-22. The plan states the rule as
  "no sentence of eight or more consecutive words is copied from the source"
  and calls it "the paraphrase lint", but no such lint exists. A hand-written
  check found seven violations in the first authored pass, all of which the
  author believed were paraphrases at the time.
- **Evidence considered:** the rule is load-bearing for a real reason. EMT
  material here derives from a copyrighted textbook, and the vault's own
  recorded miss on this source was a learner answer that was the book's
  sentences near verbatim. An author who does not think to check will not
  discover the problem, and a model under length pressure drifts toward the
  source's phrasing precisely on the passages it understands least.
- **Fit:** the registry and the file paths already exist in `## SOURCES`, so
  the check needs no new grammar. It is a warning, not an error: a defined
  term or a statutory phrase legitimately matches.
- **Risks:** a source file that is large or absent makes the check slow or
  impossible, so it must degrade to a skip with a stated reason rather than
  failing the lint. N needs a default and probably an override.
- **Disposition:** registered, small.

### IL-20260826-01: Course shell, the multi-course container

- **Proposal:** A durable container so itembank holds more than one course at
  once: `workspace` > `course` > `unit` > `treatment`, with the course manifest
  as plain Markdown beside the banks, and all progress derived from the
  evidence store rather than written into the manifest. Full sketch in
  `.planning/COURSE-SHELL-TEMPLATE.md`.
- **Origin:** Weibao 2026-08-26, "as a way to organize multiple courses and
  more, we can use this as an template". Specimen was Navigate2.
- **Evidence considered:**
  `.planning/research/2026-08-26-navigate2-teardown.md`. itembank has banks,
  sessions, lessons and a cross-subject `day` cockpit but no object naming a
  course and its parts, so every additional subject costs bespoke wiring.
- **Fit:** additive. No change to bank parsing, no second scorer, no second
  evidence store. The manifest stays readable in Obsidian per the dual-form
  rule.
- **Boundary:** the shell ships three levels below the workspace. Deeper
  nesting is NOT re-opened here; it is already answered by IL-20260817-01's
  recursive scope object, and the shell must reconcile with that model rather
  than compete with it.
- **Disposition:** Registered, **narrowed 2026-08-26 (same day)** to the
  workspace level only. See the note below.
- **Revisit trigger:** the first phase that adds a second subject (Math 1400 or
  CSCI 1100) to the workspace, or any phase touching progress display.
- **Note 2026-08-26, narrowing after checking shipped code.** Written before
  reading Phase 14B. `course.py`, `graph.py` and `course_package.py` already
  ship the course sidecar, containers with free-text labels nesting arbitrarily
  by `parent`, objectives, treatments, outline projection, and validated
  package export and restore. Course, container, objective and treatment are
  therefore **not** open proposals. What remains genuinely missing is exactly
  one level: the **workspace**, the named set of courses, and how it relates to
  discovery roots. The proposed plain-Markdown course manifest is withdrawn
  outright: the sidecar is one compare-and-swap lineage and a second authored
  manifest would put two object kinds in competition for the same bytes, which
  `course.py` refuses by design.
- **Note 2026-08-27, the narrowed remainder is now a drafted requirement
  awaiting Weibao.** The one level this entry was narrowed to has a proposal:
  `.planning/PROPOSAL-WORKSPACE-2026-08-27.md`, drafting `FILE-04` and
  recommending one of the three shapes `COURSE-SHELL-TEMPLATE.md` line 117 names
  (directory scan, authored Markdown manifest, or a root registry plus a derived
  index). **Disposition is unchanged at Registered**, narrowed, pending Weibao's
  answer; nothing above is reopened and no requirement was edited.
  - **Reconciliation with IL-20260817-01, which this entry's boundary clause
    required.** They do not compete, on one stated line: the scope object is a
    membership set over the typed graph and answers what must be learned and
    whether it may report complete; the workspace is a **locator set** and
    answers only which courses exist on this machine and where their bytes are.
    The workspace therefore carries no objective, no completion predicate, and
    no progress claim, and every rollup question stays with scope and GRAPH-03.
    Scope travels in a package; the workspace is machine-local and must not.
  - **Two findings from the tree that were not known when this entry was
    narrowed.** First, `discovery.py:174-177` already refers in prose to an
    "approved-root registry" that does not exist in the code, so half the
    proposed object is an absence the shipped docstring already names. Second,
    **FILE-01's degraded clause is currently unimplementable**: it promises "an
    unreachable root reports unavailable and the course opens over the last
    valid index", and no index persists anywhere, because discovery writes
    nothing and `surfaces/home.py:254-258` rebuilds from a live scan per
    request. So this gap is not only the mockup's top line; it is a shipped
    requirement with no object under it.
  - **What 16B-04 would invent, located exactly.** `16B-04-PLAN.md:382-384`
    takes the set of courses to be the daemon root's immediate subdirectories
    holding a sidecar, and lines 386 to 395 fall back to the directory basename
    for course identity, which is the name-based identity FILE-03 forbids. The
    plan's flagged-assumptions block at lines 695 to 702 does **not** list this
    assumption. Recorded here so that if the proposal is declined the assumption
    is at least a chosen one.
  - **Revisit trigger, sharpened:** Weibao answering the proposal, or plan
    16B-04 being scheduled, whichever comes first.
- **Note 2026-08-27, accepted. Disposition moves Registered -> Core.** Weibao
  answered the proposal the day it was drafted ("attempt all of them, or using
  the most optimal one, with room for other ones if we need to") and confirmed
  the agent's reading on 2026-08-27 with the instruction to judge by the user
  vision and by future expandability and improvability. The workspace level
  landed as **FILE-04** in `REQUIREMENTS.md`, built as shape C, a registry of
  approved roots plus a derived course index. Shape A survives as FILE-04's
  documented degraded mode (no record or no roots degrades to a single-root
  scan), and shape B survives as a derived, read-only Markdown projection and
  never as a second authored authority. Nothing above is rewritten; the
  2026-08-26 narrowing and the 2026-08-27 pending note stand as recorded.
  **Phase is deliberately still unassigned**, per the owner's selection to
  decide it after the 14B freeze; the traceability row reads Unscheduled.
- **Note 2026-08-27, owner answered the proposal the same day.** Disposition
  moves from Registered, narrowed, to **Core in principle and unscheduled**.
  Quoted verbatim on the shape question: "attempt all of them, or using the most
  optimal one, with room for other ones if we need to,". On the phase question
  he selected: decide after the 14B freeze. Full record, with the agent
  interpretation kept separate from the quotation, is section 9 of
  `.planning/PROPOSAL-WORKSPACE-2026-08-27.md`.
  - **Interpretation, the agent's, flagged for correction.** Read as: adopt
    FILE-04, build the recommended shape (root registry plus derived index), and
    do not foreclose the other two. The shape answer did not name one of the
    three labels, so this reading is stated rather than assumed settled.
  - **Why two of the three collapse in cleanly.** A workspace record with no
    configured roots, falling back to a scan of the daemon root, **is** the
    directory-scan shape, so that shape becomes a runtime degraded mode rather
    than a rival and should be the documented fresh-install default. A readable
    Markdown rendering of the workspace is available as a derived view or
    export.
  - **The one part refused rather than silently narrowed.** Two shapes may not
    both be the source of truth at once. The authored Markdown shape may never
    be an editable second copy competing with the record, which is the
    two-authorities-over-the-same-bytes mistake this entry already invoked on
    2026-08-26 when it withdrew the authored course manifest. Recorded because
    "attempt all of them" read literally would produce exactly that.
  - **Not done, deliberately.** `REQUIREMENTS.md` is unedited and FILE-04 is not
    inserted. One confirming word on the interpretation above should precede a
    write to the binding requirement document, and the phase is deferred by the
    owner's own selection until 14B-06 writes its freeze verdict.
  - **Still open:** whether the interpretation is what he meant; the phase; and
    the record's file format and location, which the packet recommended as JSON
    beside the existing settings and which the answer did not reach.

### IL-20260826-02: Treatment purpose determines the evidence contract

- **Proposal:** A closed set of treatment purposes (`orient`, `read`, `teach`,
  `drill`, `apply`, `check`, `reflect`) where purpose decides both the visual
  role and, load-bearingly, what evidence the runtime will accept and whether
  the treatment may move a mastery number. `reflect` never becomes truth.
- **Origin:** Moodle 4.x activity-purpose tokens, observed 2026-08-26. The
  mechanism exists in the specimen and every purpose is left blank.
- **Evidence considered:** the specimen colours activities by purpose as pure
  decoration. Making the same taxonomy decide the evidence contract is what
  separates a legible list from a trustworthy one.
- **Fit:** restates existing authority rules in a form the UI can render. No new
  authority.
- **Disposition:** **Duplicate in its proposed form, narrowed and registered in
  its residue.** See the note below.
- **Note 2026-08-26, correction after checking shipped code.** The proposed
  seven-value set (`orient`, `read`, `teach`, `drill`, `apply`, `check`,
  `reflect`) is **withdrawn**. `graph.py` already ships `TREATMENT_KINDS`, an
  eleven-value closed vocabulary canonical in `REQUIREMENTS.md` as TREAT-01:
  `direct-reading`, `excerpt`, `guided-lesson`, `notes-or-terms`,
  `worked-example`, `visual-or-demonstration`, `practice`, `formal-test`,
  `assessment-first-diagnostic`, `learner-artifact`, `human-review`. Proposing a
  parallel vocabulary for the same concept is the second-authority mistake this
  repository legislates against, and it was proposed only because the shipped
  code was not read first.
- **What survives, and is the registered part:** TREAT-01 says which treatment
  an objective gets; it does not say **which treatment kinds may emit evidence
  that moves a GRAPH-03 dimension and which structurally cannot**. Three kinds
  share one hole, `direct-reading`, `excerpt` and `visual-or-demonstration`,
  all of which produce nothing the runtime can verify. That hole is
  IL-20260826-08.
- **Revisit trigger:** with IL-20260826-08.

### IL-20260826-03: Coverage, mastery and claimed as three unmerged numbers

- **Proposal:** The workspace first page shows three quantities that may never
  be combined into one bar: `coverage` (units treated), `mastery` (objectives
  with sufficient evidence), `claimed` (treatments the learner marked done by
  their own word). `claimed` renders visibly weaker. If only one fits, show
  `mastery`.
- **Origin:** Weibao 2026-08-26, "dont forget the first page for the course
  either, like how it shows the completeness".
- **Evidence considered:** teardown section 2c. The specimen's headline
  `0% complete` counts activity completion, and of 435 activities only 41 carry
  a grade item, so 394 (90.6%) of the denominator is a self-pressed checkbox.
  Ticking every box without opening anything reads as 100% complete beside an
  empty gradebook.
- **Fit:** direct application of the separate-state-axes rule (accepted
  content, workflow state, epistemic confidence are independent).
- **Disposition:** **Duplicate of GRAPH-03, retained as field evidence for it.**
  See the note below.
- **Note 2026-08-26, correction after checking REQUIREMENTS.md.** GRAPH-03
  already specifies something strictly stronger: a nine-field tuple over seven
  permanently separate dimensions (design coverage, participation, settled
  evidence, current retention, formal completion, selected enrichment,
  uncertainty), no single aggregate completion, mastery or readiness score,
  separate denominators for required, required-choice and enrichment, and the
  rule that adding enrichment can never lower completion. It is owned by
  Phase 16C. The proposed three numbers were a weaker restatement and are
  withdrawn as a model.
- **What survives:** the 90.6% measurement is concrete field evidence for why
  GRAPH-03's no-single-score clause is correct, useful whenever someone asks
  why one friendly percentage would not be simpler. Two display questions are
  handed to Phase 16C rather than answered here: participation must not be
  silently sourced from an unverifiable claim, and seven dimensions do not fit
  on a course card, so which one shows at card size (and whether showing one
  re-creates the aggregate problem by the back door) needs deciding.
- **Revisit trigger:** Phase 16C, when GRAPH-03 is implemented.
- **Note 2026-08-27, disposition partly reopened by owner ruling.** This entry
  was dispositioned Duplicate because GRAPH-03 was stronger. GRAPH-03 was
  amended on 2026-08-27 (IL-20260827-01), so the ground under half of that
  disposition moved and the entry is corrected rather than left misleading.
  - **Still Duplicate:** the seven separate dimensions remain GRAPH-03's and
    are unchanged by the ruling, so the proposed `coverage` / `mastery` /
    `claimed` triple is still a weaker restatement of them and is still
    withdrawn as a model.
  - **No longer excluded:** the reason a single card figure was impossible was
    GRAPH-03's no-aggregate clause, and that clause is now amended. An
    aggregate display over the seven dimensions is permitted from 2026-08-27.
    The open card-size question this entry handed to Phase 16C, which one
    number shows when only one fits, is therefore no longer blocked; it is a
    live design question rather than a foreclosed one.
  - **Unchanged and still the entry's main value:** the 90.6% measurement. It
    stays as field evidence about Navigate2, and the overturn note in Phase 16
    synthesis 12.4 records that it was weighed and overruled rather than
    forgotten.

### IL-20260826-04: Pool depletion, a bank-seen denominator

- **Proposal:** Track and display how much of a bank the learner has ever seen,
  per category and overall, as unanswered over total.
- **Origin:** TestPrep practice-test builder, observed 2026-08-26:
  `Airway and Breathing (115 / 115)` over `Qbank (690 QUESTIONS)`,
  `0 Taken, 690 Remaining`.
- **Evidence considered:** itembank records attempts but has no notion of bank
  coverage, so it cannot answer "am I practising, or recycling the same twelve
  items". The number is cheap to derive from existing evidence.
- **Open design question:** "seen" is not "attempted" is not "mastered", and a
  shuffled variant is not a new item. The definition must precede the display.
- **Disposition:** Registered.
- **Revisit trigger:** first phase that adds an item selector or a bank report.

### IL-20260826-05: Error-driven reselection

- **Proposal:** A selector that composes a form from items the learner
  previously answered incorrectly.
- **Origin:** TestPrep checkbox `Include questions previously answered
  incorrectly`, observed 2026-08-26.
- **Evidence considered:** itembank already holds the attempt evidence needed
  and has no selector that uses it. Complements rather than duplicates the Anki
  export path, which owns scheduling.
- **Boundary:** selection only. Scheduling stays Anki's, per the 2026-08-22
  notes-to-quiz disposition.
- **Disposition:** Registered.
- **Revisit trigger:** with IL-20260826-04.

### IL-20260826-06: A reading view across sources

- **Proposal:** A second view over existing `read` bindings, grouped by source
  rather than by unit, showing what is bound, which objectives cite it, what has
  been read, and coverage of the source as distinct from coverage of the course.
  Readings keep their default placement inside the unit.
- **Origin:** Weibao 2026-08-26, "this one is where the readings are in the
  sections/chapters, which is a good enough way for now but we can have a better
  page or tab for reading and more".
- **Evidence considered:** in the specimen a reading is one row among nine,
  legible per chapter and illegible as a book. Placement inside the unit is
  still correct, because a reading belongs to the objective it serves.
- **Fit:** a renderer over existing bindings. No new durable object. Links and
  never relocates, per the edit-files-where-they-live rule.
- **Blocked by:** IL-20260826-08. There is no evidence event for having read
  something.
- **Disposition:** Registered, **narrowed 2026-08-26 (same day)** to the
  cross-course view only.
- **Note 2026-08-26, narrowing after checking APP-01 and 16B.** APP-01 already
  gives every course a `Sources` area, routed in 16B-01 and 16B-05 as
  `/course/<id>/sources`. The per-course half of this idea is therefore already
  specified and is withdrawn. What survives is the **cross-course** half:
  grouping bindings by source rather than by course, so a book that serves three
  courses reads as one book, with coverage of the source distinct from coverage
  of any course using it. Nothing in APP-01 covers that, because APP-01's IA is
  course-first by design.
- **Revisit trigger:** once a reading evidence event exists (IL-20260826-08),
  and not before 16B ships the per-course `Sources` area.

### IL-20260826-07: A time axis for the course shell

- **Proposal:** Give the shell deadlines and pacing, so a unit can be due and a
  course can be behind or ahead.
- **Origin:** agent observation 2026-08-26 while reviewing the shell against
  Weibao's actual autumn.
- **Evidence considered:** the specimen's course carries no dates at all, which
  suits self-paced EMT and does not suit Math 1400 or CSCI 1100, which are
  graded courses with due dates and exam weeks. `day` currently infers pace from
  a hand-maintained plan table, which is the closest existing mechanism.
- **Open question:** whether this is a shell concern or belongs to `day`, which
  already owns the cross-subject time view. Possibly the shell holds the dates
  and `day` renders them.
- **Disposition:** Registered, **narrowed 2026-08-26 (same day)**.
- **Note 2026-08-26, narrowing after checking 16B-04.** The shelf already ships
  `due` as one of six attention states, so the display half is specified. What
  is not specified is **where `due` comes from**: nothing in `graph.py` holds a
  date, and no requirement says what makes a container due. The residue is the
  data question, not the display question.
- **Revisit trigger:** before the first non-EMT subject is added, since a graded
  college course with real deadlines is when the gap becomes load-bearing.

### IL-20260826-08: An evidence event for a non-scored treatment

- **Proposal:** A typed, dated `self_report` evidence event for treatments that
  produce no runtime verdict, chiefly `read` and `orient`, visibly a learner
  claim and structurally incapable of moving a mastery number.
- **Origin:** falls out of IL-20260826-02 and blocks IL-20260826-06.
- **Evidence considered:** no such event type exists. The specimen's answer,
  `Mark as done`, is rejected as IL-20260826-11, so the gap is real and the
  obvious fix is the wrong one.
- **Open design question:** the honesty story. A claim the learner can make
  freely is useful for orientation and dangerous the moment anything aggregates
  it, so what may consume it needs stating before it ships.
- **Disposition:** Registered.
- **Revisit trigger:** with IL-20260826-01; it is the smallest blocking piece.

### IL-20260826-09: A media treatment purpose

- **Proposal:** A `watch` purpose distinct from `read` and `teach`, for video
  and simulation treatments.
- **Origin:** agent observation 2026-08-26. Thirty of the specimen's 32
  course-level activities are video (Virtual Mentor, Ride-Along, Soft-Skill
  Simulations).
- **Evidence considered:** media is currently folded into `read` or `teach` in
  IL-20260826-02's closed set, and its evidence story matches neither: a video
  is neither a citable passage nor a lesson with checkpoints.
- **Cost driver:** widening a closed set is cheap now and expensive once
  manifests exist in the wild.
- **Disposition:** **Duplicate.** Withdrawn 2026-08-26, same day.
- **Note 2026-08-26.** TREAT-01 already ships `visual-or-demonstration`, which
  covers video and simulation. The perceived gap was an artifact of
  IL-20260826-02's withdrawn seven-value set, which had no media kind. With
  TREAT-01 as the vocabulary there is nothing to add. The real question about
  video, that it emits no verifiable evidence, is IL-20260826-08 and is shared
  with `direct-reading` and `excerpt`.

### IL-20260826-10: Teaching pool separate from exam-fidelity pool

- **Proposal:** Distinguish items authored to teach from items authored to
  mirror the real examination, so a blueprint can draw from the right
  population.
- **Origin:** agent observation 2026-08-26. The specimen keeps per-chapter
  `Assessment in Action` items and a 690-item exam Qbank as separate
  populations in separate systems.
- **Evidence considered:** itembank treats a bank as a bank. The distinction may
  already be expressible with existing objective and difficulty metadata, in
  which case this needs a tag and not a structure.
- **Disposition:** Backburner, pending a check of whether existing metadata
  already covers it.
- **Revisit trigger:** first blueprint-driven form assembly.

### IL-20260827-01: Percent permitted on a course card, by owner override

- **Proposal:** Permit a percent character and a progress percentage on a
  course shelf card, overriding plan 16B-04's prohibition.
- **Origin:** Weibao, 2026-08-27, verbatim in `USER-VISION.md`: "Percent is
  fine even if it breaks contract, since uservision over any other contracts
  and more".
- **Authority:** the owner, exercising the precedence rule the same statement
  establishes: `USER-VISION.md` outranks any other contract in this repository.
  That precedence is the larger half of the ruling and is not limited to
  percentages.
- **Evidence considered:** the 2026-08-26 Navigate2 teardown measured a
  completeness bar at 90.6% self-report and argued a card percentage is a
  fabricated measurement. That argument stands as an observation about
  Navigate2 and is overruled as a constraint on itembank. The agent argued the
  other way on 2026-08-26 and records the reversal rather than softening it.
- **What was retained without instruction:** every percentage in the mockup is
  computed from a real numerator over a real denominator the records hold
  (objectives with an accepted treatment binding, over objectives), and a card
  whose record cannot be read shows `unknown` rather than a number. Weibao may
  strike this and ask for a synthesized figure; it was kept only because it was
  free.
- **Disposition:** Accepted, owner ruling. Not a proposal awaiting review.
- **Amendments: all four APPLIED 2026-08-27**, at Weibao's explicit instruction
  ("yes, apply all four amendments") given after they were listed. Each was
  amended in place with its original wording preserved for trace, never deleted:
  1. `REQUIREMENTS.md` GRAPH-03, the clause "no single aggregate completion,
     mastery, or readiness score is produced".
  2. Phase 16 synthesis section 12.4, the single-aggregate-score hard
     rejection. Append-only: overturned by a dated note carrying evidence and
     authority, never deleted.
  3. Plan 16B-04: the line 30 must-have truth, the line 39 `status: kept`
     prohibition, threat T-16B-04-05, and the three percent-absence assertions
     at lines 301 and 384. Unamended, Phase 16B will fail its own tests.
  4. IL-20260826-03 above, whose Duplicate disposition rests on GRAPH-03.
- **Applied state, 2026-08-27.**
  1. `REQUIREMENTS.md` GRAPH-03: clause marked amended inline, with an
     amendment note naming what is permitted, what is unchanged (the seven
     dimensions stay separate underneath), and what was deliberately not
     widened by inference.
  2. Phase 16 synthesis 12.4: the row is marked `OVERTURNED 2026-08-27` and an
     overturn note follows the table. The row itself is untouched, per the
     append-only rule.
  3. Plan 16B-04: an amendment banner opens the objective, and all five percent
     sites are amended in place (frontmatter must-have, `status: kept`
     prohibition now `overturned-by-owner-2026-08-27`, the Task 2 behaviour
     assertion, the Task 2 docstring rule, and threat T-16B-04-05's
     mitigation). Frontmatter structure was re-checked after editing.
  4. IL-20260826-03: disposition corrected. Still Duplicate on the seven
     dimensions; no longer foreclosed on the single-card-figure question.
- **Two further sites found while applying, and amended.** The four listed
  above were not the whole set. `16B-RESEARCH.md` Pitfall 3 and its
  progress-reporting anti-pattern row carried the same clause and were amended
  the same day, narrowed rather than deleted: the danger is now a percentage
  with no denominator behind it, not the percent character. Plan 16B-04's
  inputs list restated the prohibition in a sixth place and was amended too.
  Leaving these would have left the amended plan disagreeing with its own
  inputs.
- **One site deliberately left for later.** `16B-DECISIONS.md` `## D7` carries
  the same prohibition but the file does not exist yet: plan 16B-01 creates it
  and 16B-01 has not run, because its precondition check halts on Phase 16A. D7
  must therefore be **authored in its amended form** when that file is first
  written, rather than written in the old form and retrofitted.
- **The replacement rule adopted throughout, stated once.** A percentage must
  carry the numerator and denominator it was derived from, and a record
  supplying neither reports indeterminate rather than an invented number. This
  was not instructed; it is the agent's reading of what the ruling permits
  versus what it was reacting against, and Weibao may strike it.
- **Revisit trigger:** before Phase 16B executes. The precondition check still
  halts on Phase 16A, which is the remaining blocker; the amendments no longer
  are.
- **Reconsideration condition:** none. This is an owner ruling, not an agent
  recommendation, and it is recorded so that a future agent does not re-argue
  the 2026-08-26 position as though it were still open.

### IL-20260905-01: Read the confidence field itembank already writes

- **Proposal:** Give the recorded per-attempt `confidence` its first consumer.
  Cross confidence with correctness and surface confident-and-wrong as a
  distinct error signal with its own stated denominator, readable by selection
  and by the blueprint report. Collect the field on the quiz surface, which
  currently hardcodes `confidence=None`.
- **Origin:** Moodle's certainty-based marking question behaviour, read
  2026-09-05 during the open-source absorption pass Weibao asked for in chat;
  full reasoning in `.planning/research/2026-09-05-open-source-absorption.md`
  section 2.
- **Evidence considered:** `confidence` is already captured end to end and read
  by nothing: `surfaces/cli.py:988`, `surfaces/daemon.py:3608`,
  `evidence.py:448`, the SQLite column at `evidence.py:1150`, the migration
  default at `surfaces/migrate.py:344`. EVID-07 asked for it and said outright
  that nothing needed to read it yet. `surfaces/quiz.py:305` passes `None`, so
  the offline sitting produces no signal at all. No consumer exists in
  `retention.py`, `selection.py`, `blueprint.py`, `progress_claims.py`, or
  `auditor.py`.
- **Fit:** no new field, no new item type, no format surface, no second store.
  `REQUIREMENTS.md:1116` already names the failure this exposes, a confident
  wrong answer with the right nouns, as something the tool must not mistake
  for knowledge.
- **Boundary:** the diagnostic half only. Moodle also adjusts the *mark* by
  certainty, and that half is refused here for now: a certainty-weighted score
  hides its own derivation, against `REQUIREMENTS.md` lines 972 to 981 and the
  no-aggregate rule at `IDEA-LEDGER.md:800`. If a weighted mark is ever wanted
  it is an additive extension inside the one scorer per `IL-20260815-05` and
  needs its own argument, not this entry.
- **Cost driver:** collecting the field in the offline quiz page without adding
  friction to a sitting, and choosing a denominator that stays honest when the
  learner leaves confidence unset (`None` means not marked, per the conventions).
- **Disposition:** Registered.
- **Revisit trigger:** the first phase that touches selection weighting, the
  blueprint report, or the quiz submit path.

### IL-20260905-02: `n_mastery` as the one honest rollup form worth borrowing

- **Proposal:** Adopt "N of the last M attempts at or above a threshold" as a
  permitted leaf-level progress claim, stated with both numbers visible, in the
  vocabulary `progress_claims` already uses.
- **Origin:** the Canvas LMS outcomes API calculation methods, read 2026-09-05;
  see the absorption pass section 3.
- **Evidence considered:** Canvas offers `decaying_average`, `n_mastery`,
  `highest`, and `latest` behind one switch. `n_mastery` is the only one whose
  numerator and denominator survive into the claim. It degrades honestly at
  small M, which `blueprint.py`'s `uncertainty_for()` already bands.
- **Fit:** it is a countable claim, not a percentage, so it violates neither
  the no-aggregate rule nor the stated-denominator rule.
- **Boundary:** orthogonal to the owed G5 default rollup choice. ROLLUP-DIM and
  ROLLUP-MAP decide the shape of the tree; this decides what a leaf may assert.
  It is input to that decision, not a substitute for it, and the choice remains
  Weibao's.
- **Disposition:** Registered.
- **Revisit trigger:** the G5 rollup decision, or the first phase that adds a
  progress claim kind.

### IL-20260905-04: Question as generator, at authoring time only

- **Proposal:** Let an author write one parameterized form and expand it into N
  concrete items, each minted with its own id and hash and written into the
  bank through the existing `author-bank` write, lint, fix loop. Aimed at Math
  1400, where practice value lies in many instances of one form.
- **Origin:** PrairieLearn's core idea that a question is a generator producing
  and grading its own variants, read 2026-09-05; see the absorption pass
  section 4.
- **Evidence considered:** PrairieLearn reports use across roughly 800 courses
  at 20 universities, so the pedagogy is not speculative. `STATE.md` records
  that no Math 1400 course exists yet, so nothing is disturbed by deciding this
  before the course is built.
- **Boundary, stated as part of the proposal and not as a caveat:** expansion
  happens at authoring time and emits ordinary items. Runtime variant
  generation is refused, because it collides at once with stable item identity
  and `content_fingerprint()`, with evidence keyed per item id, and with the
  rule at `IDEA-LEDGER.md:843` that a shuffled variant is not a new item.
  Authoring-time expansion adds no runtime concept, no second parser, and no
  second scorer.
- **Licence boundary, which generalizes past this entry:** nothing is vendored.
  PrairieLearn CE is AGPLv3 (parts MIT, an Enterprise directory proprietary),
  Canvas is AGPLv3, Moodle is GPLv3, and `ebooklib` was parked on exactly this
  in `IL-20260828-05` and decided as `D-14C-2`. Since external installation
  became a supported goal (2026-08-14) and Phase 18 packages a desktop app, the
  practice `COURSE-SHELL-TEMPLATE.md` line 336 recorded for one Moodle specimen
  is the general rule: absorb observed behaviour, format semantics, and
  vocabulary; never the code; never assume a licence from a publisher's
  reputation. PrairieLearn's 15 shared OER banks are also not a corpus that can
  simply be taken: they sit behind an account and an instructor course space.
- **Cost driver:** the parameter and constraint language, and keeping the
  expansion reproducible so a re-expansion does not remint ids for unchanged
  variants.
- **Disposition:** Registered, sequenced behind the existence of a Math 1400
  course.
- **Revisit trigger:** the first phase that builds Math 1400, or any phase
  proposing runtime item generation, which this entry refuses in advance.

### IL-20260905-05: Bind an open-licensed algebra text as a Math 1400 source

- **Proposal:** When Math 1400 is built, bind an OpenStax or LibreTexts algebra
  title (College Algebra, Elementary Algebra) as a first-class source through
  the ordinary discovery and binding path, with direct reading available as a
  treatment.
- **Origin:** the absorption pass section 5, 2026-09-05. This is the only
  content finding in that pass and the only one that unblocks something.
- **Evidence considered:** `STATE.md` records that no Math 1400 or CSCI 1100
  course exists and that the single real sitting to date was EMT. An
  open-licensed text is a bound source whose rights answer can actually be
  recorded, unlike the AAOS-derivative EMT material whose exposure is already
  an accepted risk.
- **Boundary:** licensing is per title and not uniform. OpenStax's own
  licensing article describes the library as CC BY-NC-SA while individual
  titles and LibreTexts mirrors are commonly CC BY, so the licence is read from
  the title at binding time and recorded in rights state, never inferred from
  the publisher. NC constrains nothing for Weibao's own study and would
  constrain a packaged redistribution, which is the same Phase 18 asymmetry as
  the AGPL finding in `IL-20260905-04`. No bulk import; direct reading is
  already a treatment the source-to-course path supports.
- **Disposition:** Registered.
- **Revisit trigger:** the first Math 1400 course build.

### IL-20260905-06: The course engine needs an operating surface

- **Proposal:** Give the shipped course operations a door. Extend
  `surfaces/daemon.API_ROUTES` with the course operations (create, discover,
  bind, objective and treatment, blueprint, accept, package) and mirror each
  into `ROUTE_CLI` and `SURFACE_PARITY`, whose existing test already fails on a
  route without a twin. No new durable object, no new format surface.
- **Origin:** the measured gap pass of 2026-09-05,
  `.planning/research/2026-09-05-what-the-vision-still-needs.md` section 2.2,
  run at Weibao's request to find what the vision still needs.
- **Evidence considered, all measured rather than read:** the JSON API is 15
  routes and every one is assessment, lesson, source import, or a first-run
  shelf action. Every `/course/` route is a GET, including the six areas and
  the lesson view, so the Build and review area that
  `SOURCE-TO-COURSE.md` defines as where proposals, diffs, approval, rejection
  and undo live is read-only over HTTP. The CLI has 47 top-level commands and
  none is course-shaped; `shelf` is four first-run walkthrough actions and
  `source import` stops after extraction. Meanwhile 387 KB of course engine
  across eleven modules is frozen and tested. The 17B tracer passed because it
  drove the Python modules directly.
- **Fit:** this is the 2026-08-21 defect at milestone scale. `/lesson/<stem>`
  returned 200 with nothing linking to it, and no framework test could see it
  because every test knew the URL. The same is now true of the course engine.
- **Sequencing consequence, which is the part easy to miss:** Phase 999.3's
  success criterion 1 exposes one MCP tool per `API_ROUTES` entry. Built today
  it would expose fifteen assessment tools and no course tools. **999.3 is not
  blocked on MCP work; it is blocked on there being routes worth exposing.**
  This entry is its prerequisite, and the generated tool table is the natural
  acceptance test for this entry: if it can build a course, the routes are
  right. The MCP spec revision 999.3 was designed against, 2026-07-28, is still
  current as of this date, and `scripts/ocr_mcp.py` is existing in-repo
  precedent for the transport.
- **Boundary:** dispatch, request schemas, and parity rows only. The handlers
  exist. Nothing here adds a second parser, scorer, or evidence store, and
  every mutation still goes through `journal.commit_operation` with its
  expected-base fingerprint.
- **Disposition:** Registered.
- **Revisit trigger:** the next milestone's scoping, or any plan for Phase
  999.3, which should not start before this lands.

### IL-20260905-07: Plug the agent seam into a door

- **Proposal:** Bind `surfaces/agent_operation.py` to one route and one CLI
  twin, so an accepted agent proposal becomes exactly one
  `journal.commit_operation` with a visible undo, reachable from the Agent tab
  and from an agent client rather than only from a fixture.
- **Origin:** the same measured pass, section 2.3.
- **Evidence considered:** 17A-07 shipped the run, propose, accept state
  machine in full: four states, one sentence of copy for each of the fourteen
  `model_adapter.ADAPTER_CODES`, exactly one journal commit per accept, an undo
  path, and a passing roundtrip suite. Its only importer outside itself is
  `surfaces/visual_fixture.py`, the screenshot generator. It is bound to no
  route and no command.
- **Fit:** Weibao's 2026-08-21 entry named the gap precisely, that the Agent
  tab and `journal.commit_operation` were "two programs in one window" and the
  skill buttons "run nothing". 17A-07 built the machine that joins them. What
  it did not do is give it an entrance, so the claim moved from unimplemented
  to implemented-and-unreachable.
- **Boundary:** reach, not authority, exactly as the 2026-08-21 interpretation
  states. The agent may operate what the learner can operate and propose what
  an author can propose. It may not settle a mark or release a key, and this
  entry changes nothing about that.
- **Dependency:** rides on `IL-20260905-06`, since the door it needs is one of
  that entry's routes.
- **Disposition:** Registered.
- **Revisit trigger:** the next milestone's scoping, alongside
  `IL-20260905-06`.

### IL-20260905-08: Turn the in-product model backend on, locally first

- **Proposal:** Make a local profile active in `model_backend`, so the
  director, the treatment recommender, and the seeding loop run against real
  material for the first time in this working copy.
- **Origin:** the same measured pass, sections 2.4 and 4.
- **Evidence considered:** `itembank.json` sets `model_backend.active` to `""`,
  which `schemas/settings.schema.json` documents as disabling model calls
  entirely, and the one registered profile names a placeholder model. So every
  AI action in this project's history has been an external agent editing files
  in a repository, which is not the operation protocol the product defines. The
  product's own AI path has never been exercised here, and `seed` refuses by
  name without a backend.
- **Why local rather than hosted:** the work the in-product path actually does
  is high-volume and mechanical (extract objectives, propose a treatment, draft
  a bank, run lint and fix, propose a next action), which is a poor use of paid
  tokens and is also the half that must degrade rather than block. The judgment
  work is planning and review, which an external agent already does and which
  does not need this path. Weibao's cost constraint is on the record twice.
- **What changed externally:** ROCm 7.2 (March 2026) reached out-of-the-box
  parity with CUDA for Ollama, LM Studio, llama.cpp, and vLLM on RDNA 3, so the
  setup cost that made the 7900 XTX path a someday item is largely gone.
  Reported 24 GB throughput at Q4 is roughly 40 tok/s for a 27B, 72 tok/s for a
  26B mixture model, and 96 tok/s for an 8B; Qwen 3 32B is the quality pick
  that still fits.
- **Fit:** the adapter already normalizes transports behind one `invoke`, so
  this is a settings change, not code, and a hosted profile stays registered
  beside it so the comparison stays a settings change too. This is the seam
  discipline of `IL-20260815-02` being used rather than described.
- **Boundary:** the runtime still settles scoring, session state, keyed
  disclosure, and evidence. A backend being on changes what can be drafted, not
  who decides.
- **Disposition:** Registered.
- **Revisit trigger:** the first attempt to build a course through the
  product's own director rather than through an external agent.

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

### IL-20260826-11: Self-report completion as a progress primitive

- **Proposal considered:** Adopt the specimen's `Mark as done` model, a manual
  per-activity checkbox that the learner presses, aggregated into a course
  completeness percentage shown on the workspace card.
- **Origin:** Navigate2, observed 2026-08-26. Considered because it is cheap,
  familiar, and solves the real problem that most treatments produce no verdict.
- **Evidence considered:** teardown sections 2, 2c and 2d. In the observed
  course 435 activities exist, 41 carry a grade item, and 394 complete only by
  the checkbox. The card's headline `0% complete` is therefore 90.6%
  self-report, and a learner who opens nothing and ticks everything reads as
  100% complete beside an empty gradebook.
- **Exact reason:** it makes presentation state into attainment. The number
  cannot distinguish a learner who studied from one who tidied a list, so it is
  worse than no number, because it is trusted. It also collapses three
  independent axes (accepted content, workflow state, epistemic confidence)
  into one bar.
- **Conflicting rule:** "Presentation state never grants authorization" and the
  separate-state-axes rule, both in CLAUDE.md; and the runtime invariant, since
  a self-pressed checkbox is a verdict settled by something other than the
  runtime.
- **Retained alternatives:** IL-20260826-08 keeps the useful half, a typed dated
  claim that is visibly a claim and can never aggregate into mastery.
  IL-20260826-03 keeps it visible as `claimed`, beside and weaker than
  `coverage` and `mastery`.
- **Date:** 2026-08-26.
- **Reconsideration condition:** none foreseen for aggregation into a progress
  figure. The claim-capture half is already retained, so there is nothing left
  to reconsider unless the axes rule itself changes.

### IL-20260826-12: Flat equal-size category pools as a blueprint

- **Proposal considered:** Follow the specimen's Qbank shape, six subject
  categories holding exactly 115 items each, as the model for organising an
  itembank exam bank by category.
- **Origin:** TestPrep practice-test builder, observed 2026-08-26.
- **Evidence considered:** the six categories are uniform to the item. The real
  NREMT test plan weights its domains unevenly, so the uniformity is a
  content-production convenience rather than a measurement decision.
- **Exact reason:** equal pools per category silently teach the wrong
  proportions. A learner drawing evenly across categories practises a
  distribution the examination does not use, and the practice looks faithful
  precisely because the numbers are tidy.
- **Conflicting rule:** the 2026-08-24 accepted principle that practice should
  mirror the real examination's format, recorded in `USER-VISION.md`, which was
  already applied there to item types and applies here to domain weights.
- **Retained alternatives:** a blueprint that states weights explicitly, per
  the existing NREMT pinning work; and a linter check that notices suspiciously
  flat category counts, which is a candidate to fold into IL-20260822-03's
  calibration work rather than a separate check.
- **Date:** 2026-08-26.
- **Reconsideration condition:** a target examination that genuinely weights its
  domains equally, in which case flat pools are correct for that blueprint and
  wrong as a default.

### IL-20260828-01: A paced lesson presentation, slideshow with checkpoint items

- **Proposal:** A `paced` presentation mode over an already authored lesson: the
  same Markdown reads as a continuous document in Obsidian and projects as an
  ordered sequence of steps, with optional narration (captions and speed
  control), a table of contents that jumps rather than gates, and checkpoint
  items drawn from the bank and scored by the one scorer inside the flow.
- **Origin:** Weibao 2026-08-28, "maybe slideshow with quiz style as one of the
  options and more". Specimen was the Navigate2 Interactive Lecture SCORM
  player, inspected the same day with his authorization.
- **Evidence considered:**
  `.planning/research/2026-08-28-navigate2-interactive-lecture-shell.md`. The
  specimen's player is module, chapter, page, with one named template per page,
  a page completed event, and exactly one assessment hook. It is also the only
  activity of the observed 435 that carries a grade item, so questions inside
  the deck are the vendor's whole answer to how teaching produces evidence.
- **Fit:** additive, and deliberately not a new durable object. The lesson stays
  the artifact; pacing is a projection of it, which keeps the dual-form rule and
  avoids a second authored file competing for the same content. Checkpoints are
  ordinary bank items through the runtime, so there is no second scorer and no
  second evidence store.
- **Boundary:** position in the deck is presentation state. It is resumable and
  it never counts as coverage, mastery or progress. A step that emits no
  evidence says so, per `IL-20260826-02`.
- **Disposition:** Registered.
- **Revisit trigger:** the first phase that touches the lesson renderer or the
  treatment set, or the resolution of the recorded open question on whether a
  style is a semantic transformation or a cosmetic theme.
- **Open questions:** carried in section 4 of the research file, chiefly whether
  a checkpoint attempt is the same session object as a sitting.
- **Note 2026-08-28, boundary source left open.** Asked where step boundaries
  should come from, Weibao answered that there are several possibilities and
  likely more than were listed, so nothing was narrowed. Eight candidates and
  their consequences are preserved in section 4a of the research file, marked
  non-exhaustive. Two things were established without deciding: computed
  boundaries have unstable identity across edits, which breaks resume and step
  citation and is a correctness property rather than a preference; and the real
  fork is whether pacing is an authored property of the lesson or a view
  preference of the reader, which should be settled before any syntax is. The
  candidates are mostly composable as a precedence ladder, not rivals.
- **Note 2026-08-28, the three open questions are answered.** Under a quoted
  same-day delegation from Weibao ("just decide for each accordingly to
  uservision of modularity and improvability and achiving the end goal"), the
  fork, the evidence contract, and the wrong-answer disclosure are decided in
  `.planning/archive/DECISIONS-PACED-LESSON-2026-08-28.md` as D-PACED-1, D-PACED-2 and
  D-PACED-3. They are labelled there as agent judgments made under that
  delegation, not as his own words, and each carries a reconsideration
  condition. In short: pacing is authored, read through a precedence ladder
  (explicit id-carrying marker, else configured heading level, else the whole
  document, which is today's behaviour), with a reader control that may only
  coarsen; a checkpoint attempt is an ordinary attempt in the one evidence
  store inside a distinct lesson-run session, labelled so it never reaches a
  blueprint denominator by default; and a wrong checkpoint rules out and
  confirms in tiers the runtime releases, with the key held to tier 3.
- **Note 2026-08-31, implemented as Phase 16D.** The revisit trigger fired
  (the first phase touching the lesson renderer) and the registration is
  built: plans 16D-01 through 16D-03 executed 2026-08-31
  (`.planning/phases/16D-paced-lesson/`), with `[STEP: <id>]` and
  `[LESSON-PACE:]` as the authored surface, the lesson-run session kind and
  the `lesson_run` context label in the one store, the runtime-released
  tier ladder, and the paced view over the existing lesson mode seam and
  6.2 gate bands. IL-20260828-02's refusal held (no timer anywhere) and
  IL-20260828-03's constraint held (the pager gates on attempted, never
  correct; the TOC never gates). The freeze waits on the 16D-04 tracer and
  Weibao's sat-through review.

### IL-20260828-02: The timed slide lock

- **Proposal considered:** Adopt the specimen's `slidelock`, a configured timer
  (observed at 5000 ms) that holds the learner on a step before advancing is
  permitted, as a way to make a paced lesson produce a defensible engagement
  signal.
- **Origin:** `Shell/config.xml` in the Navigate2 Interactive Lecture package,
  observed 2026-08-28.
- **Evidence considered:** the same package sets media to remote with override,
  so the treatment cannot run unplugged; the two settings sit side by side and
  fail the same way, by putting the vendor rather than the learner in control of
  whether study can proceed.
- **Exact reason:** it counts elapsed seconds as learning. It is the same
  category error as `IL-20260826-11`, presentation state standing in for
  attainment, made worse because the learner does not even assert it. A reader
  who is faster than the timer is punished and a reader who walks away is
  credited.
- **Conflicting rule:** "Presentation state never grants authorization" in
  CLAUDE.md, and the degrade-never-block rule for the remote media half.
- **Retained alternatives:** if a step genuinely must be attempted before moving
  on, that is a checkpoint item under `IL-20260828-01` and the verdict is the
  runtime's. Dwell time may still be recorded as a labelled non-scored signal
  under `IL-20260826-08`, where it can never aggregate into mastery.
- **Date:** 2026-08-28.
- **Reconsideration condition:** none foreseen for gating navigation. Recording
  dwell as evidence is already retained separately, so nothing here is left
  pending.

### IL-20260828-03: Gating a step on an attempted checkpoint

- **Proposal:** A step in a paced lesson may be marked as a gate, so forward
  navigation waits until the learner has attempted the checkpoint on it. Jumping
  backward, and the table of contents, stay unrestricted.
- **Origin:** Navigate2 Interactive Lecture, observed 2026-08-28. In the observed
  39 page deck exactly four pages carry `locked="true"` (12, 22, 32, 38) and page
  12 is a Knowledge Check, so the attribute marks checkpoints and gates them.
- **Evidence considered:**
  `.planning/research/2026-08-28-navigate2-interactive-lecture-shell.md` sections
  1a and 2.
- **Fit:** distinct from `IL-20260828-02`, which is rejected, and the two must not
  be decided together. A timer counts clock time as learning and the learner does
  not even assert it. A gate on an attempt counts an attempt, which is evidence,
  and the verdict is the runtime's under the existing invariant.
- **Boundary:** gate on *attempted*, never on *correct*. Gating on correctness
  turns a teaching checkpoint into a mastery gate, strands a learner who cannot
  pass, and gives the checkpoint an authority a teaching-pool item should not
  have. Backward navigation and the table of contents are never gated, since
  presentation state grants no authorization.
- **Disposition:** Registered, constrained as above.
- **Revisit trigger:** the first plan that implements `IL-20260828-01`.

### IL-20260828-04: An inline-select cloze as a teaching checkpoint form

- **Proposal:** A checkpoint form where the learner completes a sentence by
  choosing a term from a dropdown embedded in the sentence, several stems to a
  step, submitted together and disclosed per stem.
- **Origin:** the Knowledge Check on page 12 of the observed deck, 2026-08-28.
- **Evidence considered:** same research file. The specimen submits four stems at
  once and then opens a per stem feedback panel, so batching the submit does not
  force a single verdict. The panels observed restate each stem rather than
  teaching the distinction, which is the part not worth copying.
- **Fit:** it is neither one of the seven shipped types nor one of the five NREMT
  types the 2026-08-24 vision entry pinned practice to. It is a teaching form, so
  it belongs in the teaching pool of `IL-20260826-10` and must never enter a
  blueprint denominator or an exam-fidelity mix.
- **Boundary:** if it ships, it ships as an additive extension inside the one
  scorer, per the 2026-08-15 clarification `IL-20260815-05`. Not a second parser
  and not a second scorer.
- **Disposition:** Registered. Sequenced behind `IL-20260828-01`, since a
  checkpoint form with nothing to sit inside is premature.
- **Revisit trigger:** the paced-mode plan, or any phase adding an item type.
- **Open question:** whether this is genuinely a new type or a presentation of a
  `table` item, which already carries several rows each choosing from a set. If
  the latter, it costs no format surface at all.

### IL-20260828-05: ebooklib, parked on an AGPL decision

- **Proposal:** Adopt `ebooklib` 0.20 for EPUB import, which would supply a
  maintained spine, manifest, and navigation-document API in place of roughly a
  hundred lines of hand-written OPF and container parsing.
- **Origin:** the Phase 14C research pass, 2026-08-21, which read `ebooklib`'s
  own PyPI license metadata and found AGPL. `14C-CONTEXT.md`'s out-of-scope
  list refuses PyMuPDF on exactly these grounds and does not mention
  `ebooklib`, because the finding is newer than that document.
- **Conflicting rule:** `SUPPLY-CHAIN-POLICY.md` section 2.4 routes copyleft and
  no-license artifacts to an explicit Weibao decision before adoption.
- **Evidence considered:** for personal use alone AGPL costs nothing, since its
  obligations trigger on distribution and on network service use. For the
  recorded product goal it is expensive and one-way: `ROADMAP.md` Phase 18 is a
  packaged desktop app a friend installs, and the 2026-08-14 vision entry made
  external installations a supported goal, so distribution would trigger the
  copyleft source-offer obligation over the whole product rather than over the
  one adapter.
- **Retained alternative, and the one taken:** stdlib `zipfile` plus
  `xml.etree`, read through the hardened `_read_zip_part` and
  `_parse_xml_safely` seam plan 14C-02 built, so the zip-bomb and
  entity-declaration guards cover EPUB with no new code and no new licence.
- **Disposition:** Parked (needs an explicit Weibao AGPL decision), exactly as
  PyMuPDF is parked by the 2026-08-17 note on `IL-20260815-07`. Parked, not
  rejected.
- **Decided:** 2026-08-27 by Weibao, recorded in full as `D-14C-2` in
  `.planning/phases/14C-source-adapter-registry/14C-DECISIONS.md`, which carries
  his answer, his verbatim rider, and the reasoning. This entry is the ledger's
  durable pointer to that record, appended 2026-08-28 by plan 14C-07 Task 1,
  which owed it and had not been written.
- **Revisit trigger:** a real EPUB proves unreadable by the stdlib path; or the
  product's licensing posture changes, for example a decision that itembank
  ships as AGPL open source, at which point `ebooklib` costs nothing; or the
  stdlib path's extraction fidelity or reading presentation is visibly worse
  than what a library would give, and the gap matters to a learner rather than
  only to a test. The third trigger is Weibao's own, from the rider quoted in
  `D-14C-2`.

### IL-20260905-03: `decaying_average` and the other collapsing rollups

- **Proposal considered:** adopt Canvas LMS's `decaying_average` outcome
  calculation (and its `highest` / `latest` siblings) as a mastery rollup, so a
  learner sees one moving number per objective.
- **Origin:** the Canvas LMS outcomes API, read 2026-09-05 during the
  open-source absorption pass; `.planning/research/2026-09-05-open-source-absorption.md`
  section 3.
- **Evidence considered:** Canvas puts four methods behind one configuration
  switch. `decaying_average` weights recent attempts more heavily and emits a
  single number from which the numerator and denominator cannot be recovered.
  `highest` and `latest` discard the rest of the record entirely.
- **Reason for rejection:** a number whose derivation is not visible is exactly
  the collapse this project refuses. It cannot state what it counted, so it
  cannot degrade honestly at small denominators, and it silently merges the
  separate state axes (accepted content, workflow state, epistemic confidence)
  that the separate-state-axes rule keeps apart.
- **Conflicting rule:** the no-aggregate rule at `IDEA-LEDGER.md:800`; the
  stated-denominator requirements at `REQUIREMENTS.md` lines 972 to 981, which
  refuse a mastery percentage from sparse evidence; and `blueprint.py`'s
  `uncertainty_for()`, which was written to band a denominator rather than
  smooth it away.
- **Retained alternative:** `IL-20260905-02`, N of the last M at or above a
  threshold, which carries both numbers into the claim and is the one Canvas
  method worth taking.
- **Date:** 2026-09-05.
- **Reconsideration condition:** an external consumer (an institution, a
  transcript, an LTI grade passback) that requires a single scalar per
  objective as a condition of interoperating. Even then it is a boundary
  adapter's output, computed at the edge with its inputs recorded, and never a
  progress claim itembank shows the learner as truth.

### IL-20260906-01: contextual stuck detour (F1)

- **Idea:** open passage-specific help or a prerequisite refresher and return to
  the same reading location.
- **Disposition:** Deferred pending the feature opportunity audit.
- **Owner:** next feature opportunity audit agent.
- **Evidence class:** recommendation, not a verified implementation gap.
- **Origin:** assistant suggestion retained at the user's request on 2026-09-06.
- **Dependency and cost driver:** existing lesson navigation, permitted help,
  source grounding, and accessible return-state integration.
- **Unblocking condition:** audit existing support and identify a learner-visible
  gap with a bounded verification or prototype.
- **Route:** `FEATURE-OPPORTUNITY-AUDIT-PROMPT.md`, F1.

### IL-20260906-02: personal confusion notebook (F2)

- **Idea:** retain recurring concept confusions with examples and links to
  comparison practice in learner-owned notes.
- **Disposition:** Deferred pending the feature opportunity audit.
- **Owner:** next feature opportunity audit agent.
- **Evidence class:** recommendation, not a verified implementation gap.
- **Origin:** assistant suggestion retained at the user's request on 2026-09-06.
- **Dependency and cost driver:** notes, objective links, and misconception
  practice integration without treating notes as scoring authority.
- **Unblocking condition:** map overlap with existing note and practice plans
  and demonstrate the missing connection, if any.
- **Route:** `FEATURE-OPPORTUNITY-AUDIT-PROMPT.md`, F2.

### IL-20260906-03: learning produces editable notes (F3)

- **Idea:** accumulate learner predictions, explanations, selected highlights,
  and corrected reasoning into an editable study document.
- **Disposition:** Deferred pending the feature opportunity audit.
- **Owner:** next feature opportunity audit agent.
- **Evidence class:** recommendation, not a verified implementation gap.
- **Origin:** assistant suggestion retained at the user's request on 2026-09-06.
- **Dependency and cost driver:** existing learner-note workflow, attribution,
  citations, durable edits, and portable output.
- **Unblocking condition:** reconcile with the existing active-annotation vision
  and note capabilities before proposing any additive work.
- **Route:** `FEATURE-OPPORTUNITY-AUDIT-PROMPT.md`, F3 and combined F1/F3 flow.

### IL-20260906-04: changed-context transfer challenges (F4)

- **Idea:** apply a concept in a changed situation, diagnose a broken example,
  or explain the limits of a rule.
- **Disposition:** Deferred pending the feature opportunity audit.
- **Owner:** next feature opportunity audit agent.
- **Evidence class:** recommendation for examining an existing contract theme.
- **Origin:** assistant suggestion retained at the user's request on 2026-09-06.
- **Dependency and cost driver:** transfer authoring, subject-specific quality
  review, activity reachability, and runtime-owned assessment behavior.
- **Unblocking condition:** verify whether current transfer requirements produce
  usable activities and identify any authoring or delivery gap.
- **Route:** `FEATURE-OPPORTUNITY-AUDIT-PROMPT.md`, F4.

### IL-20260906-05: time-aware continuation (F5)

- **Idea:** propose a ten-minute activity, full lesson, or review session with
  an evidence-backed reason and an exact return point.
- **Disposition:** Deferred pending the feature opportunity audit.
- **Owner:** next feature opportunity audit agent.
- **Evidence class:** recommendation, not a verified implementation gap.
- **Origin:** assistant suggestion retained at the user's request on 2026-09-06.
- **Dependency and cost driver:** current scheduling and resume behavior,
  uncertain duration estimates, and sensible interruption boundaries.
- **Unblocking condition:** inspect current continuation flows and establish
  whether a time-budget extension adds measurable learner value.
- **Route:** `FEATURE-OPPORTUNITY-AUDIT-PROMPT.md`, F5.

## Feature opportunity audit follow-up, 2026-09-06

This additive record follows the user's instruction to run the saved audit.
The evidence and broader inventory are in
[`research/2026-09-06-feature-opportunity-audit.md`](research/2026-09-06-feature-opportunity-audit.md).
The report is a recommendation, not implementation approval or a milestone
expansion. Earlier entries and unresolved questions above remain intact.

| Existing ID | Audit evidence and remaining question | Proposed disposition and route, not yet approved |
|---|---|---|
| IL-20260906-01 (F1) | Glossary, prerequisite filters and deep-link helpers exist. Complete selected-passage help and exact return were not observed. | Prototype only if the report's P-A tracer finds a missing connection. First verify existing navigation in 19D. |
| IL-20260906-02 (F2) | Learner-note roles and pair practice exist separately. Their learner-facing connection remains unverified. | Prototype after F3 capture is usable, owned by note/selection maintainers. Preserve incorrect notes as private claims. |
| IL-20260906-03 (F3) | Note trio and promotion checks pass. Sampled surface searches found no consumers of note APIs. | Core reach defect under existing NOTE obligations, routed through 19D to the note owner. Do not create a second note format. |
| IL-20260906-04 (F4) | Transfer is already an activity purpose and quality obligation. Metadata does not prove a changed-context learning task. | Core existing 19D representative-unit review, with 15B/16A owners and report P-B acceptance criteria. |
| IL-20260906-05 (F5) | Due-work recommendations and resume helpers exist. A stateless resume helper proves neither durable passage return nor a duration planner. | Prototype for time-budget choice after exact resume verification. Reuse IL-20260826-07 and report P-C. |

Existing dispositions remain the recorded decisions until these recommendations
are adopted. The original audit-deferral questions now have evidence, with
live UI and benefit validation still open as named in the report.

The report also reuses IL-20260826-06 for source reading, IL-20260905-01 for
confidence diagnostics, APP-04 for search, the 17C addendum for explicit restore
losses, and the existing authoring/quality obligations. The September 5 restore
addendum names all five losses but does not carry the omitted content. No new
entry duplicates those capabilities. Synthesis sections 12.2, 12.3 and 12.5
retain the broader registered, prototype and backburner portfolio.

### IL-20260906-06: return briefing separates changes from due work

- **Idea:** when returning to a course, distinguish the actual stopping point,
  changes to accepted material, and evidence-backed review needs in one brief
  explanation. Never imply that a source revision means the learner forgot it.
- **Disposition:** Prototype candidate, not approved for implementation.
- **Owner:** APP and evidence maintainers for any future prototype.
- **Evidence class:** inference and recommendation from existing resume,
  revision and retention primitives. No complete working flow was observed.
- **Origin:** feature opportunity audit O11, an assistant proposal extending
  existing return/recovery work rather than a new user quotation.
- **Existing overlap:** `surfaces/ia.py::loop_resume_state`,
  `retention.py::recommendation`, APP-01, accepted revisions and source
  staleness. The new proposal composes their explanations without creating a
  second history store.
- **Dependency and cost driver:** saved position, available accepted-revision
  comparison and evidence snapshot. Medium estimated maintenance cost from
  missing baselines, objective renames and stale sources.
- **Revisit trigger:** 19D establishes usable exact resume and a learner needs
  orientation after absence or a content revision.
- **Verification and falsifier:** compare a return after revision with a return
  after absence only. The learner must distinguish changed material from due
  review. Existing separate cues serving the same job equally well falsify the
  need for a combined briefing.
- **Authority and recovery:** canonical content/evidence remain unchanged.
  The briefing is derived and disposable, uses approved local records, names
  unavailable comparisons and stays useful as linear text offline.
- **Route:** report O11 and A5, future optional prototype after Reach resume
  evidence. No new phase or binding scope is created.

Operation note: this audit creates one report and appends this ledger section.
It changes no user quotation, runtime file or accepted product requirement.
Undo removes the report and this section only, preserving prior and concurrent
work. Verification results live in the report's validation section.

### IL-20260906-07: local-first desktop with a SaaS-quality experience

- **Idea:** make itembank feel like one approachable and dependable product,
  with guided first use, a clear course home, consistent navigation, durable
  operation state, recovery, and understandable settings.
- **Disposition:** Core product-experience direction. It changes the acceptance
  lens for current work and creates no new architecture or phase.
- **Owner:** `SOURCE-TO-COURSE.md` for the binding direction, Phase 18 for
  installation and first use, the UI character audit for the bounded
  presentation proposal, and Phase 19D for the continuous learner walkthrough.
- **Evidence class:** direct user direction, supported by observed gaps in
  `UI-CHARACTER-AUDIT-2026-09-06.md`, `VISION-PLAN-AUDIT-2026-09-06.md`, and
  `research/2026-09-06-feature-opportunity-audit.md`.
- **Origin:** the 2026-09-06 SaaS-entry-point conversation, promoted verbatim to
  `USER-VISION.md`.
- **Dependency and cost driver:** the shipped Tauri shell and shared local
  runtime remain the delivery base. Costs come from connecting existing doors,
  consistent UI behavior, packaging verification, and human usability review.
- **Boundary:** SaaS-quality names the experience and not the hosting model.
  Accounts, multi-tenancy, hosted storage, cloud gradebooks, billing, and cloud
  synchronization are not implied. Electron is not required.
- **Verification and falsifier:** a learner enters through the packaged or
  canonical browser-served shell, creates or resumes a course, follows visible
  controls through a representative learning loop, observes durable agent-job
  state, recovers from an interruption, and returns home without a guessed URL
  or CLI repair. If existing Phase 18 and 19D evidence already proves this with
  the reviewed UI, no additional product-experience work is justified.
- **Authority and recovery:** canonical learning records stay local and the one
  runtime retains assessment authority. UI state is derived. Hosted model use
  follows declared rights and egress. Existing application revisions and local
  files remain the recovery base.
- **Relationship:** extends the paid-subscription substitution entry without
  recreating its business model. It confirms the Phase 13 shell decision and
  coalesces existing APP, Phase 18, UI-audit, and Reach obligations.

### IL-20260906-08: comprehensive future UI character

- **Idea:** redesign the future learner interface comprehensively so it has a
  distinctive, coherent learning-workspace identity. Do not preserve the
  current visual appearance merely because it shipped first.
- **Disposition:** Core visual-experience direction, sequenced after the
  current Reach milestone's functional and journey evidence.
- **Owner:** `UI-CHARACTER-AUDIT-2026-09-06.md` for the amended visual plan and
  the future UI phase for prototypes, selection, implementation, and review.
- **Evidence class:** direct user direction, informed by user comparison of the
  running Syntax Lab interface with the current itembank UI. Syntax Lab is
  comparative product evidence, not a selected design system.
- **Origin:** the 2026-09-06 comprehensive future UI character statement,
  promoted verbatim to `USER-VISION.md`.
- **Dependency and cost driver:** first establish the representative course
  journey through R5 and R6. Costs include comparative prototypes, shared
  component implementation, all-surface migration, responsive and
  accessibility verification, visual assets where chosen, theme preference
  migration, and human review.
- **Boundary:** the redesign may replace current colors, typography roles,
  geometry, layout, component styling, theme catalogue, and default look. It
  may not replace runtime scoring or disclosure authority, canonical local
  files, learner evidence, accessible operation, responsive behavior, durable
  preferences without migration, or recovery guarantees.
- **Verification and falsifier:** compare materially different directions on
  the same representative shelf, course, lesson, practice, assessment,
  evidence, settings, empty, unavailable, and recovery states. The user selects
  a direction that feels more distinctive and coherent. Keyboard, screen
  reader, reflow, contrast, reduced motion, and task-completion checks pass. If
  the redesigned states do not improve recognition, navigation, and task
  clarity in review, visual novelty alone does not justify adoption.
- **Migration and recovery:** retain the prior accepted application revision.
  Map or explicitly retire saved looks and accents. Unknown or invalid saved
  settings fall back visibly and recoverably. Reversal restores the prior
  visual revision without changing course, assessment, or evidence data.
- **Relationship:** strengthens IL-20260906-07 and the earlier structured-studio
  direction. It partly supersedes preservation-first clauses in the UI
  character audit while retaining their observed defects and quality gates.

### IL-20260907-01: extensible presentation and capability composition

- **Idea:** make the complete learner-facing presentation adaptable through
  named extension seams. Presentation profiles arrange shared primitives.
  Appearance themes provide semantic visual tokens. Capability adapters plug
  readers, activities, editors, source views, agent panels, exporters, and
  integrations into shared operations without requiring a frontend fork.
- **Disposition:** Core for the semantic presentation and registration
  contract. The two selected presentation profiles are Registered. New
  capability adapters begin as Prototype until their representative behavior
  and degradation gates pass.
- **Owner:** `UI-CHARACTER-AUDIT-2026-09-06.md` owns presentation architecture.
  `EXTENSION-DELIVERY-2026-09-06.md` owns the reusable registration shape.
  Each capability phase owns its adapter and evidence.
- **Evidence class:** direct user direction plus recommendation based on the
  existing selected-profile architecture and the verified EXT-01 through
  EXT-03 registration work.
- **Dependency and cost driver:** prove the two profiles on one representative
  shelf-to-lesson-to-practice slice. Cost comes from cross-profile state
  coverage, accessibility, settings migration, compatibility, packaging, and
  recovery rather than from registration metadata alone.
- **Boundary:** canonical content, parser, scorer, assessment disclosure,
  evidence, rights, route identity, and recovery authority are not plugins.
  Registration metadata grants no authority. External code loading remains
  Deferred under EXT-05 and the supply-chain policy.
- **Verification and falsifier:** add a second real registration at a named
  seam without duplicating state or authority. Render representative states in
  both profiles across appearance modes, desktop, mobile, keyboard, screen
  reader, unavailable behavior, migration, and recovery. If the shared shape
  adds special cases or does not reduce duplication, keep the seam local and
  do not generalize it.
- **Origin and relationship:** direct 2026-09-07 statement in
  `USER-VISION.md`. Extends IL-20260816-01 and IL-20260906-08. It does not
  reopen IL-20260815-04.

### IL-20260907-02: comparative home projections and transition-complete UI

- **Idea:** compare resume-first, shelf-first, agenda-first, and within-course
  path presentations over identical course data and routes. Treat the complete
  transition graph, including Home, Back, exact resume, interruption, practice
  completion, quiz and exam completion, pending review, remediation, later
  return, and course completion, as part of the UI contract rather than gaps to
  decide screen by screen. Keep the supporting platform and repository evidence
  renewable through named re-research triggers.
- **Disposition:** Core for the shared transition graph and state matrix.
  Prototype for the four home presentations until comparable learner review.
- **Owner:** `notes/2026-09-07-home-and-transition-ui-scope.md` owns the initial
  synthesis. `PROMPT-UI-FLOW-AND-OPEN-SOURCE-ABSORPTION-2026-09-07.md` owns the
  deeper research packet. `UI-CHARACTER-AUDIT-2026-09-06.md` remains the
  implementation-direction owner after evidence is reconciled.
- **Evidence class:** direct user direction plus observed screenshot evidence
  and current official product documentation. Applying external patterns to
  itembank remains a recommendation until prototype and learner review.
- **Dependency and cost driver:** the active Reach milestone remains unchanged.
  Later work depends on a populated representative course, the two registered
  presentation profiles, stable route identity, and real assessment sessions.
  Costs come from repository research, comparable prototypes, durable
  navigation and resume state, cross-mode transition tests, responsive and
  accessibility coverage, and user review.
- **Boundary:** all projections use the same parser, scorer, assessment
  disclosure, evidence, route identity, rights, and recovery authority. A home
  view may project or arrange state. It may not invent progress, completion,
  scores, recommendations, or a second session. External repositories are
  prior-art evidence only and no code, markup, styles, assets, fixtures, or
  wording are copied.
- **Verification and falsifier:** walk every row in the scope note's transition
  matrix through both presentation profiles and each retained home projection
  at desktop and narrow widths. Verify Home, Back, reload, stop, finish, resume,
  and profile switching preserve one session, exact location, focus or a
  meaningful successor, unsaved-work handling, and assessment disclosure. A
  home projection is superseded if it serves no distinct learner job or is less
  clear than a simpler composition in user review.
- **Re-research triggers:** reopen affected evidence when a named platform or
  repository materially changes relevant behavior, a prototype or real sitting
  falsifies a recommendation, a new itembank capability introduces uncovered
  states, or a source becomes stale, contradicted, unavailable, or differently
  licensed. Record access date and upstream version or commit when available.
  Do not repeat the entire landscape without a changed assumption or named gap.
- **Origin and relationship:** direct 2026-09-07 statements in
  `USER-VISION.md`. Extends IL-20260906-06, IL-20260906-08, and IL-20260907-01.
  It concretizes APP-01, APP-02, FLOW-01, and FLOW-02 without changing their
  authority. It does not supersede Measured Field Guide or Learning Trajectory
  Deck.

### IL-20260907-03: agent-operable learning harness product identity

- **Idea:** define itembank as a local-first learning harness for people whose
  stable contracts let replaceable AI agents construct, operate, inspect, and
  improve source-grounded courses without transferring assessment authority to
  a model.
- **Disposition:** Core product identity. AI training, reinforcement learning,
  prompt optimization, and general model evaluation are not the primary product
  identity. A specific learner-serving use of those techniques may be
  Registered later under the same contracts.
- **Owner:** `SOURCE-TO-COURSE.md` owns the binding product definition.
  `AGENT-WORKFLOW.md` owns agent operation. The runtime owns scoring,
  assessment disclosure, session state, and accepted evidence.
- **Evidence class:** direct user question and approval on 2026-09-07, plus an
  interpretation of the existing source-to-course and agent-operable workspace
  contracts.
- **Dependency and cost driver:** no new implementation dependency follows from
  the identity clarification. Any adjacent AI-facing capability must name its
  learner job, durable objects, evidence authority, rights and egress,
  validation, degradation, maintenance, and recovery. Its cost comes from those
  capability-specific gates rather than from the product framing.
- **Boundary:** the learner is the beneficiary. Agents are replaceable
  operators and collaborators. Parser, scorer, keyed disclosure, accepted
  evidence, permissions, and recovery remain canonical authorities rather than
  learned or swappable verdicts.
- **Verification and falsifier:** future contracts, requirements, plans, and
  product descriptions call it a learning harness only when the learner-facing
  system remains primary. A proposal that makes model improvement the primary
  user outcome must be treated as a separate product-direction decision, not
  inferred from this entry.
- **Origin and relationship:** direct 2026-09-07 statements in
  `USER-VISION.md`. Confirms the 2026-08-13 source-to-course and course-generator
  entries and clarifies the agent-operable workspace contract. It supersedes
  no existing learner or agent capability.

### IL-20260906-09: Syntax Lab-inspired CS Dojo

- **Idea:** add a focused CS Dojo course surface inspired by Diego's Syntax
  Lab, with concise coding prompts, a real editor, declared context,
  deterministic checks, actionable feedback, retry, controlled reveal, and
  support for additional programming languages through adapters.
- **Disposition:** Prototype. Validate the learning, execution, authority, and
  maintenance model before adding a durable activity or item format.
- **Owner:** the future activity-capability owner for the learner experience,
  the runtime owner for scoring and disclosure, and the security owner for
  execution isolation. D3.1 of the consolidated audit remediation plan owns the
  current prototype route.
- **Evidence class:** direct user direction plus observed implementation
  evidence from the locally reviewed Syntax Lab repository. The review verified
  1,579 Python and JavaScript drills across 40 language/category groups and a
  passing JavaScript worker regression suite. It also found missing durable
  objective evidence, client-owned scoring and reveal, incomplete worker
  coverage, and high-severity dependency audit findings.
- **Dependency and cost driver:** R6 must establish the representative course
  journey. Each language adds runtime distribution, sandbox, resource-limit,
  package-policy, fixture, accessibility, offline, security-update, and
  compatibility costs. Multi-file projects and compiled languages cost more
  than single-file interpreted drills.
- **Boundary:** the Dojo is an optional objective treatment, not a second course
  system. Language adapters execute and normalize results. The existing runtime
  settles scores, disclosure, session state, and evidence. Hidden tests cannot
  require undeclared learner identifiers or context. Unavailable execution has
  a useful non-executable fallback. Short function challenges are one drill
  mode, not the curriculum or the complete CS coursework model. The Dojo must
  distinguish code reading and prediction, tracing and explanation, typed
  construction, debugging and test writing, tool or multi-file work, and
  learner-owned labs or projects. Executable code is not assumed to be one new
  universal item type before the activity contract separates practice,
  assessment, and learner artifacts.
- **Verification and falsifier:** a synthetic objective completes prompt,
  execution, per-test feedback, retry, reveal, objective-linked evidence,
  reload, timeout recovery, and offline use through at least two adapters.
  The representative slice also includes one predict-run-explain activity, one
  debugging or test-construction activity, and one bounded multi-file lab or
  learner artifact with an explicit review state. Hostile-code and
  keyed-disclosure tests pass. If the slice can demonstrate only isolated
  function submissions, it remains a narrow drill capability and cannot claim
  to represent the CS coursework extension. If executable practice does not
  improve transfer beyond an existing static treatment for the chosen
  objective, the Dojo is not justified for that treatment.
- **Migration and recovery:** no current lesson or bank migrates automatically.
  The prototype is removable without altering canonical course or evidence
  files. Any accepted schema change requires spec, lint, schema, export,
  roundtrip, threat, accessibility, and clean-restore coverage.
- **Relationship:** extends IL-20260906-08 by applying the Syntax Lab reference
  to a specific learning surface. The 2026-09-07 direction broadens the
  prototype from Syntax Lab-style drills to CS coursework while keeping those
  drills as one mode. It concretizes existing runnable-code and transfer goals
  without making coding execution a universal requirement.

### IL-20260908-01: authenticated source acquisition and transcript completion

- **Idea:** add a source acquisition layer that discovers and downloads an
  authorized Canvas course, preserves its hierarchy and per-object provenance,
  sends each supported object through the existing source adapters, and
  completes the media path with caption discovery and optional ASR.
- **Disposition:** Prototype for Canvas course exports and local ASR. Registered
  for live Canvas API acquisition. Backburner for browser-session capture.
  Registered research targets include Moodle backup, IMS Common Cartridge,
  SCORM, Blackboard, D2L Brightspace, Panopto, Kaltura, and YouTube captions.
- **Owner:** the post-Reach source acquisition phase proposed in
  `SOURCE-ACQUISITION-EXTENSION-AUDIT-2026-09-08.md`.
- **Evidence class:** direct user direction plus verified codebase audit. Phase
  14C already imports transcript files and one public web page. It registers
  ASR as unavailable. Canvas LTI is delivery rather than acquisition.
- **Dependency and cost driver:** reuse the Phase 14C adapter, locator, rights,
  fingerprint, and journal contracts. Cost comes from authenticated discovery,
  pagination, rate limits, batch recovery, credentials, per-resource rights,
  loss reporting, incremental reconciliation, and real-course validation.
- **Revisit and promotion gate:** start after Reach. Promote the export path
  only after an authorized Canvas export completes preview, import, bind,
  interruption and resume, recheck, undo, and offline restore with one outcome
  per discovered object. Promote live API acquisition only after credential
  isolation and a real learner-approved Canvas walkthrough pass.
- **Boundary:** acquisition creates raw snapshots and manifests. Existing
  adapters remain the only extraction path. The runtime remains the only scorer
  and disclosure authority. Credentials never enter course artifacts or logs.
  Unknown rights remain restrictive. Student submissions and grades are
  excluded from the first slice.
- **Relationship:** extends IL-20260815-07 and IL-20260907-01. It turns the
  earlier Navigate2 scrape specimen into a general acquisition need without
  authorizing unrestricted crawling or external package execution.

### IL-20260908-02: defer local AI and the new Math 1400 sitting

- **Idea:** allow the post-Reach UI phase to proceed without repairing live
  local-model proposal generation or completing a new Math 1400 sitting now.
- **Disposition:** Deferred for both validation legs.
- **Owner:** the future local-AI compatibility owner for proposal generation;
  Phase 19D for the representative sitting and dependent restore observation.
- **Evidence class:** direct user direction on 2026-09-08 plus observed 19D
  evidence that the provider returned malformed proposal output and no sitting
  began.
- **Dependency and cost driver:** local AI requires a provider-compatible
  structured-output contract and regression fixture. The sitting requires
  reviewed source-grounded content, runtime session execution, evidence review,
  and dependent export and restore observation.
- **Revisit trigger:** reopen local AI when the user prioritizes offline model
  operation. Reopen the sitting when the user requests representative learner
  validation or before a release claims Math 1400 learning outcomes.
- **Boundary:** no deferred result is a pass. No agent may invent a proposal,
  score, mastery result, recommendation, human acceptance, or restore result.
  Parser, scorer, disclosure, evidence, rights, and recovery authority remain
  unchanged.

### IL-20260908-03: reader action menu and external-source workspace

- **Idea:** let a learner double-click selected reader text to request a
  definition or related help, and let the reader open and work alongside PDF,
  EPUB, and slide sources with stable source locations and course bindings.
- **Disposition:** Prototype for double-click and the contextual action menu.
  Registered for a shared external-source reader over existing adapters.
- **Owner:** the future reader and lesson-capability phase under
  `SOURCE-TO-COURSE.md`; source-format support remains owned by the source
  adapter registry.
- **Evidence class:** direct user direction on 2026-09-08 plus existing shipped
  glossary behavior and planned PDF, EPUB, and PPTX adapter coverage. The exact
  double-click interaction has not been validated with learners.
- **Dependency and cost driver:** reuse semantic term roles, stable locators,
  source bindings, rights grants, and the shared operation protocol. Cost comes
  from text-selection conflicts, cross-input accessibility, embedded renderer
  security, locator fidelity, annotations, large-file performance, offline
  packaging, and format-specific loss reporting.
- **Revisit and promotion gate:** promote the interaction only after a learner
  can select text, request a definition, use the additional actions, dismiss
  and reopen the panel, and resume reading by pointer, keyboard, touch, and
  screen reader. Promote each external format only after a representative file
  passes navigation, citation and locator fidelity, binding, offline reopen,
  unavailable-state, and clean-restore checks.
- **Boundary:** double-click is optional, not the only activation path. The
  source file remains separately identified and is not silently copied,
  converted, edited, or superseded. Unknown rights remain restrictive. Reader
  help does not reveal keyed content or create a second scoring authority.
- **Relationship:** extends the 2026-08-13 and 2026-08-20 definition entries,
  IL-20260815-07 source intake, and the Phase 14C EPUB decision. It composes
  existing reader and adapter seams instead of introducing a parallel content
  model.

### IL-20260908-04: selective competitor absorption

- **Idea:** reuse source-grounded lesson generation and supporting components without making a simulated multi-agent classroom the default product.
- **Disposition:** Prototype.
- **Owner:** competition absorption coordinator, then the existing course-authoring and reader owners.
- **Evidence class:** direct user direction on 2026-09-08, pinned upstream code inspection, and hands-on OpenMAIC and DeepTutor trials.
- **Dependency and cost driver:** one source-to-draft boundary, source citations, caller-owned models, accepted revisions, portable fallbacks, and existing validation. Cost comes from model calls, package maintenance, fidelity checks, and runtime integration.
- **Promotion gate:** one bounded source produces a useful candidate lesson without classroom orchestration. Source-selection assistance verifies revision and canonical passage before preparing context. Production adoption still requires artifact validation, review, rights, recovery, and reader integration.
- **Boundary:** no imported scoring, evidence, classroom roster, or generated executable authority. Optional multi-agent teaching remains Backburner under IL-20260908-05.
- **Relationship:** narrows the OpenMAIC fork exploration and extends IL-20260908-03. `research/competition-2026-09-08/ABSORPTION.md` owns reconciliation.

### IL-20260908-05: optional simulated classroom

- **Idea:** optional teacher/classmate personas, agent discussion, avatar staging, and narrated classroom playback.
- **Disposition:** Backburner.
- **Owner:** future learning-treatment owner.
- **Evidence class:** user excludes this overhead from current needs. OpenMAIC demonstrations establish product behavior rather than learning efficacy.
- **Dependency and cost driver:** a learner job where dialogue adds value, additional model calls, latency, audio/media dependencies, and accessible alternatives.
- **Revisit trigger:** explicit user demand or a bounded trial showing a learning benefit over one direct explanation that justifies the additional time and cost.
- **Retained alternative:** single-artifact generation and learner-triggered contextual help. This disposition does not require a product fork.

### IL-20260908-07: wider competitor absorption in the native workflow

- **Idea:** implement useful source, lesson, interaction, authoring, and review patterns from the full competitor landscape.
- **Disposition:** Registered.
- **Owner:** existing course, lesson, reader, review, and source-adapter owners by capability.
- **Evidence class:** direct user instruction on 2026-09-08. Specific implementation selection is an engineering interpretation.
- **Dependency and cost driver:** existing semantic rendering and runtime authority first. Source-model work, generation quality, extraction dependencies, and scheduler conformance require their own evidence.
- **Promotion gate:** a native learner flow with source fidelity, static meaning, runtime disclosure, regression checks, and named human review limits.
- **Boundary:** no simulated classroom, voice, imported scorer, or automatic dependency adoption. No claim of whole-platform parity.
- **Relationship:** extends IL-20260908-04 and IL-20260908-06. The full landscape and implementation record remain in `research/competition-2026-09-08/ABSORPTION.md`.

### IL-20260908-06: interactive visual teaching without conversation

- **Idea:** absorb direct lesson interaction, bright text emphasis, and useful small visual effects without conversational staging.
- **Disposition:** Registered.
- **Owner:** existing lesson-rendering and reader workstream.
- **Evidence class:** direct user direction on 2026-09-08. The earlier OpenMAIC polynomial control trial demonstrates an interaction, not a learning-effect measurement.
- **Dependency and cost driver:** semantic lesson roles, existing interaction capabilities, portable content, accessible controls, and motion preferences. Avoid a second renderer or a model call for routine visual interaction.
- **Promotion gate:** demonstrate a useful highlighted explanation and learner-controlled interaction in the existing surface. Verify keyboard and touch behavior, readable contrast, reduced motion, and a study-usable static fallback. Highlights must not imply mastery or accepted evidence.
- **Boundary:** no character chat, turn-taking, simulated discussion, or narration dependency. Staged reveals and subtle motion are candidate interpretations, not mandatory effects on every lesson.
- **Relationship:** extends IL-20260908-04 and clarifies that IL-20260908-05 does not exclude visual richness. Adoption criteria live in `research/competition-2026-09-08/ABSORPTION.md`.
