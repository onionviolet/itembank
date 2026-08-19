# 14A freeze record

## 2026-08-18: reflow-normalization decision (D-14A-2's deferred half)

**Decision: option-a. Keep the first cut. No reflow normalization.**

`identity.normalize_for_fingerprint` is unchanged: line endings are
normalized to `\n` for every kind, and trailing whitespace is stripped for
every kind except `bank` and `lesson`. No further collapsing of mid-content
whitespace or line-wrap position is added.

### Decision provenance

Weibao's verbatim answer, when the reflow corpus check's evidence and the
two options were put to him: "do whats best and keep things open in case
another option is better." This is a delegation with a keep-options-open
condition, not a direct pick of option-a or option-b.

The orchestrating agent resolved the delegation to **option-a** under that
condition. Option-a is the reversibility-preserving choice: the rule can be
added later as a recorded migration with its own corpus evidence, while
option-b's absorbed changes (a rewrap that stops being recorded as a
revision) could never be recovered retroactively once adopted, because the
information about what changed would simply never have been written to the
journal. Option-a keeps the later door open; option-b would close it. The
plan's own recommended default was also option-a, for the matching reason
stated there: "every change [the candidate rule] absorbs is a change a
compare-and-swap write will pass without noticing."

### Evidence: the four reflow counts

From `tests/file_fault_tracer.py:reflow_corpus_check()`, run over a 2000-file
mutation sample of the 10k synthetic corpus (`.planning/phases/14A-identity-lifecycle-operation/14A-TRACER-REPORT.md`,
"Reflow corpus check" section):

- Total mutations: 2000
- Meaningful changes noticed by the first cut: 500
- Reflow-only changes noticed by the first cut: 500
- Changes the first cut already absorbs (trailing whitespace, line
  endings): 1000
- False-absorption count (candidate rule would absorb a change that is
  NOT reflow-only): 0
- Mutation class proportions used: content=0.25, line_ending=0.25,
  reflow=0.25, trailing_ws=0.25

The false-absorption count is 0 on this corpus: the candidate rule would
not have discarded any of the synthetic content mutations. This does not
by itself justify adopting the rule (a synthetic corpus of generated
filler prose is not the same evidentiary weight as behavior on the
learner's own material over time), but it does confirm the rule is not
obviously unsafe. The decision to stay with option-a rests on the
asymmetry of recoverability described above, not on this count alone.

This amends `DECISIONS-PRE-14A-2026-08-14.md`'s D-14A-2 deferred item: the
reflow half of D-14A-2 is now resolved as option-a, recorded here with its
evidence.

### Reconsideration condition

This decision stays open, per Weibao's own keep-options-open instruction.
If rewrap-only revisions become a real annoyance in a later history view, a
later phase may:

- add reflow normalization as a recorded migration with its own corpus
  evidence (re-running a check of this same shape against real learner
  material, not only synthetic filler), or
- handle rewrap noise in the presentation layer instead of the fingerprint
  layer (for example, collapsing adjacent whitespace-only revisions in a
  history view without changing what the journal records).

Both routes stay available under option-a; neither route is available,
after the fact, under option-b.

### What the executor did with this answer

Per the plan's Task 3 action list for option-a: nothing was changed in
`identity.normalize_for_fingerprint`. The decision and the counts are
recorded here. Task 4 proceeds on this basis.
