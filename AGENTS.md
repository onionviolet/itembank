# AGENTS.md — itembank for AI coding agents

This file is the universal on-ramp for AI coding agents (OpenAI Codex, Claude
Code, Cursor, Gemini CLI, and anything else that reads `AGENTS.md`). Read this
first, then the files it points at. Claude Code should also load
`.claude/CLAUDE.md`, which carries the full GSD project context.

## What this repo is

`itembank` is a local-first assessment protocol and runtime. You author
exam-style question banks in plain markdown; the tool validates them with an
actionable linter, renders them as an offline HTML quiz, or runs a graded
sitting through a loopback server. It also exposes deterministic JSON sessions
(`start` / `next` / `submit` / `report`) that an AI tutor uses to administer a
test without ever seeing the answer key. Python stdlib only — there is no
install step: `python itembank.py` from a checkout is the whole thing.

The useful artifact is the **contract**: `itembank spec` prints the format,
`itembank lint` tells an author exactly what it got wrong, by item number, in
language it can act on. Authoring becomes write, check, fix.

## The four layers (boundaries are the design)

```
model.py                  what a bank is, and what makes one invalid (one parser)
runtime.py                the only scorer; decides what a surface may see
server.py                 one loopback HTTP server
surfaces/                 clients only: quiz, study, day, session, CLI, export
```

Non-negotiable rules:

1. **One parser, one scorer.** Never parse a bank a second way and never decide
   correctness outside `runtime.py`. A future MCP/function-calling adapter must
   wrap the JSON commands, not reimplement them.
2. **The runtime, not a model, decides what reaches the learner.** Answer keys,
   scoring, session position, and attempt recording belong to the runtime. An
   agent owns explanation and remediation choices only.
3. **Never auto-grade prose.** A `short` item scores `None` (pending review),
   never `False`. Marking happens later against a rubric, by a human or a
   human-approved model.
4. **Never commit real question banks.** This repository holds code and
   synthetic fixtures only. `itembank guard .` enforces it in CI.
5. **Evidence and banks stay on disk.** No telemetry, no hosted gradebook.

## Quick start

```bash
python itembank.py spec                 # the whole format contract
python itembank.py lint bank.md         # validate; exits non-zero on error
python itembank.py build bank.md out.html   # offline quiz (holds the key, saves nothing)
python itembank.py serve bank.md        # graded sitting; every answer written to disk
python itembank.py stats bank.md        # item mix, objective coverage, position skew
python itembank.py study bank.md        # flashcards + Learn loop
python itembank.py day plan.md          # the day cockpit across subjects
```

## The authoring loop (writing a bank)

1. `python itembank.py spec` and follow the contract. Items are `Qn.` blocks
   with `[OBJECTIVE:]`, `[TYPE:]` (mc/multi/table/build/dnd/short), `CORRECT:`,
   `WHY BEST:`, `KEY DISCRIMINATOR:`, `DISTRACTOR ANALYSIS:`, `TRAP:`,
   `CONFIDENCE:`. A bank may carry one optional `## LESSON` section of teaching
   text above the first question, with `###` subheadings items link to via
   `[LESSON-REF: heading text]`.
2. `python itembank.py lint bank.md` — fix every `error`; warnings advise.
   Notable checks: every distractor must say when it WOULD be correct;
   answer-position skew is flagged; `CONFIDENCE: low` items must be reviewed.
3. `python itembank.py id-assign bank.md` — the only command that writes into a
   bank; mints opaque ids and content-hash fingerprints.
4. `python itembank.py stats bank.md` — check objective coverage and difficulty
   spread before shipping.

## The tutoring loop (administering a test as an AI tutor)

```bash
python itembank.py start bank.md --count 10 --mode practice --out s.json
python itembank.py next s.json        # returns the item WITHOUT its key
python itembank.py submit s.json --answer '"B"'
python itembank.py report s.json      # objective-level evidence
```

