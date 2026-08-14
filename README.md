# itembank

Turn learner-owned books, syllabi, notes, exam blueprints, and question banks
into an inspectable course and learn through readings, rich lessons, targeted
practice, and graded tests whose evidence stays on disk.

itembank's shipped core authors, validates, and renders exam-style question
banks in plain markdown. Its next milestone makes the **course** the primary
unit: an AI-operable workspace that connects sources to objectives, decides
whether an objective deserves direct reading, a guided lesson, terms/notes, a
worked or visual explanation, practice, or a test, and uses recorded evidence
to recommend what comes next. See
[the source-to-course contract](.planning/SOURCE-TO-COURSE.md).
The [living user vision](.planning/USER-VISION.md) preserves the goal in
Weibao's own words and can be extended without rewriting the product contract.
The [cross-agent workflow](.planning/AGENT-WORKFLOW.md) explains how Codex,
Claude Code/Cowork, local agents, and other clients preserve that direction,
run research and synthesis, mutate artifacts safely, record deferred or
rejected ideas, and hand off work without relying on chat history.

One command gets you from a markdown file to a graded sitting:

- author in markdown → `lint` with actionable errors by item number
- offline quiz (`build`) or graded sitting (`serve`)
- JSON sessions for AI tutors (`start` / `next` / `submit` / `report`)
- `day` cockpit across every subject

The intended complete experience combines source-grounded course construction,
Brilliant-like interactive teaching, Albert-like objective practice and exam
preparation, and local inspectable artifacts. AI may drive discovery,
curriculum mapping, drafting, quality review, metric interpretation, and
remediation through a hosted coding-agent client or a registered local backend.
The parser, scorer, and evidence authority stay deterministic.

Here is the whole format:

```
Q1. An operator notices a low chlorine residual at the far end of the
     distribution network. What is the most likely explanation?
     A) Dead-end stagnation  B) A leaking service line  C) Pump cavitation
     CORRECT: A

Q2. Name two lab checks before clearing a main for service.  [TYPE: short]
     MODEL: turbidity, total chlorine
```

That is the whole format. `itembank spec` prints the rest.

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

A checkout run this way checks GitHub for a new version at most once per
interval (24 hours by default) when the daemon starts, and nothing but that
request leaves the machine. The first launch prints this notice once before
it checks anything. To turn the check off, set `update_policy` to `opt_in`
in `itembank.json`.

There is nothing to install. If you want it on your PATH, copy `itembank.py`
somewhere and make it executable.

## Install and run (release)

A release is one `itembank-X.Y.Z.pyz` file plus one launcher shim per OS,
downloaded from GitHub Releases and run in place. There is no installer and
no install step.

**Python 3.11 or newer must already be on the machine.** `zipapp` does not
bundle an interpreter, and the stdlib-only constraint this project holds
itself to rules out the tools that do. "Double-clickable" here means
double-clickable on a machine that already has Python 3.11+, not a
Python-free installer.

**Windows.** Double-click `itembank.bat`, or the raw `.pyz` itself where a
standard python.org installer has already set up the file association.

**macOS.** Double-click `itembank.command`. The first time you run a file
downloaded from the internet, Gatekeeper attaches a quarantine flag and
blocks the double-click with no explanation. Fix it once: right-click the
file, choose Open, and confirm -- or run `xattr -d com.apple.quarantine
itembank.command` from a terminal. Fully solving this needs a paid Apple
Developer signing certificate, which is deferred (`V2-DEL-01`, signed
binaries revisited when a second person runs the tool).

**Linux.** Install or double-click `itembank.desktop`, or run the executable
`.pyz` directly from a terminal (`./itembank-X.Y.Z.pyz`). File-manager
behavior for desktop entries varies across desktop environments; running it
from a terminal always works.

**Verify what you downloaded.** Every release includes `SHA256SUMS.txt`
covering the `.pyz` and every launcher shim (`itembank.bat`,
`itembank.command`, `itembank.desktop`). Check a downloaded file against it
with:

```
sha256sum -c SHA256SUMS.txt
```

## Use

Every command below is one CLI entry point into the same runtime. The grouped
index is the whole shipped surface. `python itembank.py --help` is the
ground truth it is kept against.

**The core loop:** author, validate, render, audit:

