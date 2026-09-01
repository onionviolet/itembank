# 16A-01 summary (RETROSPECTIVE)

**This is a retrospective record, written 2026-09-01** to close the
plan-summary pairing gap found by the 17B-01 precondition run
(`.planning/phases/17B-production-vertical-tracer/17B-PRECONDITION.md`).
Plan 16A-01 was executed 2026-08-27; its summary was never written at the
time. Everything below is reconstructed from the commit record (commits
`3a8938d`, `94a39ed`, `d7b2e93`), `16A-PRECONDITION.md`,
`16A-DECISIONS.md`, and `16A-FREEZE.md`. Nothing here is a new claim;
where the record is silent, this file says so plainly.

## Precondition result

Commit `3a8938d` (2026-08-27), writing `16A-PRECONDITION.md`: the check
passed on all seven steps with **no deviations**, run immediately after
the 14B freeze closed (which it had been waiting on). Every 14A and 14B
constant Phase 16A was planned against, read from plan text at planning
time because those modules did not yet exist, matched the landed source
exactly, so plans 02 through 10 needed no re-reading against the freeze
records. Phase 13.9 was checked directly rather than through
`14B-FREEZE.md` (the ROADMAP forbids that freeze closing behind an
unwalked skeleton, and a downstream record is not evidence for its own
precondition). The three additivity baseline hashes matched the values
recorded at planning time, so there was no found-versus-planned pair to
record; `capabilities.py` was correctly absent. This run cleared the halt
that 16B's precondition dry run had reported earlier the same day. The
full per-step record, including the hashes themselves, is
`16A-PRECONDITION.md`; this retrospective does not duplicate it.

## The checkpoints, and how they were settled

Tasks 2 and 3 carried the two one-way decisions reserved for Weibao,
D-16A-1 (promote the semantic-role registry or add alongside, plus the
seven role token spellings) and D-16A-2 (where the capability registry
lives and which module owns the media grammar). **Weibao did not answer
them directly.** Commit `94a39ed` records that both took the plan's own
RECOMMENDED DEFAULT under his 2026-08-27 standing delegation: the seven
roles were added alongside the shipped four (not promoted), and the
capability registry went into a new pure `capabilities.py` while the media
and activity grammars stayed in `model.py`. Each `16A-DECISIONS.md`
section says in its own words that it is an agent choice under the
delegation and not his answer, quotes the delegation verbatim, names the
accepted costs, and states what reversing it costs today versus after
16A-02 lands. The fourteen one-way strings (seven role tokens and their
seven slug-and-label pairs) were checked character by character against
plan lines 543 to 549 before commit; the tokens as finally recorded are in
`16A-DECISIONS.md` under D-16A-1 and this retrospective does not
re-transcribe them.

D-16A-3 through D-16A-9 were transcribed from the plan's own objective
table, plus the probe-classification note recording that both unclassified
edge-coverage rows (CAP-01 completeness, CAP-03 derivation) were
classified and neither dropped.

## One routed question

Commit `d7b2e93` appended a routing note to `16A-DECISIONS.md`: a
`## MEDIA` row's rights column holds a single granted/denied/unknown value
while every other durable rights record carries the seven-key
`identity.RIGHTS_OPERATIONS` map. Verified against plans 16A-04 and
16A-05 as deliberate and consistent, not an error, and not a reopening of
D-16A-8; routed to the subphase that first packages or exports a media
asset, so it is inherited rather than rediscovered.

## Plan edits forced in plans 02 through 10

Both checkpoints took the recommended defaults, which are the paths plans
02 through 10 were written for. No plan-edit list was recorded in the
commits, and `16A-DECISIONS.md` records the choices rather than forced
edits; the record is otherwise silent and this retrospective does not
invent an edit list.

## Command-by-command stdout

The plan asked this summary to record which truth was verified by which
command with actual stdout. The surviving per-step record is
`16A-PRECONDITION.md`'s table; verbatim stdout beyond what that file and
the commit messages preserve was not recorded, and the record is silent
there.

## Why this summary was missing

The record is silent on why no summary was written on 2026-08-27. The
three commits landed within minutes of each other late that evening and
wave 2 work began immediately after; the summary step was evidently
dropped in that handoff. That is an inference, and it is labeled as one.
