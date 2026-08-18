---
phase: 17C-maintenance-restore-audit
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - .planning/phases/17C-maintenance-restore-audit/17C-AUDIT.md
autonomous: false
requirements: ["ROADMAP governance clause: Post-Phase-17 maintenance and restore audit", "17B gate G10"]
must_haves:
  truths:
    - "The audit runs only after Phase 17B's exit record exists with every gate passed or defect-routed."
    - "Every supported canonical object either restores on a clean machine offline or is named in the loss report; nothing is silent."
    - "Every accepted item names a maintenance owner, or appears on the audit's finding list."
  artifacts:
    - "17C-AUDIT.md records the drill sweep results, the loss-report completeness check, the owner sweep, and the named recurring audit triggers."
  key_links:
    - "The drill script is 17B's (17B-CONTEXT D-07); 17C reruns it as a sweep and never writes a second drill implementation."
---

<objective>
Run the post-Phase-17 maintenance and restore audit so it stops being ownerless.
Implements the ROADMAP governance clause "Post-Phase-17 maintenance and restore
audit" and the Phase 17C block (registered 2026-08-17), reusing the scripted
restore drill 17B-CONTEXT decision D-07 requires 17B to leave behind. 17B proved
the tracer's unit restores; this audit sweeps all supported canonical objects
and all accepted items. Weibao holds acceptance authority on the report.
</objective>

<context>
@.planning/ROADMAP.md (sections "Phase 17C: Maintenance and Restore Audit" and "Post-Phase-17 maintenance and restore audit")
@.planning/phases/17B-production-vertical-tracer/17B-CONTEXT.md (decision D-07)
@.claude/CLAUDE.md (section "Durable objects and derived state", the canonical object list)
@.planning/REQUIREMENTS.md (Owner: fields)
</context>

<tasks>
<task type="auto">
  <name>Task 1: Precondition halt on the 17B exit record</name>
  <files>.planning/phases/17C-maintenance-restore-audit/17C-AUDIT.md</files>
  <read_first>.planning/phases/17B-production-vertical-tracer/17B-GATES.md (whole file, if present); 17B-04-SUMMARY.md for the drill script path</read_first>
  <action>1. Check that `.planning/phases/17B-production-vertical-tracer/17B-GATES.md` exists and that every gate row reads passed or defect-routed (a defect row must carry a named defect and a named owner, the D-06 shape). 2. If the file is missing, or any gate row is neither passed nor defect-routed, STOP: write nothing except a one-paragraph 17C-AUDIT.md stub containing exactly "HALTED: Phase 17B exit record incomplete; 17C cannot audit an unfinished milestone. Rerun after 17B closes." and end the plan. 3. Otherwise record in a new 17C-AUDIT.md header: the 17B commit audited, the drill script path as named by 17B's exit record or 17B-04-SUMMARY.md (D-07 says the drill is scripted so 17C can rerun it; if no script path is recorded, that is itself finding F0 and the drill portion of this audit is blocked, recorded, and the plan continues with Tasks 3 and 4 only).</action>
  <verify>17C-AUDIT.md exists and either carries the HALTED sentence or names the audited commit and the drill script path (or finding F0).</verify>
</task>
<task type="auto">
  <name>Task 2: Restore drill sweep over all supported canonical objects</name>
  <files>.planning/phases/17C-maintenance-restore-audit/17C-AUDIT.md</files>
  <read_first>The 17B drill script recorded in Task 1; 17B-CONTEXT.md D-07 for its clean-machine mechanics</read_first>
  <action>1. Rerun the 17B drill exactly as D-07 defines it (fresh clone at the audited commit into a temp directory, fresh empty data directory, network unavailable to the process under test), invoking the script recorded in Task 1 verbatim and capturing its exit code and full output into 17C-AUDIT.md. 2. Extend the run to a sweep: for each canonical object class in the .claude/CLAUDE.md durable-object list (course, scope or framework version, concept, objective, source, source binding, artifact, lesson, bank or assessment form, activity, learner note, learner artifact, evidence event, strategy, agent operation, rights grant, accepted revision) plus the operation journal (this plan's own addition to that list, since the journal is restore-relevant state CLAUDE.md tracks under the mutation rules rather than the object list), record one row: restored by bytes, restored by pointer, or NOT RESTORED. 3. Assert loss-report completeness: every row marked NOT RESTORED must appear by name in the drill's loss report; a capability restored by neither bytes nor pointer and absent from the loss report is a failing finding (a silent loss), recorded as F-LOSS-n. 4. No writes outside the temp directory and 17C-AUDIT.md; the audit never edits runtime code, fixtures, or the drill script.</action>
  <verify>17C-AUDIT.md carries one row per canonical object class, the drill exit code, and zero silent losses (every NOT RESTORED row cross-referenced to a loss-report line or an F-LOSS finding).</verify>
</task>
<task type="auto">
  <name>Task 3: Maintenance-owner sweep and the recurring triggers</name>
  <files>.planning/phases/17C-maintenance-restore-audit/17C-AUDIT.md</files>
  <read_first>.planning/REQUIREMENTS.md (grep target below); accepted-revision records under .planning/</read_first>
  <action>1. Run verbatim: `grep -n "Owner:" .planning/REQUIREMENTS.md` (expected: one Owner: line per accepted requirement block; 48 lines at planning time, count may have grown). 2. Cross the grep against the requirement blocks: any accepted requirement or accepted-revision record without a named Owner: goes on the audit's finding list as F-OWN-n; assigning owners is Weibao's call at Task 4, never this audit's. 3. Write the recurring-triggers section: the audit reruns after any 14B change (course and file semantics), any 16C change (agent job protocol), and any 17B change (tracer, restore drill, export packaging), naming for each the file globs whose modification fires the trigger. 4. Close 17C-AUDIT.md with the summary table: drill result, loss-report completeness verdict, owner-sweep count, findings list, and next safe action for each finding. No em dashes anywhere in the report.</action>
  <verify>`grep -c "Owner:" .planning/REQUIREMENTS.md` output matches the count the report states; 17C-AUDIT.md names all three recurring triggers and every finding carries a next safe action.</verify>
</task>
<task type="checkpoint:human-verify">
  <name>Task 4: Weibao accepts the audit report</name>
  <files>.planning/phases/17C-maintenance-restore-audit/17C-AUDIT.md</files>
  <action>Present 17C-AUDIT.md to Weibao (owner assignment per ROADMAP: a Claude-class session runs the audit, Weibao holds acceptance). Ask: accept the report as written, accept with owner assignments for the F-OWN findings, or reject with reasons. Record the decision, date, and any assigned owners in a closing "Acceptance" section. An unanswered checkpoint stops here; no silent default.</action>
  <verify>17C-AUDIT.md ends with an Acceptance section carrying Weibao's recorded decision and date.</verify>
</task>
</tasks>

<out_of_scope>Fixing any finding (findings are routed, not repaired here); writing a second restore-drill implementation; editing runtime code, fixtures, schemas, scripts/preflight.py, tests/preflight_roundtrip.py, AGENTS.md, or .gitattributes; assigning owners without Weibao; auditing unaccepted draft items.</out_of_scope>
<summary_obligations>Record in 17C-01-SUMMARY.md: the halt-or-run outcome of Task 1, the drill command and exit code, the per-object restore table verdict, the owner-sweep counts, every finding id, Weibao's acceptance decision, and which truths were verified by which command.</summary_obligations>
