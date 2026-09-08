---
phase: 19B-agent-operation-door
plan: 01
type: execute
wave: 1
depends_on: ["19A-09", "17A-07"]
files_modified:
  - surfaces/agent_operation.py
  - surfaces/course_ops.py
  - surfaces/daemon.py
  - surfaces/home.py
  - surfaces/visual_fixture.py
  - schemas/course_operation.schema.json
  - itembank.py
  - tests/agent_operation_roundtrip.py
  - tests/course_ops_roundtrip.py
  - tests/daemon_roundtrip.py
  - tests/home_roundtrip.py
autonomous: true
requirements: [AGENT-01, AGENT-02, RIGHTS-02, RELIABILITY-01, RELIABILITY-02, RELIABILITY-03, APP-01, APP-02, A11Y-01]
must_haves:
  truths:
    - "A learner enters the visible Agent tab, starts a runnable skill, reviews the stored target, citations, validation, and diff, then accepts or rejects without posting draft bytes back to the server."
    - "An agent client performs the same lifecycle through the token-gated route and its CLI twin using one published request contract and the same shared operation function."
    - "Each accepted proposal creates exactly one applied journal entry, repeated settlement creates none, and each accepted change has a visible undo that restores byte-identical prior content and records the durable undone disposition."
    - "Rejected and conflicted proposals change no accepted bytes, and proposed, accepted, rejected, conflicted, and undone records remain inspectable after reload and process restart."
    - "Pending, needs-input, unavailable, conflicted, accepted, rejected, undone, empty, and report_only states provide distinct text and legal next actions in the server-rendered Agent flow."
    - "No Agent surface settles a mark, chooses correctness, releases a key, accepts caller-supplied authority, or adds another journal or file-operation type."
  artifacts:
    - path: "surfaces/agent_operation.py"
      provides: "Durable proposal lifecycle and the sole shared start, status, accept, reject, and undo implementation"
    - path: "schemas/course_operation.schema.json"
      provides: "Closed request definitions for the agent-operation command family"
      contains: "agent_operation"
    - path: "surfaces/daemon.py"
      provides: "Token-gated route, CLI mapping, and SURFACE_PARITY reservation"
    - path: "surfaces/visual_fixture.py"
      provides: "Server-rendered Agent-tab workflow and review history"
    - path: "tests/agent_operation_roundtrip.py"
      provides: "Persistence, settlement, conflict, rejection, and byte-exact undo proof"
  key_links:
    - from: "surfaces/visual_fixture.py"
      to: "surfaces/course_ops.py"
      via: "normal server POST forms identify an opaque proposal and invoke the shared command family"
      pattern: "agent[_-]operation"
    - from: "surfaces/course_ops.py"
      to: "surfaces/agent_operation.py"
      via: "one dispatcher for browser, API, and CLI callers"
      pattern: "agent_operation"
    - from: "surfaces/agent_operation.py"
      to: "journal.commit_operation"
      via: "accepted stored draft with expected-base fingerprint"
      pattern: "journal\\.commit_operation"
    - from: "surfaces/agent_operation.py"
      to: "journal.undo"
      via: "stored applied journal entry identity"
      pattern: "journal\\.undo"
---

<objective>
Open the existing agent-operation state machine through the canonical Agent tab,
one token-gated route, and one CLI twin. Preserve the stored proposal as the
review boundary so acceptance is one journaled mutation and undo is visible and
verifiable.

Purpose: Make the product's existing agent capability reachable without moving
assessment authority or creating another proposal, mutation, or recovery path.
Output: A durable proposal lifecycle, shared route and CLI contract, complete
server-rendered Agent flow, and a two-surface acceptance and undo transcript.
</objective>

<execution_context>
@.codex/get-shit-done/workflows/execute-plan.md
@.codex/get-shit-done/templates/summary.md
</execution_context>

<context>
@AGENTS.md
@.planning/phases/19B-agent-operation-door/19B-CONTEXT.md
@.planning/phases/19B-agent-operation-door/19B-PATTERNS.md
@.planning/phases/19B-agent-operation-door/19B-UI-SPEC.md
@.planning/phases/19B-agent-operation-door/19B-SEED.md
@.planning/REACH-MILESTONE.md
@.planning/phases/17A-visual-system-component-foundation/17A-07-SUMMARY.md

<interfaces>
Use the existing contracts directly:

