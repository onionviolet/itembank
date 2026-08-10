# Style: Worked Example -> Variation -> Formalization

[STYLE-PARENT: house]

## Voice

Content parent: expository. Each `###` section is one knowledge point: a
fully worked `[!EXAMPLE]` with annotated steps comes first, then a
variation the learner must attempt (`[!KEY]` practice), and the formal
statement last -- a definition read after it has been watched work is a
compression, not a string. This is Math Academy's knowledge-point shape
(catalogue 4) and the best-replicated result for novice procedural
learning; fade the annotation on later examples as the learner's evidence
warrants (Phase 7's selection decision, never a style rewrite).

## Rules

| id | kind | params | severity | lock | prompt |
|----|------|--------|----------|------|--------|
| example.before.variation | order.before | [!EXAMPLE], [!KEY] | error | | yes |
| variation.per.knowledge.point | style.require | [!KEY], 1 | error | | yes |
| section.cadence | cadence.section | 120, 400 | warn | | no |

## Exemplar

### Completing the square

> [!EXAMPLE] Complete x^2 + 6x + 5 by completing the square.
> 1. Halve the linear coefficient: 6 / 2 = 3.
> 2. Square it and add to both sides: (x + 3)^2 - 9 + 5 = 0.
> 3. Factor and simplify: (x + 3)^2 = 4, so x = -5 or x = -1.

Now attempt the variation item that follows before reading the formal
statement of the square-completion procedure.

> [!KEY] Completing the square rewrites ax^2 + bx + c as
> a(x + b/2a)^2 + (c - b^2/4a); the procedure is the claim, not the
> answer.