```
itembank spec                 # print the format contract; give this to your LLM
itembank lint  bank.md        # validate; exits non-zero on error
itembank build bank.md out.html   # offline HTML quiz; holds the key, saves NOTHING
itembank serve bank.md        # the graded sitting: the process scores and records
itembank stats bank.md        # item mix, objective coverage, answer-position skew
itembank coverage bank.md     # objective coverage map, computed on demand from the
                              #   bank and its ## SOURCES registry, never stored
itembank guard .              # fail if a real question bank got committed
```

**JSON sessions for agents:** the resumable, key-free assessment protocol:

```
itembank start bank.md --count 10 --mode practice --out s.json
itembank next s.json        # return the next item without its answer key
itembank submit s.json --answer '"B"'  # score and record a response
itembank report s.json      # summarize the recorded evidence
itembank teach s.json       # READ the fixed six-tier AUTHORED hint ladder; moves
                            #   nothing, so it is safe to run twice
itembank teach s.json --next     # open the next tier the learner has earned
itembank teach s.json --stumped  # open the next tier without that entitlement
itembank hint --session s.json   # one error-specific GENERATED hint from the model
                            #   backend, falling back to the authored tier offline
itembank rubric-review --session s.json  # per-point rubric suggestions; a suggestion
                                #   can never settle a mark (pending only)
itembank select bank.md     # preview a selection without starting a session
itembank override bank.md   # one extra sitting past today's cap, on confirmation
itembank interact --action '{"action_id":"..."}' s.json  # commit one semantic
                            #   action on the current visual item
itembank usage              # the machine-readable agent usage contract (MODEL-04)
itembank schema [name]      # the published JSON contracts, like `spec` prints the format
```

**Evidence and marking:** everything recorded is an append-only event:

```
itembank evidence --objective OBJ   # response history across every session and subject
itembank trends [--weeks N]         # longitudinal retention report: due, week series,
                                    #   weights, evidence claim (Phase 10)
itembank mark --session S --file m.ndjson  # record short-answer marks as events
itembank retract EVENT_ID --reason "..."  # undo an event by appending a reasoned
                                          #   compensating event; nothing is deleted
itembank render --session S --bank B attempt  # rebuild attempt markdown / session JSON
itembank id-assign bank.md    # the only command that writes into a bank: mints ids
                              #   and content-hash fingerprints (lint stays read-only)
```

**Learning surfaces:** the same bank as reading, flashcards, and today's work:

```
itembank study bank.md        # flashcards plus a session-only Learn loop
itembank lesson bank.md       # render the LESSON section as reading material
itembank render-style bank.md --style house   # lesson permuted into a named style
itembank gloss bank.md term   # one term's definition from the ## TERMS block
itembank key-review bank.md KEY_ID   # record a [!KEY] card as added to review
itembank lesson-check bank.md CHECK_ID --answer '...'  # score one gate band check
itembank lesson-skip bank.md CHECK_ID  # record one gate_skip event
itembank day plan.md          # today's work across every subject, ticked and logged
```

**Data and tools:** export, import, packaging, and housekeeping:

```
itembank export bank.md out.tsv --format basic   # Anki Basic TSV
itembank export bank.md out.tsv --format cloze   # Anki Cloze TSV
itembank export bank.md out.gift --format gift   # GIFT for LMS import
itembank export bank.md pack/ --objective OBJ  # audio drill pack (stem, pause, key, why)
itembank export bank.md out.tsv --format keys  # answer-key TSV
itembank import anki deck.apkg   # import an Anki deck into itembank candidates
itembank seed bank.md            # six-stage accept loop, one item at a time
itembank config                  # the settings schema, the way `spec` prints the format
itembank theme                   # preview, set, reset, or pick the source accent
itembank migrate --write         # one-time import of the three legacy stores into the
                                 #   evidence log (a dry run by default)
itembank update                  # check GitHub for a newer release, verify, prepare it
itembank daemon <dir>            # one process on one port for every surface
itembank sidecar                 # packaged-app launch: daemon in sidecar mode with the
                                 #   fixed stdout handshake (port/token/version)
itembank cli-twin <path>         # the CLI command that reaches the same runtime call as
                                 #   a served view path
itembank disclosure              # print the one-disclosure render-hook state
itembank calibrate <corpus-dir>  # measure each style warning's false-positive rate (D-18)
```

The intended loop with an LLM:

1. `itembank spec` and paste the output into your prompt.
2. Ask for questions on your material.
3. Save them to a markdown file.
4. `itembank lint` it, paste the errors back, iterate.
5. `itembank serve` and sit it. Use `build` only for a throwaway drill; a static
   page holds the answer key and saves nothing.

