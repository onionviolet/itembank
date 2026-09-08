# Reading-to-Itembank protocol

Use this protocol when a live-course source may become early reading or later practice. The numeric ranges are defaults, not quotas.

## Choose the learning mode

Modes are selectable treatments, not mandatory stages. A familiar topic may go directly to retrieval; a difficult topic may need teaching before a summary helps.

| Mode | Purpose | Default output | Evidence meaning |
|---|---|---|---|
| **Early view / familiarity** | Reduce first-contact cost | 5 to 10 minute topic map, five to eight terms, prerequisite reminders, and two or three things to notice in class | Exposure only. Optional recognition checks are unscored and give no mastery credit. |
| **Source summary** | Navigate or consolidate an available source | Central claims, definitions, diagrams, examples, and unresolved questions with page or slide locators | Preparation, not learning evidence and not answer authority. |
| **Teaching content** | Explain a mechanism the source does not make usable alone | One 20 to 35 minute lesson with three to five objectives, why-it-works explanations, a worked example, a contrasting case, and teach-back prompts | Guided performance stays labeled guided. |
| **Retrieval / quiz** | Test independent recall and transfer | Four to six varied items across the block, then explanations and targeted rereading | Readiness evidence only when answers and sources are verified and no hints appear during the scored attempt. |

Apply course policy before selecting a mode. A summary never replaces an explicitly assigned reading. After a summary, use one closed-source teach-back; if it exposes a gap, return to the cited source.

Track `source_state` separately from `acquisition_status`. A published file may still be `inventory_only`, which means it cannot support a claimed summary. Generated artifacts should also record `coverage`, `source_version`, `mode`, and `assistance`; treat these as protocol fields until Itembank supports them directly.

## Handle slides faithfully

- Preserve definitions, notation, diagram relationships, and instructor examples. Summarize by concept and cite slide locators.
- Mark sparse or unexplained slides as incomplete. Never invent what the instructor may have said aloud.
- Label supplementary explanation separately from instructor content.
- If visuals were not inspected, say so. Text extraction alone cannot establish coverage of diagrams or visual emphasis.
- Familiarity checks measure recognition, guided checks measure supported performance, and independent retrieval measures readiness. Never present immediate repetition of a revealed answer as mastery.

## Build a proper early reading

1. Start with the next published class topic or due preparation. Choose one coherent subsection, argument, proof family, or worked-example group. Archive completeness does not determine reading priority.
2. Budget 20 to 35 minutes and at most three to five learning targets. Dense proofs may require only a few pages. Split long required readings into coherent blocks without reducing assigned coverage.
3. Keep the evidence state visible:
   - **Published:** explicitly posted or assigned for the relevant class.
   - **Bounded:** the smallest coherent prerequisite or next topic supported by the verified sequence, normally no more than one class ahead.
   - **Provisional:** a weaker forecast capped at a 10 to 15 minute preview. Never attach an invented deadline.
4. End with closed-source retrieval or one small production attempt, then check against the source. A miss triggers a short prerequisite repair, not a larger speculative reading.
5. Persist: `course | class/topic | evidence state | source version and locator | reading range | time budget | targets | completion evidence | next recheck`.

## Promotion gate for practice

Create Itembank practice only when all of these are true:

- the source and course policy allow independent generated practice;
- the objective has an exact source locator and stable wording;
- the expected answer or rubric is independently checked against an authoritative source;
- the item scope is original and does not reproduce or closely imitate collected work;
- forecast state remains explicit. Provisional objectives never enter graded or mastery-scored quizzes.

Published objectives and stable bounded objectives may qualify. A completed reading, learner note, or one correct response is not assessment authority.

## Small-bank defaults

- Begin with two or three distinct items per new target. A reading check usually needs four to six items across the whole block.
- Mix brief retrieval with application or changed-context transfer. Add an explanation or misconception check when the objective calls for it. Do not pad coverage with surface-level clones.
- Use untimed learning mode first. After a committed response, show the answer or rubric, a short explanation, the source locator, and a targeted reread. After repair, use a fresh transfer item.
- For later mixed or scored quizzes, delay feedback until submission. Retest misses after a gap rather than immediately repeating the same item.

Before release, pass policy and source review, answer checking, Itembank schema and lint, statistics and objective coverage, and one real runtime smoke test. Report anything still unreviewed.

## Rescope safely

When a new post arrives, compare its source version and objectives with the current map:

- **Retain:** same objective and authority.
- **Revise:** objective remains but emphasis, range, or answer changes.
- **Replace:** the new source contradicts the old scope.
- **Retire:** the objective is no longer taught or practice is no longer permitted.

Preserve completed reading history. Quarantine only affected items and record the reason and replacement trigger.

Trace a changed source to affected summaries, lessons, and items through source version and objective. Do not reset unrelated material.

## Course boundaries

- **MATH:** use permitted notes, textbook examples, and fresh original contexts. Collected homework never enters generation.
- **CSCI:** use permitted lecture and textbook concepts for original tracing, conceptual, and small-program practice. Exclude lab prompts, student code, screenshots, tests, and assignment-specific errors. Verify course permission before generating.
- **POL:** direct reading and learner-written retrieval remain the default. Permission to acquire readings does not imply permission for AI quizzes.
- **CHIN:** distinguish vocabulary, grammar, register, listening, and production. Recognition practice is not evidence of speaking ability.
- **AS 103 and EMT:** use permitted instructional sources and published objectives, not assessment banks. EMT answers retain edition and protocol provenance; uncertain clinical claims require source verification.

Avoid these failure modes: treating the largest archive as the next reading; generating questions before selecting objectives; quietly promoting forecasts to assignments; unsupported answer keys; duplicate variants inflating coverage; stale items surviving a source change; course-policy restrictions disappearing during batch work; and feedback leaking before a scored attempt ends.
