# Style: Artifact First (Bottom-Up ordering, PRIMM pacing)

[STYLE-PARENT: house]

## Voice

Content parent: expository. Bottom-Up ordering (concrete artifact ->
observed behaviour -> the name for it) composes with PRIMM's five-stage
pacing (predict, run, investigate, modify, make) -- orthogonal rules in one
style (D-03, catalogue 10+11). Each section opens with a prediction the
learner must commit to (`[!CHECK]`), then the runnable example, then the
abstraction it names. Falsify-first assumption recorded: if the Wienand
reading of "The Bottom Up" is wrong, this style re-derives from PRIMM
alone.

## Rules

| id | kind | params | severity | lock | prompt |
|----|------|--------|----------|------|--------|
| predict.opens | open.with | [!CHECK] | error | | yes |
| concrete.before.abstract | order.before | [!EXAMPLE], [!KEY] | error | | yes |
| stage.sequence | style.require | [!CHECK], 1 | error | | yes |

## Exemplar

### What a syscall does

> [!CHECK] Run this program and predict what it prints before reading on.
> import os; print(os.getpid())

The runnable artifact above showed a process id -- an observable behaviour.
That behaviour is the concrete thing a syscall produces: a request from a
process to the kernel. The abstraction (the syscall) is named only after
the artifact has been run and investigated.