For an agent, use the JSON session interface instead of scraping HTML:

1. `start` selects a deterministic set and returns the first public item.
2. `next` returns the current item without answers, rationales, or model text.
3. `submit` scores the response, records it locally, and returns the next item.
4. `report` returns objective-level evidence and manually graded response count.

The runtime owns answer keys, scoring, session position, and attempt recording.
An agent owns explanation and remediation choices. This separation prevents a
tutor from silently changing the test or grading its own explanation.

## Using itembank with an AI coding agent

The same loops work whether the agent is you, a coding agent you pointed at
this repo, or a tutor you spawned. Everything an agent needs to start cold is
in `AGENTS.md` at the repository root (read by Codex, Cursor, Gemini CLI, and
Claude Code), with the full project context in `.claude/CLAUDE.md`.

**Repo skills.** This repository ships five playbooks that an agent can
invoke by name. The two trees are byte-identical mirrors:

| Skill | What it does |
|---|---|
| `absorb-book` | Turn a textbook, chapter, or notes into lesson + bank content |
| `curriculum-design` | Map a syllabus to objective coverage and find the gaps |
| `guiding-questions` | Tutor a learner through the JSON session protocol, one diagnostic question at a time |
| `author-bank` | Write or extend items and make them lint clean |
| `ocr` | Read text out of images via a local Ollama vision model, the vision bridge for text-only models (optional; needs `ollama pull qwen2.5vl:7b`) |

**Where each tool finds the skills** (the SKILL.md files carry the standard
`name` + `description` frontmatter every tool reads):

| Tool | Skill location | Setup |
|---|---|---|
| Claude Code | `.claude/skills/` | auto-discovered |
| Codex | `.agents/skills/` | auto-discovered |
| Gemini CLI, Cursor, GitHub Copilot, and other agents.md readers | `.agents/skills/` | auto-discovered |
| Reasonix | `.agents/skills/` | auto-discovered as a convention root; no config needed; the optional OCR plugin wiring lives in `reasonix.toml.example` |
| Anything else | point its skill root at `.agents/skills/` | see your tool's docs |

The two trees are byte-identical mirrors. Edit either and copy to the
other; CI runs `diff -rq` on them and fails on drift.

**The rules of the road for any agent** (full contract in `AGENTS.md` and
`.planning/UI-SPEC.md` §9):

- The runtime owns assessment authority: keys, legal feedback tiers, session
  state, evidence, and scoring are the runtime's call. An agent may build and
  teach the course, diagnose errors, and choose permitted explanation forms,
  but it may not invent a score, reveal keyed content early, or decide a tier.
- `short` answers are recorded, never auto-graded; they stay `pending` until a
  marker grades them against the rubric.
- Never commit a real question bank to this repository. Real banks live in
  private storage; `fixtures/` is synthetic.

`study` and `export` are generic bank surfaces. Subject-specific pipelines such
as Mandarin TTS and `.apkg` packaging remain separate because they require
content-specific dependencies and network behavior.

## The day surface

Every other command tests one subject. `day` shows the whole day across all of
them, records what got done, and counts the streak.

```
itembank day plan.md            # open today, tick it, ticks hit disk immediately
itembank day plan.md --lan      # also reachable from a phone on the same wifi
itembank day plan.md --due      # print what is outstanding across every lane, exit
itembank day plan.md --check    # print today's row and exit
itembank day plan.md --date 2026-01-06   # backfill a day you missed
itembank day plan.md --lanes wiring.md   # wiring file (default: lanes.md beside the plan)
```

It exists because of a specific failure. A study plan split across several
documents and tools is a plan that does not get opened, and two consecutive
days were lost that way while the plan itself sat there, correct and concrete.
The fix is not a better plan, it is one screen.

**Finding the plan.** Any markdown table whose first column parses as a date is
a plan table, so the plan can live inside a dashboard next to unrelated tables
and this does not need to be told where. Column headers name the lanes; a
`2026-01-07` or a `**Mon Jan 5**` first cell both work.

**The floor.** A day counts if the floor lanes are done, not only if every lane
is. A plan with no smaller version offers all-or-nothing once a day starts
badly, and nothing wins. `full` and `floor` are both unbroken days in the
streak; the strip along the top shows which was which.

**The log** is markdown, one row per day, written beside the plan by default.
Same reasoning as attempt files: the reader is a human or an LLM, and both read
a table better than they read a state blob. The reader maps columns by the
log's own header row, so a log written before a lane existed still reads
correctly: a lane the header does not name is simply not done that day.

