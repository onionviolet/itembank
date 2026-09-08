# Consolidated audit remediation plan

Date: 2026-09-06. Status: active. R0 is reconciled, and R1 and R2 are
implemented and browser-verified. Integrated preflight has unrelated failures
recorded below.
Owner: the executing agent for each bounded packet, with existing phase owners
retaining their responsibilities. This is a sequencing and routing overlay,
not a new milestone or a replacement for phase contexts.

User request, preserved verbatim:
> Based on audits, make on plan to plan to how to address while being most token efficient and more, like how to use lesser agent for lesser tasks and more

Interpretation: consolidate the audits into one economical route to fixes and
verified use. Match model capability to uncertainty. Reduce repeated reading,
coordination, and testing without reducing acceptance standards. This task
mechanic is recorded here rather than promoted into product vision.

## Evidence and current baseline

Use these owning reports instead of copying their findings:

| Source | What it establishes | Limit |
|---|---|---|
| [Vision audit](VISION-PLAN-AUDIT-2026-09-06.md) | VPA-01 to VPA-08 and existing owners | Planning coverage does not prove shipped behavior |
| [UI audit](UI-CHARACTER-AUDIT-2026-09-06.md) | Observed control defects and proposed A1.1 to A1.5 | Sampled dark-mode screens, no complete accessibility review |
| [Feature audit](research/2026-09-06-feature-opportunity-audit.md) | Existing components, missing journey evidence, optional prototypes | Most whole-journey behavior remains unobserved |
| [Reach milestone](REACH-MILESTONE.md) | Current dependencies and representative-unit exit | Reach completion is not whole-vision completion |
| [Product contract](SOURCE-TO-COURSE.md) | Local-first desktop delivery with a SaaS-quality experience | The experience standard does not authorize hosted accounts, storage, billing, or a new shell |
| [`code_learner` review](https://github.com/onionviolet/code_learner) | A focused browser coding drill can combine a code editor, local Python and JavaScript workers, deterministic tests, declared provided context, retry, and solution reveal. Its local validation passed for 1,579 drills in 40 language/category groups on 2026-09-06 | One initial commit, no objective graph or durable attempt evidence, aggregate browser-local statistics, client-owned scoring and disclosure, incomplete worker regression coverage, and 12 high-severity dependency audit findings |

The 19C seed already includes VPA-03 declarations. The 19D seed already
includes VPA-04 loss reporting. Carry these into their eventual contexts rather
than adding another acceptance checklist. Five restore losses remain reported
by the audits. Naming a loss is not repairing it.

The 2026-09-06 product-experience direction changes the acceptance lens, not
the queue architecture. R1 and R2 repair controls that make the application
feel unfinished. R5 establishes one recognizable navigation frame. R6 proves
that the connected desktop experience supports real learning and recoverable
agent work. Phase 18 retains packaged first-use and external-install evidence.
No SaaS backend packet is added.

STATE lists 19A-03 as latest, but the feature audit found later operations in
code. Before selecting a packet, inspect current summaries, relevant symbols,
and the working diff. Do not rebuild functionality from a stale status line.
The working tree has concurrent code and planning changes. Never reset it or
stage unrelated files.

## D0: Workflow optimization finding

The full GSD pipeline has protected assessment authority, recovery, accepted
revisions, and long-lived product intent. It is not the token-efficient default
for every remaining task. The measured 2026-09-06 structural baseline found 67
GSD skill files with about 7,000 lines, an active `.planning` tree with about
219,000 lines occupying 17 MB, and 638 commits touching `.planning`. STATE
recorded 212 completed plans while real-use evidence still consisted of one
learner sitting. These are measurements of process footprint and product
validation balance, not direct token-usage measurements.

Diego's one-pass Syntax Lab provides the counterexample and the warning. It
produced a focused interface and 1,579 locally validated drills quickly. The
same review found client-owned scoring and reveal, no durable objective-linked
attempt evidence, regex structural grading, incomplete worker regression
coverage, and high-severity dependency findings. Preserve rapid coherent
prototyping, then spend process only on risks that observed evidence exposes.

Apply the proportional workflow in `AGENT-WORKFLOW.md`: direct execution or
`gsd-fast` for trivial reversible work, one agent with an evidence-gated packet
for settled implementation, `gsd-quick --validate` for bounded work needing
durable state and independent gates, and full GSD only for named consequential
decisions. Optional research, pattern mapping, plan checking, broad review, and
subagent fan-out are activated by a concrete ambiguity or risk rather than by
habit. Deterministic tests, one-parser and one-scorer authority, dirty-tree
safety, recovery gates, and the repository's commit rules remain unchanged.

## D1: Default execution shape

Use one agent directly for each ready packet. Keep one writer active. A small
task does not need a supervising large model. Model assignments below are
starting recommendations based on the installed routing skill, not measured
price or performance guarantees. Check availability in the executing client.

| Task shape | Starting model and reasoning | Escalation trigger |
|---|---|---|
| Exact local edit with an observable check | Spark directly if available, otherwise Luna at low | The fix requires unsettled behavior or fails for a nonlocal reason |
| Repetitive wiring, clear tests, short documentation edits | Luna at low | Existing patterns conflict or authority semantics are unclear |
| Symbol-first investigation and audit reconciliation | Terra at medium | Evidence reveals a cross-system design decision |
| Multi-file behavior, interaction decisions, integration diagnosis | Sol at medium | Unresolved architecture, recovery integrity, or disclosure risk |
| Hard cross-system failure or consequential design review | Astra for that bounded question | Return a decision and acceptance criteria, then resume cheaper execution |

Separate Spark allowance, when available, may preserve another allowance.
It does not prove lower total token use. No numeric savings are promised.
Do not run a new usage audit for every packet unless remaining capacity is a
constraint. Use available counters rather than building a tracking feature.

## D2: Dependency-ordered work queue

Later rows remain seeds. Expand only the next ready packet into exact edits.
Each row references original finding IDs to avoid duplicate defect records.

| Packet | Scope and original findings | Execution and owner | Exit evidence |
|---|---|---|---|
| R0: reconcile current work | Locate existing fixes and completed 19A operations before selecting work | Terra, one bounded read pass | Each next action is either already verified, still missing, or awaiting a named check. Link current evidence |
| R1: study visibility | UI F1.1, hidden action groups only | Spark or Luna directly, Study owner | Front, reveal, and learn states show only their valid controls. Hidden groups have zero rendered area and no focusable descendants |
| R2: shared controls | Remaining UI A1.1, table/build selects and walkthrough buttons | Luna directly, presentation owner | Browser measurements meet the project's 44px targets and 16px action text. Existing actions still work |
| R3: complete existing doors | Remaining 19A families, then 19B and 19E under their existing plans | Luna for proven route/CLI patterns. Sol for proposal acceptance, undo, or unfamiliar semantics | Published requests, parity, and required phase gates pass. Proposal acceptance produces one journal entry and undo is verified |
| R4: backend diagnostic | VPA-03, existing 19C scope | Luna for settled configuration/run steps. Sol only for environment or authority ambiguity | Context declares profile revision, endpoint, rights, egress, authority, output paths, validation and fallback. Real input run is retained and judged. Diagnostic output is not accepted course content |
| R5: visible course journey | VPA-01/07, UI A1.2 and A1.3 where an existing obligation fails, IL-20260906-07 | Sol settles a bounded component and interaction contract, then Luna implements clear portions | Shelf-to-course navigation, current area, mobile disclosure, actionable empty states, and runtime-permitted help work as one recognizable shell. No guessed URL bypass or early keyed disclosure |
| R6: one representative unit | VPA-02, feature P-A/P-B and A1 to A3, existing 19D, IL-20260906-07 | Sol coordinates the unit. Smaller model executes only bounded authoring with the relevant skill | Enter through the packaged or canonical browser-served shell. Observe source locators, justified reading, one reviewed generated treatment, meaningful transfer, note capture, actual resume, source lookup or search, sitting, evidence uncertainty, durable agent-job state, interruption recovery, and accepted change with undo |
| R7: recovery closure | VPA-04, feature O9, existing 19A-08 and 17C loss owners | Luna runs a specified restore drill. Sol diagnoses failures. Astra only if a repair changes a durable recovery contract | Classify F-LOSS-1 to F-LOSS-5 against the package. Repair every applicable silent loss through its owner and rerun the affected clean restore step. Attach the manifest and loss report. An explicitly disclosed exclusion may remain only when the binding contract permits that object not to travel |

R4 can begin as soon as its input and authority are available. It need not wait
for R3. With one writer, execute it between code packets rather than launching
another coordinator. Prepare R6 source/objective inputs early. Its walkthrough
requires the relevant R3/R4 doors, and full closure keeps the existing phase
dependencies. R7 runs when packaging is exercised and before recovery claims.
19E remains a deliverable without becoming an extra prerequisite for R6.

Do not expand this whole queue before continuing implementation. The next
ready packet is the bounded part of R5 that applies UI A1.2 to the course shelf
and course frame. It owns a recognizable application shell, visible current
area, mobile navigation disclosure, actionable empty state, and an unbroken
shelf-to-course-to-home return path. Use the existing component direction and
do not expand it into the future comprehensive redesign. Its evidence is
before-and-after browser views and a keyboard walk at 1280, 375, and 320 CSS
pixels, plus the targeted presentation and IA route suites.

After that packet passes, resume R3 with 19A-06. Prepare 19C input and authority
declarations beside implementation only when that does not idle the active
writer. Put the thin R6 walkthrough in use as soon as its required doors exist.
Let observed failures decide which additional planning and review are worth
their cost.

### D2.1: Current priority order

1. **P0 app journey:** bounded R5 course shell and first-use return path.
2. **P1 operating doors:** 19A-06 through 19A-10, with R7 recovery closure
   applied at 19A-08.
3. **P1 live intelligence:** R4 through 19C, then the 19B agent door.
4. **P1 representative use:** thin R6 Math 1400 unit as soon as its required
   doors exist, followed by repair of only its blocking defects.
5. **P2 interop and breadth:** 19E, human legs, Phase 18 cold install, and the
   post-Reach visual and capability work under their existing owners.

Priority describes what receives the active writer next. It does not waive a
dependency or turn P2 into abandoned work.

### D2.2: Audit closure protocol

Every finding in the vision, UI character, feature opportunity, 17C recovery,
17B gate, and Phase 18 gate records must finish in exactly one visible state:

| State | Required record |
|---|---|
| Verified closed | Revision or artifact, exact check, result, and owning evidence file |
| Human owed | Named reviewer, exact walk or decision, and the artifact awaiting review |
| Deferred | Durable owner, dependency or trigger, and the evidence needed when reopened |
| Superseded | Replacement decision, preserved original record, migration effect, and verification route |
| Rejected | Evidence, conflicting rule, retained alternative, and reconsideration condition |

“Addressed later,” a completed milestone label, or a copied checklist is not a
closure state. At each phase handoff, update only findings exercised by that
phase and search the owning audit IDs for any item left without one of these
states. Before Reach closes, produce a compact closure index that links to the
owning evidence rather than duplicating audit prose. Open human and deferred
items may remain, but none may be unowned or described as verified.

For future UI findings, supersession is legitimate when a better fitting
component or interaction replaces the old one. Preserve behavior and durable
state through an explicit migration. Remove obsolete presentation after the
replacement's journey, accessibility, responsive, and recovery gates pass.

R1 and R2 are the cheapest concrete audit fixes. R5 must distinguish navigation
defects from the future comprehensive visual redesign. Reach excludes new
visual-system work. The UI character audit owns that later direction and may
replace the current aesthetic after comparative prototypes and user review.

## D3: Preserve later work without expanding the critical path

| Work retained | Disposition and owner | Revisit trigger |
|---|---|---|
| Comprehensive UI character, reader styling, identity, component system, and default promotion, IL-20260906-08 | Measured Field Guide and Learning Trajectory Deck are selected as user-switchable presentation profiles over one semantic foundation. Color, contrast, and accent remain independent settings. Field Guide emphasizes source-heavy reading and reflection. Trajectory Deck emphasizes movement, practice, evidence, operations, and recovery. The current aesthetic is not a compatibility target | Implement semantic roles, shared tokens and primitives, both recipes, and a recoverable profile setting with preview and visible fallback. Prove one shelf-to-lesson-to-practice slice across profiles, appearance modes, desktop, mobile, keyboard, accessibility, settings migration, and recovery before broader migration |
| New help detours and confusion-practice orchestration, feature F1/F2 | Existing prototype dispositions, note/navigation owners | Existing controls demonstrably fail the real unit's job |
| Time budgeting, confidence calibration, return recap, F5/O7/O11 | Existing registered or prototype routes | Exact resume works and actual history supports a useful comparison |
| Onboarding breadth, multi-course experience, VPA-05 | Phase 18 and registered breadth | R5 and R6 establish the core first-use path, 19D defects are routed, and external install evidence becomes available |
| OCR, annotation expansion, bilingual/audio, sync, VPA-06 and feature register breadth | Retain every existing disposition and owner | A real workflow meets its recorded dependency and rights gates |

This table groups routes, not replacements for their full registers. No idea
is rejected or removed. Current note capture and exact resume obligations stay
in R6 even while richer optional features wait.

### D3.1: Register executable coding practice without changing the critical path

**Disposition:** prototype. Treat executable coding as one possible treatment
for an objective whose verb and transfer demand require writing or changing
code. Do not make it the default treatment for programming material and do not
create a parallel course, scorer, evidence store, or learner shell.

#### CS Dojo interaction concept

Use **CS Dojo** as the working name for the focused course area or activity
surface inspired by Diego's Syntax Lab. Preserve the useful interaction loop:
choose a language and topic, read one concise task, see all provided context,
write code in a real editor, run deterministic checks, receive specific
per-test feedback, retry, request a runtime-permitted reveal, and advance. The
Dojo should inherit the broader future UI system while retaining a denser,
editor-centered workspace appropriate to programming practice.

Make language support adapter-based. Each adapter declares language and runtime
version, accepted source shape, provided files or values, compile or execution
command, result schema, resource limits, offline assets, dependency policy,
and unavailable fallback. Python and JavaScript are prototype candidates
because the reviewed implementation demonstrates them. Later adapters may
support TypeScript, Java, C, C++, Rust, Go, SQL, shell, HTML/CSS, or another
course-required language only when its objective, sandbox, distribution cost,
and maintenance owner justify it. Adding a language must not require a second
scorer or a second evidence model.

The reviewed `code_learner` repository supplies implementation evidence for a
narrow interaction, not authority for an itembank format change. Retain these
patterns for a bounded prototype:

- A focused prompt, accessible code editor, declared language and provided
  context, deterministic test cases, timeout, retry, and runtime-authorized
  solution reveal.
- An authoring invariant that every identifier a hidden test requires the
  learner to create is named in the public prompt. Test setup visible to or
  required by the learner is declared as provided context.
- Replaceable local execution adapters, such as an isolated browser worker or
  a separately reviewed local runner. Adapter results remain proposals to the
  existing runtime, which settles scoring, disclosure, session state, and
  evidence.

#### CS coursework activity matrix

Treat the current Syntax Lab interaction as a concise code-construction drill.
It resembles the smallest part of a LeetCode-style workflow because the learner
submits code against tests, but it is organized around language syntax and API
categories rather than algorithmic interview problems. Neither model is a
course by itself. The CS Dojo must support the following objective-linked
families without forcing them into one response or scoring policy:

| Family | Representative activities | Verification and evidence boundary |
|---|---|---|
| Read and predict | choose an implementation, predict output, inspect a diff, classify complexity | Existing item types or a low-stakes prediction followed by observation; successful selection does not prove code construction |
| Trace and explain | trace variables, stack frames, heap references, control flow, or algorithm state; explain observed behavior | Semantic visual, table, check, or pending prose response; execution output alone cannot settle explanation quality |
| Construct and modify | fill an expression, write a function, complete or refactor code, adapt it to a changed requirement | Deterministic examples, hidden cases, properties, compilation, or type checks settled through runtime authority |
| Debug and test | reproduce a failure, locate a defect, repair code, write a failing test, strengthen a test suite | Record diagnosis, tests added, behavioral repair, and attempts separately; regex structure checks are advisory unless the accepted contract makes them binding |
| Build and use tools | work across files, a terminal, Git diff, database, DOM, API stub, build system, or bounded project | Learner-owned artifact with checkpoints and explicit review state; tests may settle behavior while design, maintainability, and reasoning remain pending review |

Do not commit a universal `code` item merely because the editor interaction is
useful. The activity contract must first decide when typed code is a scored
assessment response, an instructional lesson capability, a persistent learner
artifact, or several distinct forms sharing an editor and execution adapter.
The course director selects among these families from the objective verb,
prerequisites, cognitive demand, and desired transfer rather than assigning a
code editor to every CS objective.

#### Gaps inherited from the comparison

The prototype must close or explicitly defer the gaps that prevent
`code_learner` from standing as a CS coursework system: stable objective and
prerequisite links; prediction, tracing, debugging, test-writing, and project
activities; runtime-owned scoring, reveal, and durable evidence; hostile-code,
timeout, dependency, and worker-recovery assurance; and multi-file, tool,
accessibility, offline, and non-executable fallback behavior. Its fast,
coherent editor loop is evidence for the interaction, not evidence that these
course, authority, or safety gaps are solved.

**Owner and dependencies:** the future lesson-capability or activity-format
owner proposes the treatment. The runtime owner settles assessment semantics.
The security owner reviews the execution boundary. Prototype only after the
objective/activity contract can distinguish instructional execution from a
scored assessment response and after source, rights, egress, offline, and
recovery declarations exist for the operation.

**Prototype gate:** use synthetic code only. Demonstrate one Python or
JavaScript objective from public prompt through execution, per-test feedback,
retry, runtime-controlled reveal, objective-linked attempt evidence, reload,
and offline use. In the same bounded course unit, demonstrate a
predict-run-explain activity, a debugging or learner-authored-test activity,
and a small multi-file lab or learner artifact whose behavioral checks and
pending review state remain distinct. Verify CPU/time termination, worker
replacement after timeout, no keyed-content leak, no undeclared identifiers or
fixtures, keyboard and screen-reader operation, and a useful static fallback.
Add hostile-code, Python, JavaScript, DOM where applicable, and disclosure
regression tests before any accepted format or capability change. A prototype
that proves only isolated function submissions may register a narrow drill
mode, but it does not satisfy the CS coursework extension gate.

**Failure and degraded behavior:** unavailable execution is an explicit
`unavailable` activity state with a non-executable fallback. A timeout or
runner crash records the attempt outcome without implying incorrectness or
mastery. Dependency or sandbox findings block publication of the executable
capability, not access to the underlying lesson. Regex-only structural checks
cannot settle semantic correctness unless the accepted scoring contract names
that narrow construct.

**Migration, documentation, and maintenance:** no current bank or lesson is
migrated automatically. Any durable schema addition requires the full format,
authority, threat, accessibility, and recovery gates plus updated spec, lint,
JSON schema, roundtrip tests, export behavior, and clean-machine restore. Pin
and audit the local execution dependencies. The capability owner maintains
language runtimes, resource limits, sandbox tests, and version compatibility.
Revisit after R6 proves the representative course journey or when a real
objective cannot be taught or assessed adequately through existing static
treatments. See IL-20260906-09 for the durable CS Dojo disposition.

## D4: Packet and verification rules

Each execution packet fits in a short handoff: original finding ID, observable
result, exact files/symbols, current base revision and relevant dirty-file
fingerprints, settled constraints, smallest verification command, and stop
condition. Read cited sections only. Do not copy full audits or large modules.

Use the existing failing test or browser observation before writing a new
test. Static markup cannot prove computed visibility, focusability, or control
size. Use browser checks for R1/R2. Use the UI audit's representative viewport,
mode and accessibility matrix when shared interactions or templates change.

Run targeted tests during edits. Run required preflight before handing back an
implementation packet and reuse its suite results for that same revision.
Use quick preflight for planning-only changes. Recheck after relevant changes
or failures, not to obtain a second identical transcript. Never combine two
plans merely to avoid their required gates.

Escalate after two attempts at the same unexplained failure, or immediately
when authority or durable format choices appear. This is an escalation budget,
not permission to ship failure. Send only the failure, relevant diff, named
symbols and smallest reproducer. Do not restart the audit on a stronger model.

Add an independent reviewer only for a concrete risk such as keyed disclosure,
accepted writes, rights, or recovery integrity. A review returns findings and
evidence, not another implementation. Do not automatically chain planner,
researcher, implementer and verifier for every patch. Human visual,
screen-reader and instructional-quality legs remain owed until performed.
The existing freeze waiver permits progress without inventing their approval.

Each packet returns changed paths, checks and results, unresolved defects,
and one next action. Evidence stays in its owning phase. Update STATE's next
action by reference when execution advances, without duplicating this queue.
Follow current user commit authorization and stage only owned files if asked.

## Planning-pass record

Read scope: the three linked audits, workflow and product contract, Reach,
STATE's current-position section, 19C/19D seeds, selected vision context, and
the installed efficient-routing skill. This pass did not inspect application
implementations or rerun audit behavior. It does not claim an exhaustive
historical audit or current runtime verification.

Write scope: this new plan only. No learner data, application settings, source
files or external services are mutated. The durable object is this reviewable
planning file. Prior reports and phase contexts retain authority. Recovery is
removal of this added file only. Existing concurrent edits are preserved.

Next action at the time of planning was R0, then R1 if the
computed-visibility defect remained. No subagents were needed to consolidate
the existing reports. Validation results are reported with the handoff rather
than copied from prior audits.

## Execution record, 2026-09-06

R0 confirmed that 19A-01 through 19A-04 were already verified. It also found
that 19A-05 exists in code but still lacks its route and CLI acceptance-and-undo
gate and current STATE entry. R1 repaired Study action-group visibility and
duplicate navigation bindings. Browser checks confirmed that front, revealed
Flash, and revealed Learn expose only their valid controls, with hidden groups
absent from the accessibility tree. R2 gave table and build selects 44px
minimum targets and 16px text, and applied the shared control treatment to the
Start, Skip, and Replay walkthrough actions. Chromium measurements passed at
1280, 375, and 320 CSS pixels without page overflow.

The targeted Study, presentation, IA route, serve, and stylesheet suites pass.
The integrated full preflight remains red for three independently owned
conditions: the pre-existing skill-mirror difference at
`.agents/skills/author-bank/_attempts`, the daemon concurrent-request timeout,
and the unclassified 19A-05 course commands reported by
`tests/surface_coverage_check.py`. The clean-tree preflight gate also reports
the already-present planning edits and this packet's uncommitted files, as
expected in the shared dirty worktree. R3 should begin with the 19A-05
route-and-CLI acceptance, undo, coverage, and STATE reconciliation packet.

R3 completed the bounded 19A-05 packet. All seven director operations are
exercised through both route and CLI against temporary course roots. The gate
found and repaired one recovery defect: acceptance's sidecar mutation and its
operation metadata were separate journal records, so reverse-operation could
not reach the mutation's before-image. The accepted CAS record now carries the
operation identity, proposal, local egress disclosure, and restore record in
one applied acceptance entry. No separate accept phase is appended. The route
and CLI checks each observe exactly one acceptance entry, reverse exactly one
entry through `journal.undo`, recover byte-for-byte original sidecar content,
and parse the restored course successfully. Surface coverage now classifies
all seven commands and seven routes, reaching 48 of 82 meaningful cells.
Full preflight remains red only for the pre-existing skill-mirror difference
at `.agents/skills/author-bank/_attempts`, the intermittent daemon concurrent
request timeout (also reported by the nested model-phase authority regression),
and the expected clean-tree failure from the shared uncommitted worktree. The
JavaScript gate and every other completed preflight gate passed.