- `surfaces.agent_operation.start(skill, settings, base)` creates the bounded proposal through `model_adapter.invoke`.
- `surfaces.agent_operation.accept(state, settings)` is the current sole settlement function and calls `journal.commit_operation`.
- `surfaces.course_ops.run(root, operation, request, actor_kind="human", actor_name="", base=None)` validates a published request before dispatch.
- `journal.undo(base, entry_id, actor_kind, actor_name)` is the only byte-restoration path.
- `surfaces.home.AGENT_AREA_HREF` is the canonical Agent-tab link and `pending_proposals(root)` is the shelf attention seam.
- `surfaces.daemon.API_ROUTES`, `ROUTE_CLI`, and `SURFACE_PARITY` must remain one-to-one for the new route.
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Make proposals durable and settlement idempotent</name>
  <files>surfaces/agent_operation.py, tests/agent_operation_roundtrip.py</files>
  <behavior>
    - A successful run stores a course-local opaque proposal record with target, kind, draft, citations, provider, validation, expected fingerprint, operation and interaction ids, timestamps, and proposed disposition.
    - Fresh module and process loads recover proposed, accepted, rejected, conflicted, and undone records. Malformed or future-version records return a typed actionable unavailable state and never crash the course surface.
    - Accept and reject receive only proposal identity. Accept uses stored bytes and produces exactly one applied `journal.commit_operation` entry. Reject records review facts and changes no accepted bytes.
    - Stale expected fingerprints persist a conflicted disposition and overwrite nothing. Repeated accept, reject, and undo return the durable settled result without another mutation.
    - Undo uses the stored applied entry with `journal.undo`, verifies byte equality against the before-image, then records the undone disposition and undo entry.
  </behavior>
  <action>
Extend the existing state machine in place per D-01 through D-07. Keep proposal
records below the resolved course root in a versioned sidecar namespace, mint
opaque ids, and use temporary-file plus atomic-replace writes guarded by the
record's expected fingerprint. Retain all settled records and their provenance,
reviewer, validation, accepted journal link, prior revision, and undo facts per
D-02. Do not implement compaction per D-03. Do not add to
`journal.OPERATION_TYPES`, duplicate `commit_operation`, accept client-posted
drafts, retry conflicts, or restore bytes outside `journal.undo`. Preserve the
runtime's exclusive scoring and keyed-disclosure authority.
  </action>
  <verify>
    <automated>python3 tests/agent_operation_roundtrip.py</automated>
  </verify>
  <done>Durable records survive restart, every terminal disposition remains inspectable, accept writes once, reject and conflict write zero accepted bytes, and undo proves exact restoration through the journal.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Publish one shared route and CLI twin</name>
  <files>surfaces/course_ops.py, surfaces/daemon.py, schemas/course_operation.schema.json, itembank.py, tests/course_ops_roundtrip.py, tests/daemon_roundtrip.py</files>
  <behavior>
    - The closed agent-operation request family supports start, status, accept, reject, and undo with course id plus only the identifiers and user decisions each action needs.
    - Browser, token-gated API, and CLI callers reach one `course_ops.run` dispatcher and receive the same durable response fields and typed errors.
    - The route rejects draft bytes, filesystem paths, actor kind, scoring, marking, key, rights, and authority claims before proposal content is read.
    - Route, CLI, schema, and reserved MCP name stay aligned in `API_ROUTES`, `ROUTE_CLI`, and `SURFACE_PARITY`.
  </behavior>
  <action>
Add one canonical `/api/course/agent-operation` route and one `itembank course
agent-operation` CLI twin per D-04. Use an `action` discriminator inside this
single published command family while preserving course operation request
validation and token plus loopback write gates. Dispatch every action to the
Task 1 functions. The surface fixes actor kind and resolves course and proposal
identities below approved roots. Return proposal disposition, validation,
journal linkage, fingerprints, verification, and exact next action without
drafting a second transport-specific result. Reserve one MCP tool name now, but
do not build MCP transport in this phase. Preserve all unrelated working-tree
hunks in these shared files.
  </action>
  <verify>
    <automated>python3 tests/course_ops_roundtrip.py &amp;&amp; python3 tests/daemon_roundtrip.py</automated>
  </verify>
  <done>The published schema, route, CLI twin, and parity row describe one command family, both clients return equivalent lifecycle results, and forbidden authority-shaped input fails before dispatch.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: Complete the visible Agent-tab flow and run the Reach gate</name>
  <files>surfaces/home.py, surfaces/visual_fixture.py, tests/home_roundtrip.py, tests/agent_operation_roundtrip.py, tests/daemon_roundtrip.py</files>
  <behavior>
    - From the course shelf, the Agent link opens the live course Agent tab without a guessed URL. A runnable skill starts through a normal POST and returns focus to durable status.
    - Review shows target, citations, validation, egress disclosure, expected fingerprint, bounded diff, and separate Accept and Reject controls before settlement.
    - Accepted history exposes Undo beside its journal evidence. Rejected, conflicted, and undone records remain readable after reload.
    - Empty, needs-input, unavailable adapter families, report_only, conflict, accepted, rejected, and undone states use the exact UI contract copy and legal next actions with JavaScript disabled.
    - Controls remain keyboard reachable, named by action and proposal, at least 44px, non-color-dependent, reflow without page-level horizontal scroll at 375px and 400% zoom, and reduced-motion safe.
  </behavior>
  <action>