What the runtime guarantees you (an agent):

- `next` returns a `public_item` — stem, options, response schema — never the
  key, rationale, or model text.
- `submit` scores deterministically, records the attempt locally, and returns
  the next item.
- `short` responses are recorded but left `pending` for a marker; you must not
  pretend to have graded them.
- Repeated `submit` calls are idempotent (a `dedupe_key` guards replays).

Your side of the contract (see UI-SPEC.md §9 for the full list):

- You may ask **one diagnostic question** tied to the learner's actual wrong
  answer, and choose among permitted explanation forms (analogy, example,
  counterexample, visualization, derivation, simulation, Socratic question) —
  but only after the runtime has granted the tier for that content.
- You may **not**: reveal the key or higher-tier content, decide the hint tier,
  imply a score, select items, mark prose as accepted, or replace the activity
  with generic chat. Do not retry indefinitely.
- A learner's response may be `submit`-ted multiple times only as the runtime
  allows; you never change the test or the scoring.

## Commit discipline (standing rule)

**One atomic commit per plan.** When executing a GSD plan (or any phase
task), commit exactly once per plan, after that plan's own verification
passes, and only that plan's files. Do not batch two plans into one commit,
do not commit another plan's in-flight work, and do not leave a plan's work
uncommitted in a worktree — a nested worktree under the main checkout can be
removed by a concurrent process, and uncommitted work is then lost. If the
working tree carries another agent's uncommitted edits (this repo is
sometimes executed by concurrent chats), stage only your own plan's files by
name, never `git add -A`. Commit messages follow the repo's
`<type>(<plan>): <summary>` shape, e.g. `feat(10-01): ...` or
`test(10-02): ...`.

## Testing

Every test is stdlib-only and self-contained. There is no pytest dependency:

```bash
python tests/protocol_roundtrip.py     # lint codes, schemas, published contracts
python tests/agent_roundtrip.py        # full JSON session round trip
python tests/serve_roundtrip.py        # served sitting reaches disk, no key leak
python tests/scoring_roundtrip.py      # one scorer, offline key matches it
python tests/lesson_roundtrip.py       # LESSON grammar and reader
python tests/surface_roundtrip.py      # study and Anki export
# ...any tests/*_roundtrip.py — CI runs every tests/*.py (see .github/workflows/ci.yml)
```

CI (`.github/workflows/ci.yml`) additionally asserts `fixtures/sample_bank.md`
lints clean, `fixtures/broken_bank.md` is caught with each named error, the
sample builds, and every session payload validates against `schemas/*.json`
via `schema_validate.py`.

## Skills

Repo playbooks live in two mirrored trees so every agent finds them:

| Skill | Purpose |
|---|---|
| `absorb-book` | Turn a source document/textbook into lesson + bank content |
| `curriculum-design` | Turn a syllabus into objective-by-objective coverage, find gaps |
| `guiding-questions` | Run a Socratic tutoring session with the JSON protocol |
| `author-bank` | The write → lint → fix loop for new items |

- **Codex and agents.md readers**: skills are at `.agents/skills/<name>/SKILL.md`
  and are discovered automatically from the repo root.
- **Claude Code**: skills are mirrored at `.claude/skills/<name>/SKILL.md`
  (project-level). Invoke with `/name` or let Claude auto-match the description.
- **Other tools**: install by pointing your tool's skill root at
  `.agents/skills/` (the two trees are identical; edit either and mirror).

The two trees are mirrors of the same playbooks — keep them in sync when
editing.

## Where to look next

- `README.md` — full user documentation (item types, serve vs build, the day
  surface, design boundaries).
- `ROADMAP.md` — the public product contract and sequenced improvement plan.
- `.planning/` — the GSD planning workspace (PROJECT.md, REQUIREMENTS.md, the
  per-phase plans under `.planning/phases/`).
- `.claude/CLAUDE.md` — GSD project context for Claude Code.
