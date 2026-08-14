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

## Shipped surfaces for the protocol steps

Skills document only shipped command surfaces. These exist today:

| Protocol step | Shipped surface |
|---|---|
| Contract and grammar | `python itembank.py spec`, `schema`, `usage`, `config` |
| Inventory a bank | `stats BANK`, `coverage BANK`, `select` |
| Inventory a source | `audit source FILE` (read-only, locator-faithful) |
| Source-versus-bank coverage | `audit coverage --source S --bank B` (read-only) |
| Deterministic validation | `lint BANK` (errors and warnings by item number) |
| Plain preview | `lesson BANK`, `study BANK`, the bank file itself in a Markdown reader |
| Rich preview | `build BANK` (static HTML), `serve BANK`, `render-style` |
| Bounded model-backed writes | `audit material`, `audit author --mode ... --state-dir ...` (manifest, before-image, pending set, exact-id approval) |
| Identity and fingerprints | `id-assign BANK` (the only direct bank writer) |
| Undo | `audit undo WRITE_ID --bank B --state-dir DIR` (refuses stale work) |
| Evidence, honestly | `evidence`, `trends`, `report`, `retract`, `mark`, `render` |
| Ship gate | `guard .` (no real bank committed; CI enforces it) |

## Pending surfaces

The following section-10 capabilities have no shipped command yet. Where a
skill needs one, it states the manual planning-level procedure and marks the
surface as pending. Do not invent commands for them:

- A course manifest or course package command (14B).
- Discovery, binding, link/import/move/supersede, and reconciliation commands
  across multiple roots (14A/14B). Today this is a manual, read-only,
  documented inventory.
- A rights-grant record or per-operation rights command. Today rights are
  stated in the operation manifest prose and unknown stays restrictive.
- A general expected-fingerprint compare-and-swap write surface outside the
  `audit author` loop. Today, bounded writes go through `audit author` or are
  ordinary reviewed file edits with the diff shown before writing.
- Dependency and staleness marking. Today staleness is reported in the
  handoff, not recorded by a command.
- The semantic lesson profile, media policy, and legacy-upgrade tooling
  (16A/16C). See the stub skills.

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
