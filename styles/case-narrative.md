# Style: Case Narrative (progressive disclosure)

[STYLE-PARENT: house]

## Voice

Content parent: expository. The case-narrative style teaches judgement
revision through a `## SCENARIO` (Phase 9's staged-reveal container): the
learner sees the presentation, makes a call, and only then sees the next
finding. The reveal order is the pedagogy -- flattening the sequence into a
chapter would assert things the case only implied, which is why
render_style refuses case-narrative -> anything (D-11). Depends on Phase
9's `## SCENARIO` grammar; shipped last per D-07 because it is the only
style with an external dependency.

## Rules

| id | kind | params | severity | lock | prompt |
|----|------|--------|----------|------|--------|
| scenario.required | style.require | ## SCENARIO, 1 | error | | yes |
| narrative.holds | style.forbid | [!KEY] | warn | | no |
| reveal.sequential | order.before | [!CHECK], [!KEY] | warn | | no |

## Exemplar

### The unresponsive patient

## SCENARIO

You are called to a 54-year-old who is not responding. The first finding is
the presentation; the next finding is disclosed only after the learner
states the most likely cause.

The narrative holds the key: no `[!KEY]` interrupts the case, and the
checks that open each stage precede the keyed summary that closes it.