**The wiring (`lanes.md` beside the plan, optional).** Which Anki deck, notes
file, and dated fuse each lane carries, plus a table of global fuses. Data,
never code: fuses expire and lanes change, and a tool with them baked in dies
with them. Two kinds of table, told apart by their headers: a `Lane` column
wires lanes; a two-column table whose second header is a date carries global
fuses. An optional `Notes glob` column makes a lane's whole document cluster
reachable from its card through a file selector, and the notes button hands
the file to whatever already edits it. The wiring is linted like everything
else here: unknown lane, missing notes path, malformed date, and deck absent
from Anki are each a named error with its line, because a wiring mistake that
fails silently is a lane that silently stops being watched.

**The two computed numbers.** `behind` is past plan rows that asked for a lane
and were never ticked. `load` is what is still owed divided by the days left
to that lane's fuse; above 1.0 the lane no longer fits in the days it has
left, which is the signal the plan needs re-cutting. A cell that names no work
("none", "Slip budget") is a planned zero, never debt.

**Degraded, never broken.** Anki counts come over AnkiConnect and are omitted
with a note when Anki is closed; a missing wiring file turns off fuses and
badges and says so; a git repo around the plan adds an evidence dot per lane
(a change touched the lane's file today) and its absence just hides the dot.
A morning view that errors out because one of four sources is shut is a view
nobody opens.

## Item types

Eight types ship. The first five span familiarity through discrimination with
uniform scoring across them. `short` is constructed response, and it is the one
the machine refuses to mark. `visual` is the interactive assessment protocol
from phase 06.1, and `check` runs the learner's own code with no model anywhere
in the path.

| Type | Task |
|---|---|
| `mc` | pick one of four (default; no `[TYPE:]` line needed) |
| `multi` | pick a fixed number from five or six |
| `table` | classify each row into a named category |
| `build` | put options into a required order |
| `dnd` | sort items into buckets |
| `short` | type an answer in prose; never auto-graded, marked later against a rubric |
| `visual` | interactive plot or number-line item; the scene and scoring envelope are declarative JSON parsed as data, never executed |
| `check` | write and run your own code; scored against hidden cases, dichotomously, with no model anywhere in the path |

**Scoring is dichotomous on every type.** Two of three correct scores zero. This
is deliberate: a half mark hides the exact gap the item exists to find.

The authoring contract grows additively. A type or field that ships in a later
phase is added to `itembank spec`, never documented here before it exists.

Run `itembank spec` for the full contract with examples.

## The `check` item type

`check` is the one type where the learner's answer is *code*: the stem asks for a
program, the learner writes it in a real editor (vendored CodeMirror 6, Tab
inserts a tab, the gutter numbers the lines you see), and the machine runs it
once per authored case, then scores the pass vector through the same scorer as
every other type. A `CASE)` line pairs an input with an expected output:

```
Write a program that reads two integers and prints their sum.
[TYPE: check]
[LANG: python]              optional; defaults to python
[MATCH: trimmed]            optional; exact | trimmed | regex
CASE) 5 7 :: 12
CASE) 3 4 :: 7
STARTER:                    optional; pre-filled source
import sys
print(sum(map(int, sys.stdin.read().split())))
```

Three match modes are available: `exact` (byte-for-byte), `trimmed` (the default;
whitespace around the output is ignored), and `regex` (the expected value is a
pattern). A function-signature mode, `[HARNESS: name]`, calls the named function
with each case's arguments instead of running the program; `[TOLERANCE: 0.01]`
then compares float return values within the stated tolerance.

Two bounds apply while the learner's code runs, and their settings keys are
`check.timeout_seconds` (default 5) and `check.max_output_bytes` (default 65536):
a case that runs past the deadline is stopped, and a case whose output exceeds
the cap is cut off. Each renders as a failed case whose status says it was
*stopped by a bound*, so a learner can tell that apart from producing wrong
output. A run the deadline kills is not graded at all: it records no verdict and
stays pending for a marker, matching how `short` is never auto-graded.

Execution is refused by default when itembank serves on your network: the
`check.allow_lan` setting (default false) must be switched on for a device on
the LAN to be trusted to run code. A page opened as a file cannot run code at
all, and says so.

What the bounds stop, and what they do not, is the project's honest-limits
statement. The exact sentence appears in two places and no more -- the `check`
section of `itembank spec` and the line beside the editor on every served check
item -- and both read the single constant `model.HONEST_LIMITS_NOTE`. See the
`check` section of `itembank spec` for the canonical limits text; the README
does not duplicate it. And because this type runs the learner's own code and
scores it deterministically with no model anywhere in the path, a course's ban
on model-assisted work is not engaged by using it.

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

`serve` also scores. The page is sent items with the key stripped out, posts
each response to the process, and renders the verdict and the explanation the
process sends back. So under `serve` the browser never holds an answer, and
there is one scorer for every surface: the same function the JSON session
interface calls.

**`build` is the exception, and it is one on purpose.** A `file://` page has no
process to ask, so the static file carries the key. Anyone who opens the source
can read the answers. That is acceptable for drilling alone and disqualifying
for a sitting somebody else marks or an agent administers, so use `serve` for
anything that counts. What `build` does not carry is a second set of scoring
rules: Python writes a canonical key into the page and the page compares one
string against it.

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

**How it is built.** Four layers, and the boundaries between them are the
design. `model` says what a bank is. `runtime` holds the only scorer and decides
what a surface may see. `server` is one loopback HTTP server. Everything in
`surfaces/` is a client: the quiz page, `study`, `day`, `export`, the JSON
session commands and the CLI. No surface parses a bank a second way and none of
them decides whether an answer is correct.

**This does not generate questions.** The LLM writes them; this validates and
renders them. Any feature drifting toward generating content belongs in a prompt.

**This does not auto-grade prose.** A `short` item is recorded and left for a
marker. Keyword matching cannot separate a correct explanation from a confident
wrong one containing the right nouns, and a grader that cannot tell those apart
is worse than none, because it certifies the wrong answer.

**Model output is never accepted as a score.** An optional hosted or local
backend may generate hints and per-point marking suggestions. The runtime gates
the tier (`tier_gate.py`), so a model cannot unlock a tier for itself, and a
suggestion is a `pending` token until a human marks it. Model activity may be
logged as provenance, but model output is never accepted as response evidence
or a score without the runtime's deterministic or human-approved action.

**Retention is evidence-derived, not a recall scheduler.** `retention.py`
derives due state and daily caps by replaying captured evidence through one
scheduler strategy (FSRS is the registered default), surfaced as `itembank
trends`, the `day` cockpit's recommendations, and the retention report variant.
What it still does not do: it is not a per-card recall scheduler, and `study`'s
Learn loop remains session-only. A learner who wants spaced-repetition recall
still graduates misses to a dedicated tool.

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
itembank.py               entry point; imports every layer, delegates to cli
model.py                  what a bank is, and what makes one invalid (one parser)
runtime.py                the only scorer; decides what a surface may see
server.py                 one loopback HTTP server, for surfaces that need a browser
evidence.py               the append-only evidence log and its readers (retraction-safe)
retention.py              evidence-derived pacing: FSRS strategy, caps, trends, day loads
selection.py              the one selection engine: spec expansion, profiles, seeding
model_adapter.py          optional hosted/local model backend (hints, marking suggestions)
tier_gate.py              fail-closed boundary: what a model may say, at which tier
build.py                  the static HTML quiz build
schema_validate.py        the published JSON contract validator (stdlib subset)
surfaces/                 26 client modules: quiz.py, quiz_page.py, session.py, study.py,
                          day.py, cli.py, theme.py, daemon.py, export, migrate, seeding, ...
schemas/                  published JSON contracts (12 documents; `itembank schema`)
styles/                   lesson render styles (6; `itembank render-style`)
launchers/                itembank.bat / itembank.command / itembank.desktop
installers/               NSIS installer sources
scripts/                  build/asset generators and the OCR helper scripts
src-tauri/                the desktop shell (Tauri over the Python sidecar)
fixtures/sample_bank.md   synthetic, exercises six of the seven types, lints clean
fixtures/broken_bank.md   deliberately defective; CI asserts lint catches each defect
GRADING.md                how to mark an attempt file; hand this to your marker
AGENTS.md                 agent on-ramp: layers, boundaries, authoring + tutoring loops
.agents/skills/           agent playbooks (absorb-book, curriculum-design, guiding-questions, author-bank, ocr)
.claude/skills/           same playbooks, mirrored for Claude Code (CI keeps the two trees byte-identical)
tests/                    every tests/*_roundtrip.py; CI runs each one
ROADMAP.md                product contract and sequenced improvement plan
```

The JSON session commands use the same `itembank.py` runtime. Session files are
private output and should live in a bank's `_attempts/` directory.

## Licence

MIT.
