# itembank

Author, validate and render exam-style question banks written in plain markdown.

One file, Python standard library only, no network and no services. The output is
a self-contained offline HTML quiz you open by double-clicking.

## Why this exists

A prose format spec does not fail loudly.

The specific failure that produced this tool: an AI was asked to write a 21-item
question bank. It invented its own format, wrote four turns of content in it, and
nothing noticed. The repository it was writing into already contained three
renderers and a documented format. The bank was silently unreadable by all of
them, and the error surfaced days later by accident.

That is not a discipline problem, it is a missing feedback signal. An author,
human or model, can conform to a prose spec or not with no way to tell which.

So the useful artifact here is not the renderer, it is the **contract**. `itembank
spec` hands an authoring agent the format. `itembank lint` tells it exactly what
it got wrong, by item number, in language it can act on. Authoring becomes write,
check, fix.

## Install

```
git clone <this repo>
python itembank.py --help
```

There is nothing to install. If you want it on your PATH, copy `itembank.py`
somewhere and make it executable.

## Use

```
itembank spec                 # print the format contract; give this to your LLM
itembank lint  bank.md        # validate; exits non-zero on error
itembank build bank.md        # interactive offline HTML quiz
itembank stats bank.md        # item mix, objective coverage, answer-position skew
itembank guard .              # fail if a real question bank got committed
```

The intended loop with an LLM:

1. `itembank spec` and paste the output into your prompt.
2. Ask for questions on your material.
3. Save them to a markdown file.
4. `itembank lint` it, paste the errors back, iterate.
5. `itembank build` and study.

## Item types

Five, the set the NREMT uses, chosen because it spans familiarity through
discrimination and because scoring is uniform across it.

| Type | Task |
|---|---|
| `mc` | pick one of four (default; no `[TYPE:]` line needed) |
| `multi` | pick a fixed number from five or six |
| `table` | classify each row into a named category |
| `build` | put options into a required order |
| `dnd` | sort items into buckets |

**Scoring is dichotomous on every type.** Two of three correct scores zero. This
matches the NREMT's own rule that no credit is given for a partially correct
response, and it is deliberate: a half mark hides the exact gap the item exists
to find.

Run `itembank spec` for the full contract with examples.

## What the linter checks

Syntax is the easy half. These are the checks worth having:

- **Every distractor must say when it WOULD be correct.** This is the property
  that makes a wrong option teach a second concept by contrast instead of being a
  dead end, and it is the first thing a model drops under length pressure.
- **Answer-position skew.** If correct answers cluster on one letter beyond
  chance, the bank is easier than it looks and the author cannot see it. Run
  against a real 388-item AI-written bank, the first thing this found was that
  53% of answers were B and 3% were D.
- Select count against keyed count, keys naming options that do not exist,
  categories referenced but never declared, duplicate stems, duplicate build
  steps, missing rationale fields, and items flagged `CONFIDENCE: low` that were
  never reviewed.

Errors block a build. Warnings advise.

## Design boundaries

**This does not generate questions.** The LLM writes them; this validates and
renders them. Any feature drifting toward generating content belongs in a prompt.

**This does not do spaced repetition.** Recognition is for diagnosis and exam
simulation. Retention belongs in a spaced-repetition tool, and misses should
graduate there as recall cards.

**This repository never contains question banks.** Fixtures are synthetic and
written for this repo. `itembank guard` enforces it in CI: any markdown outside
`fixtures/` that parses as a bank fails the build. Real banks are usually
coursework-derived or textbook-derived, and they belong somewhere private.

## Layout

```
itembank.py              the whole tool
fixtures/sample_bank.md  synthetic, exercises all five types, lints clean
fixtures/broken_bank.md  deliberately defective; CI asserts lint catches each defect
```

## Licence

MIT.
