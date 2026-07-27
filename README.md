# itembank

Author, validate and render exam-style question banks written in plain markdown.

It is also a local-first assessment runtime. Humans and AI tutors use the same
parser, scoring rules, resumable sessions, and evidence files through browser,
CLI, or JSON interfaces.

One file, Python standard library only, no network and no services. Render a
bank to a self-contained offline HTML quiz, or sit it under a local server that
writes every answer to disk as you give it.

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
itembank build bank.md        # interactive offline HTML quiz, NOTHING is saved
itembank serve bank.md        # sit it locally, every answer written to disk
itembank stats bank.md        # item mix, objective coverage, answer-position skew
itembank start bank.md       # start a resumable JSON assessment session
itembank next SESSION.json   # return the next item without its answer key
itembank submit SESSION.json --answer '"B"'  # score and record a response
itembank report SESSION.json # summarize the recorded evidence
itembank guard .              # fail if a real question bank got committed
```

The intended loop with an LLM:

1. `itembank spec` and paste the output into your prompt.
2. Ask for questions on your material.
3. Save them to a markdown file.
4. `itembank lint` it, paste the errors back, iterate.
5. `itembank build` and study.

For an agent, use the JSON session interface instead of scraping HTML:

1. `start` selects a deterministic set and returns the first public item.
2. `next` returns the current item without answers, rationales, or model text.
3. `submit` scores the response, records it locally, and returns the next item.
4. `report` returns objective-level evidence and manually graded response count.

The runtime owns answer keys, scoring, session position, and attempt recording.
An agent owns explanation and remediation choices. This separation prevents a
tutor from silently changing the test or grading its own explanation.

## Item types

Six. Five are the NREMT set, chosen because it spans familiarity through
discrimination and because scoring is uniform across it. The sixth, `short`, is
constructed response, and it is the one the machine refuses to mark.

| Type | Task |
|---|---|
| `mc` | pick one of four (default; no `[TYPE:]` line needed) |
| `multi` | pick a fixed number from five or six |
| `table` | classify each row into a named category |
| `build` | put options into a required order |
| `dnd` | sort items into buckets |
| `short` | type an answer in prose; never auto-graded, marked later against a rubric |

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

## Sitting a quiz that gets graded

`build` writes a static HTML file. A page opened from `file://` is sandboxed by
the browser: it cannot write anywhere, so when the tab closes the sitting is
gone. That is fine for drilling and useless for anything anyone will mark.

`serve` is the same page behind a loopback server. Each answer is POSTed the
moment it is given, and the process writes an attempt file to disk. Nothing is
batched at the end, so a closed tab or a dead battery costs at most the item in
progress.

```
itembank serve bank.md
```

It prints a `http://127.0.0.1:...` URL, opens your browser at it, and writes
`_attempts/<bank>_attempt_<date>.md` next to the bank. Ctrl-C when you are done.
Nothing listens on any external interface and nothing leaves the machine.

Useful flags:

| Flag | Why |
|---|---|
| `--reveal` | show the model answer after each `short` item. Off by default, because seeing it turns the items after it into recognition |
| `--out PATH` | put the attempt file somewhere specific |
| `--port N` | default 8731. If it is taken or blocked, a free port is used automatically |
| `--no-open` | do not launch a browser |

Then hand the attempt file to whoever is marking it, with `GRADING.md`.

## Running this when there is no agent around

Every part of this works with no AI in the loop. If you are out of usage, out of
credits, or offline:

**Sit a quiz.** `python itembank.py serve bank.md`. Answer, Ctrl-C. The attempt
file is on disk. Selected-response items are already marked in it. It will still
be there tomorrow.

**Mark your own short answers.** Follow `GRADING.md`, including the part about
why self-marking is worse and how to blunt it. Do it a day later, mark strictly
against the rubric wording, and fail anything arguable.

**Write more questions without an agent.** `itembank spec` prints the whole
format. Write items by hand in any editor, then `itembank lint` them. The linter
is the reviewer: it catches the structural mistakes and the two quality ones
(a distractor that never says when it would be correct, answers clustering on
one letter).

**Check a bank you already have.** `itembank stats bank.md` shows the item mix,
which objectives are covered, and the difficulty spread. If one objective has
nine items and another has none, that is visible in one command.

**The only thing that needs an agent** is someone else marking your prose. That
work queues: attempt files accumulate, and a marker can do six of them in one
pass later. Nothing blocks on it, and nothing is lost while you wait.

## Design boundaries

**This is an assessment protocol and runtime, not only a renderer.** Markdown is
the durable item source. The runtime is the shared layer beneath HTML, CLI, and
agent adapters. A future MCP or function-calling adapter should wrap the JSON
commands rather than implement a second parser.

**This does not generate questions.** The LLM writes them; this validates and
renders them. Any feature drifting toward generating content belongs in a prompt.

**This does not auto-grade prose.** A `short` item is recorded and left for a
marker. Keyword matching cannot separate a correct explanation from a confident
wrong one containing the right nouns, and a grader that cannot tell those apart
is worse than none, because it certifies the wrong answer.

**This does not do spaced repetition.** Recognition is for diagnosis and exam
simulation. Retention belongs in a spaced-repetition tool, and misses should
graduate there as recall cards.

**This does keep private local learning evidence.** The repository contains no
learner data, hosted analytics, or accounts. A session JSON file records answers,
deterministic scores, objective labels, and manual-grading state next to the
private bank. That is the minimum evidence an agent needs to choose a useful
next test. It is not a gradebook and is never committed to this repository.

**This repository never contains question banks.** Fixtures are synthetic and
written for this repo. `itembank guard` enforces it in CI: any markdown outside
`fixtures/` that parses as a bank fails the build. Real banks are usually
coursework-derived or textbook-derived, and they belong somewhere private.

## Layout

```
itembank.py               the whole tool
GRADING.md                how to mark an attempt file; hand this to your marker
fixtures/sample_bank.md   synthetic, exercises all six types, lints clean
fixtures/broken_bank.md   deliberately defective; CI asserts lint catches each defect
tests/serve_roundtrip.py  asserts a served sitting reaches disk
tests/agent_roundtrip.py  asserts the JSON session contract survives a full sitting

The JSON session commands use the same `itembank.py` runtime. Session files are
private output and should live in a bank's `_attempts/` directory.
```

## Licence

MIT.
