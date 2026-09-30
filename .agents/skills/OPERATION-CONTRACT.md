# Shared operation contract for itembank agent skills

**Provenance:** created 2026-08-14 (reframe slice 4b). This file condenses the
agents-and-skills contract in `.planning/research/phase-16/14-synthesis.md`
section 10, with the authority vocabulary of sections 2, 3, and 6, so that
every skill can point at one copy instead of restating it. The binding product
contract is `.planning/SOURCE-TO-COURSE.md`; the cross-agent procedure is
`.planning/AGENT-WORKFLOW.md`. If this file and those disagree, those win.

This contract applies to every agent client: Claude Code/Cowork, Codex, local
backends, and any compatible agent. The backend changes capability, latency,
cost, and privacy disclosure. It never changes the artifact or authority
contract.

Resolve sibling reference paths from the skill directory; repository paths and CLI commands use the checkout root. Use only source content permitted by the current course policy, not a cached course example in this skill library.

## The one operation protocol

Every consequential operation follows the same sequence:

1. **Declare intent.** State what the operation will produce and why.
2. **Declare authority.** Name the approved read roots, write roots, rights
   basis, permitted network egress, and execute authority for this operation.
   Discovery never grants writing, transformation, execution, egress, or
   export.
3. **Inventory before creating.** Search the approved roots for existing
   sources, artifacts, and accepted revisions. Reconcile duplicates, moves,
   and conflicts. Never identify or merge artifacts from filenames alone.
4. **Plan treatment.** Decide the best treatment per objective before
   generating anything. Direct source reading is a first-class outcome, not a
   failure to generate.
5. **Checkpoint.** Record enough durable state that a different client, or a
   human, can resume the operation without chat history.
6. **Draft the smallest missing artifact.** One bounded objective or section
   at a time. Reuse or link an adequate existing artifact instead of
   recreating it.
7. **Cite and label synthesis.** Every source-derived claim keeps a stable
   locator. Generated synthesis is labeled as such and never presented as a
   source passage.
8. **Validate deterministically.** Run the shipped lint and audit contracts.
   A draft that has not passed them is not done.
9. **Preview accessibly, plain and rich.** Show the durable plain-file form
   and the rendered learner-facing form. An agent never self-certifies
   accessibility.
10. **Present a bounded diff.** The reviewer sees exactly what would change,
    and nothing changes outside that diff.
11. **Pass configured review.** Recommend-only, draft-and-review, or approved
    bounded writes: the granted autonomy level decides who accepts.
12. **Accept atomically.** A committed write leaves the old valid state or
    the new valid state, never a mixed state.
13. **Update staleness; report undo and uncertainty.** Mark derived and
    dependent material stale, state the exact reversal step, and report what
    remains uncertain, including denominators and missing signals.

Course operations with exams, graded work, competency checks, or completion
thresholds also use `ASSESSMENT-INTAKE.md`. Assessment policy is source-bound
authority, not an authoring convenience. Official grades, runtime scores,
advisory marks, mastery inferences, and course completion remain separate.

An agent may recommend, draft-and-review, or perform approved bounded writes.
It cannot self-expand scope, self-certify accessibility, silently accept its
own uncertain source claim, transfer evidence between objectives, or cross the
runtime's keyed-disclosure boundary.

## Authority vocabulary

- The **learner** owns goals, private notes, scratch work, strategy choice,
  and evidence export.
- A **course builder** defines scope, treatments, and paths within source and
  rights limits.
- A **reviewer** accepts or rejects revisions at the configured consequence
  level.
- An **agent client** discovers, aligns, drafts, validates, and explains
  within an operation manifest. It never owns accepted truth or assessment
  authority.
- The **deterministic runtime** is the sole authority for assessment session
  state, keyed disclosure, scoring, and attempt evidence. Prose stays pending
  until approved marking.

Accepted files (courses, lessons, banks, notes, evidence) are canonical.
Indexes, HTML, caches, rankings, and progress views are derived and
disposable. Accepted content, workflow state, epistemic confidence, validation
state, rights state, and availability are separate axes; never collapse them.
Rights are operation-specific (read, quote, transform, remote-process,
package, export, share) and unknown rights stay restrictive. Link, import,
copy, move, edit-in-place, supersede, migrate, and synchronize are distinct
operations, never synonyms. Same ID with divergent bytes is a conflict, never
a silent overwrite. Similar names never justify identity.

## Current surfaces and capability checks

Check `python itembank.py --help` and the relevant subcommand's `--help` before composing an operation. The table names command families, not complete invocations. CLI presence proves a route exists, not that its dependencies, configured agent skill, installed package or human acceptance are ready.

| Operation | Current surface |
|---|---|
| Format and agent boundaries | `spec`, `schema`, `usage`, `config` |
| Bank inventory and validation | `stats`, `coverage`, `lint`, `audit source`, `audit coverage` |
| Source extraction and registration | `source import --preview`, accepted `source import`, `course register-source`, `course add-source` |
| Course graph and bindings | `course create`, `course show`, `course structure`, `course add-objective`, `course add-edge`, `bind list`, `bind source`, `bind treatment`, `bind rights` |
| Policy and operation record | `course autonomy`, `course begin-operation`, `course replay` |
| Reviewed agent proposals | `course agent-operation` start/status/preview/revise/accept/reject/undo, for configured supported skill IDs |
| Bounded bank proposals | `audit material`, `audit author`, `audit undo`, `seed` |
| IDs and fingerprints | `id-assign BANK`; not a general acceptance or undo mechanism |
| Plain and rich inspection | Plain authored Markdown, `lesson`, `study`, `build`, `serve`, daemon views |
| Assessment and evidence | `start`, `next`, `submit`, `hint`, `teach`, `report`, `evidence`, `trends`, `marks`, `mark`, `retract`, `render` |
| Dependencies and recovery | `course audit`, `course staleness`, `course reverse-operation`, proposal `undo` |
| Course packages | `course export-package`, `course verify-package`, `course restore-package`, `course package-losses` |
| Repository privacy gate | `guard .` |

## Limits and partial integrations

- Multi-root discovery still needs an explicit approved-root inventory; graph and binding commands do not authorize a wider scan.
- The three `Stub:` skills describe unavailable guided automation, with bounded manual workflows against existing primitives. Their UI availability must remain honest.
- `upgrade_audit` has its own source, rights and media availability checks. General course records do not automatically populate those legacy audit rows.
- Use the source's real grants, not agent-proposed permissions. Never impersonate a human actor or add `--confirm` to bypass configured review.
- Recovery surfaces are distinct. `audit undo` reverses its own bank write; proposal undo and course reversal operate on their recorded objects. Verify before-images, newly created files, sidecars, stale-base refusal and package losses before promising exact recovery. Command presence is not proof of lossless undo.
- These are course-artifact controls. Ordinary repository instruction or code edits follow host Git and review rules; they do not require a fabricated course operation record.

## Hard limits in every skill

- Never commit a real bank or learner data to this repository; `fixtures/` is
  synthetic; `guard` enforces this in CI.
- Never auto-grade prose; `short` items stay `pending` for a marker.
- A learner note or generated draft never silently becomes keyed assessment
  truth, lesson truth, a score, or mastery.
- Key material (`CORRECT:`, `TRAP:`, rationale) is disclosed by the runtime,
  never by the model mid-session.
- No em dash characters in authored repository prose.
- Handoffs land in files, not chat: objective, files read, files produced,
  decisions, unresolved conflicts, verification done and owed, exact next
  action.