Replace `AGENT_AREA_HREF`'s screenshot-only destination and the descriptive
skill controls with the live server-rendered flow per D-08 through D-10. Read
durable proposal history tolerantly for the shelf attention count and Agent
view. Use semantic headings, one polite status region, native forms and
disclosures, confirmation UI, bounded diff paging, visible conflict recovery,
and the exact CLI twin for each next legal action. Keep the framed console as
the separate open-ended path. Do not hide the proposal behind JavaScript or
optimistically invent status.

Run the Reach acceptance transcript twice against one synthetic temporary
course. First, enter from the shelf and use the Agent-tab forms to start,
review, accept, assert exactly one applied journal entry, undo, and verify the
prior bytes. Second, use the token-gated API as the agent client to perform the
same sequence and assertions, then invoke the CLI twin for status and verify
the same ids and disposition. Also prove reject changes no accepted bytes,
conflict overwrites nothing, and no response exposes a key or settles a mark.
Record human screen-reader and visual acceptance as owed, never passed by the
agent.
  </action>
  <verify>
    <automated>python3 tests/home_roundtrip.py &amp;&amp; python3 tests/agent_operation_roundtrip.py &amp;&amp; python3 tests/daemon_roundtrip.py &amp;&amp; python3 tests/visual_system_roundtrip.py &amp;&amp; python3 scripts/preflight.py --quick</automated>
    <human-check>Owed after execution: one representative screen-reader and visual review of the Agent flow. Do not block deterministic execution or self-certify this leg.</human-check>
  </verify>
  <done>The shelf-to-Agent UI journey and agent-client route each accept one proposal as exactly one applied journal entry, visibly undo it, and verify restoration. All required states remain usable as static accessible HTML.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Browser or agent client to daemon | Untrusted action, ids, and review decisions cross a token-gated loopback route. |
| Model result to proposal store | Untrusted generated draft and citations become reviewable data, never accepted truth. |
| Proposal store to journal | Only a reviewed stored proposal may cross into the canonical atomic mutation authority. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-19B-01 | Spoofing | agent-operation route | mitigate | Token and loopback gates plus surface-owned actor kind. |
| T-19B-02 | Tampering | proposal settlement | mitigate | Opaque id lookup, closed schema, stored draft, expected-base comparison, atomic record update. |
| T-19B-03 | Repudiation | accept, reject, undo | mitigate | Durable reviewer, time, proposal, operation, journal, and reversal links retained after settlement. |
| T-19B-04 | Information disclosure | route and Agent tab | mitigate | Reject authority-shaped fields and keep keys, scoring, and private source spans outside responses. |
| T-19B-05 | Denial of service | model and record reads | mitigate | Typed unavailable states, bounded diffs, tolerant reads, and core learning remains operational. |
| T-19B-06 | Elevation of privilege | model-authored proposal | mitigate | Human review controls settlement and runtime retains all assessment authority. |
| T-19B-SC | Tampering | package installs | accept | No package installation occurs in this plan. |
</threat_model>

<source_audit>
GOAL is covered by Tasks 1 through 3. CONTEXT D-01 through D-07 are covered by
Task 1, D-04 is also covered by Task 2, and D-08 through D-10 are covered by
Task 3. REQ AGENT-01, AGENT-02, RIGHTS-02, RELIABILITY-01 through 03, APP-01,
APP-02, and A11Y-01 are addressed by the plan's declared gates. RESEARCH has no
separate artifact; 19B-PATTERNS supplies the implementation constraints covered
by all three tasks. Deferred proposal compaction, a generalized extension
loader, and external package installation do not appear in the tasks.
</source_audit>

<verification>
The focused lifecycle, course operation, daemon, home, and visual suites pass.
The quick preflight passes. The recorded acceptance transcript names both
surfaces, the two accepted proposal ids, exactly one applied journal entry per
acceptance, both undo entries, byte-equivalence results, rejected and conflict
no-write results, and the still-owed human review leg.
</verification>

<success_criteria>
Phase 19B is executed when the visible Agent-tab flow and agent-client API flow
each accept one stored proposal through the shared operation function, create
exactly one applied journal entry, expose and perform undo, and re-verify exact
prior bytes. Route and CLI parity, durable review history, accessible static
states, and assessment authority boundaries are proven by the focused gates.
</success_criteria>

<output>
Create `.planning/phases/19B-agent-operation-door/19B-01-SUMMARY.md` when done.
Commit exactly once after all automated verification passes, staging only this
plan's owned files and preserving unrelated worktree edits.
</output>
