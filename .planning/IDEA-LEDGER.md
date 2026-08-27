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
