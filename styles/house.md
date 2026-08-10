# Style: House (the artifact-wide baseline)

The house style is the floor every lesson sits on, whatever its named
style. It is not a pedagogy; it is the artifact's non-negotiables plus the
shared register. `expository` is the content parent of every shipped style;
the house rules below apply to all of them (R1.4: house constrains the
artifact, style constrains the sequence).

## Voice

The locked house rows are **code constants** in `model.py`'s
`LOCKED_RULE_IDS`; this file documents them in prose and can never define,
override, suppress, or re-severity them (ruling 13, T-031-12):

- `runtime.decides` -- the runtime, not a model, decides what reaches the learner.
- `no.second.parser` -- exactly one parser.
- `no.second.scorer` -- exactly one scorer.
- `no.evidence.leave` -- evidence and banks stay on disk.
- `format.additive` -- every format change is additive.
- `accessibility.gates` -- the nine UI-SPEC section 8 gates.

House rules beyond the lock: one lesson serves one job (Diataxis: teach,
explain, or look up -- never a reference pretending to be a tutorial), calm
declarative register with mechanism before drill, every claim traceable to
a resolvable source, and no second-person hectoring. These rows are
parameterizations of the closed rule kinds; they never add a lint code.

## Rules

| id | kind | params | severity | lock | prompt |
|----|------|--------|----------|------|--------|
| diataxis.one.job | style.forbid | reference-material | warn | | yes |
| register.calm | open.with | prose | warn | | no |
| claim.traceable | style.require | [SRC:], 1 | warn | | yes |
| no.hectoring | style.forbid | second-person-hectoring | warn | | yes |
| section.cadence | cadence.section | 120, 400 | warn | | no |

## Exemplar

### Reading a rhythm strip

A rhythm strip is a timed record of the heart's electrical activity. This
section names the pacemaker before it names the abnormality, stays in the
calm declarative register, and cites the bank's `## SOURCES` registry for
every claim. Nothing here asserts a verdict the runtime has not scored.
