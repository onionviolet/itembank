# Plan template: the lesser-model executor standard

**Status:** standing template, adopted 2026-08-14 (vision inbox entry of the
same date). Every next-milestone plan is written against this template and the
executor bar in `PLANNING-DIRECTIVES.md` section 5. The reference exemplar is
`.planning/phases/13.9-walking-skeleton/13.9-01-PLAN.md`.

**Who executes:** a Sonnet-class model with no chat history and no repo
intuition beyond the files the plan tells it to read. The plan therefore
carries every decision; execution is transcription plus verification, never
judgment. The pre-handoff test: find any sentence a reasonable executor could
implement two different ways; either decide it in the plan or make it a
checkpoint.

## Required structure

Frontmatter (YAML), matching the house format used since Phase 13.5:

```yaml
---
phase: <phase-dir-name>
plan: <NN>
type: execute
wave: <N>
depends_on: ["<phase>-<NN>", ...]   # plans, not phases
files_modified:                      # exhaustive; a file not listed is out of scope
  - path/one
  - path/two
autonomous: true | false             # false when any checkpoint task exists
requirements: [<REQ-IDs or audit sections>]
must_haves:
  truths:                            # observable statements, testable after execution
    - "..."
  artifacts:                         # named things that must exist afterward
    - "..."
  key_links:                         # the non-obvious couplings that break silently
    - "..."
---
```

Body sections, in order:

1. `<objective>` What becomes true, why now, and what defect or gap this
   closes. Cite the decision records this plan implements; the executor never
   re-derives or re-litigates a decision.
2. `<context>` The exact files to read first, with `@path` lines. Nothing the
   plan depends on may live only in a chat.
3. `<tasks>` Each task carries:
   - `type="auto"` for executor work, `type="checkpoint:decision"` where the
     user must choose (state the options AND the recommended default), or
     `type="checkpoint:human-verify"` where only a human can confirm.
   - `<files>` the subset of `files_modified` this task touches.
   - `<read_first>` functions/sections by name and approximate line.
   - `<action>` numbered steps. Commands verbatim in fenced blocks with their
     expected output or exit code. Every user-visible string written out in
     full, never "an appropriate message". Content rules stated inline (for
     this repo: no em dashes in authored prose, additive format changes only).
   - `<verify>` the command or fixture that proves the task done, named
     before the work, plus the degraded-state behavior it must also prove.
4. `<out_of_scope>` The adjacent temptations this plan refuses, by name, so
   scope is enforced by the plan rather than by executor judgment.
5. `<summary_obligations>` What the SUMMARY file must record: deviations,
   decisions resolved at checkpoints, evidence pointers, and which truths were
   verified by which command.

## Standing rules the template enforces

- **One source of truth per decision.** A plan cites decisions
  (`DECISIONS-*.md`, UI-SPEC sections, audit sections); it never restates them
  in conflicting words.
- **Fixtures precede features.** Every task names its proof before its work.
  If proof needs a human or a browser, the task is a checkpoint, not an auto
  task with a hopeful assertion.
- **Real learner content never enters this repository.** Plans that touch real
  study material direct all such artifacts to a user-chosen root outside the
  repo, and repo-side records carry pointers, counts, and hashes only.
  `itembank guard` is the enforcement backstop.
- **Degrade, never block.** Any task adding a surface states its offline and
  failure behavior, and the verify step exercises at least one of them.
- **Checkpoint hygiene.** A checkpoint states what is being asked, the options,
  the recommended default, and what the executor does with each answer. An
  unanswered checkpoint stops the wave; it never gets a silent default.
- **Name the seam before adding a provider.** (Added 2026-08-15, IDEA-LEDGER
  IL-20260815-02.) When a plan introduces or extends a capability that is
  meant to vary (model backend, treatment policy, teaching surface,
  source-discovery root), it names the interface, the provider being built,
  and the consumers, and keeps the interface in one module so a later
  provider is a config change, not a rewrite. Layers whose variation is a bug
  (scorer, parser, evidence store) are never seams; they extend additively
  inside the runtime per AGENTS.md rule 1. No plugin registry, loader, or
  mount machinery is built until a second provider actually exists.
