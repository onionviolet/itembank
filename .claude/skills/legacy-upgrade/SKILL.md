---
name: legacy-upgrade
description: "Upgrade legacy lessons and question artifacts safely: run the eleven-item baseline audit, propose a bounded reviewable diff, reject cosmetic novelty, link derived enhancements the artifact cannot express, and halt on any keyed-meaning change (upgrade_audit.py, Phase 16C)."
---

# Upgrade a legacy artifact

**Provenance:** stubbed 2026-08-14 (reframe slice 4b) per
`.planning/research/phase-16/14-synthesis.md` section 10; shipped 2026-08-29
by plan 16C-08.

Older lessons and banks were written before capabilities that exist now. This
skill is how you make one of them better without losing anything it already
had, and without touching the one thing an upgrade may never touch.

## The order, which is not negotiable

**1. Audit before you edit.** Run `upgrade_audit.baseline_audit(bank_path)`.
It returns eleven rows in a fixed order: `current_parse`, `identity`,
`fingerprint`, `objectives`, `sources`, `rights`, `media`,
`assessment_boundaries`, `plain_rendering`, `rich_rendering`, `validation`.
Read them before proposing anything. There is no function that produces a
diff without auditing first, so this is a property of the code rather than a
rule you have to remember.

The `sources`, `rights`, and `media` rows read `plan-text stand-in` today,
because their backing records have not shipped. That is the honest answer,
not a pass. Do not report those three as checked, and do not fill them in
from your own reading of the artifact.

**2. Propose a bounded diff.** Every change carries `before`, `after`, and a
`reason` naming its learning value. A change whose reason is empty or reads
`cosmetic` is skipped with `Skipped: no learning value added.` and never
reaches the proposed list. If you cannot say what a change teaches better,
it is churn, and this tool will not offer it.

**3. Never apply the change yourself.** `upgrade_audit` reads and proposes.
It writes nothing on any path, including the halted one. Mutation goes
through the 14A journal operations under the operation contract in
`../OPERATION-CONTRACT.md`: expected base fingerprint, temp file, validate,
atomic commit, journal entry. Present the diff for human review and stop.

**4. Preserve identity and history.** An accepted upgrade never changes an
artifact's item IDs. The audit records identity before and after so a
reviewer can see that it did not.

**5. When the artifact cannot express an enhancement, link it beside.**
`upgrade_audit.cannot_express` renders the enhancement as a derived trio
projection and states the portability cost in words: the derived form lives
beside the file, not inside it, and does not travel when the file is copied
or exported alone. Say that cost out loud. An enhancement silently stored
beside an artifact is one someone loses in the first move and cannot explain
the absence of.

## The halt

`upgrade_audit.run_upgrade(bank_path, proposed_changes)` compares what the
upgrade WOULD produce against the original through
`upgrade_audit.keyed_meaning_delta`, which pairs items by id and watches
three things: the tested-content fingerprint, the difficulty, and the
objective alignment.

On any delta the run halts. The result carries `KEYED_HALT_COPY`:

> Halted: this change would alter keyed assessment meaning ({what}).
> Assessment changes are reviewed separately and are never part of an
> upgrade.

and exactly two affordances, `Open assessment review` and `Cancel upgrade`.
There is no third, no override, no force flag, and no diff on a halted
result. Do not offer the learner or the reviewer a way past it, and do not
build one: assessment meaning belongs to the runtime and its own review, and
an upgrade is not where it changes.

A rationale rewrite is not a keyed change. `model.content_fingerprint`
deliberately excludes `why`, `disc`, `trap`, and the rest of the reasoning
around an item, so improving an explanation is an ordinary proposed change
while rewriting a stem is a halt.

## Before you start

Read the "Course artifact workflow" section of `.claude/CLAUDE.md`, step 7 in
particular, and the operation protocol in `../OPERATION-CONTRACT.md`. A
worked fixture lives at `fixtures/legacy_pre135_bank.md` and the behavior
this skill describes is asserted in `tests/legacy_upgrade_roundtrip.py`.
