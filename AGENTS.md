# AGENTS.md: itembank for AI coding agents

On-ramp for every agent. Claude Code also loads `.claude/CLAUDE.md`. Rationale
and walkthroughs live in `docs/AGENT-REFERENCE.md`; read a section only when
the task needs it.

## What this repo is

`itembank` is becoming a source-to-course learning workspace: learner-owned
sources become an objective map and a course of readings, lessons, practice,
and tests, and evidence informs what comes next. The shipped foundation is a
local-first assessment runtime: plain-markdown banks, `spec` and `lint`,
offline quizzes, graded sittings, on-disk evidence, and JSON sessions. Agents
may drive authoring and remediation; accepted artifacts stay files and scoring
stays in the runtime.
Full text: `docs/AGENT-REFERENCE.md §Repository purpose and binding documents`.

Binding documents:

- `.planning/SOURCE-TO-COURSE.md`: product contract. Read before course, source, agent, authoring, metrics, or learner-UI planning.
- `.planning/USER-VISION.md`: the user's goal verbatim. Never overwrite or summarize it; append dated statements only.
- `.planning/AGENT-WORKFLOW.md`: cross-agent workflow. Read before consequential work, using its task-scoped reading modes.

## The four layers (boundaries are the design)

```
model.py                  what a bank is, and what makes one invalid (one parser)
runtime.py                the only scorer; decides what a surface may see
server.py                 one loopback HTTP server
surfaces/                 clients only: quiz, study, day, session, CLI, export
```

Non-negotiable rules (planning files cite these numbers; keep them stable). Full text: `docs/AGENT-REFERENCE.md §Non-negotiable rules, full text`.

1. **One parser, one scorer.** Never parse a bank a second way or decide correctness outside `runtime.py`; adapters wrap the JSON commands. New scoring extends `score_response` additively; advisory graders may propose a mark, never settle one.
2. **Runtime owns assessment authority.** Correctness, session state, evidence, and keyed disclosure belong to the runtime. An agent may not invent a score, bypass the feedback mode, or reveal keyed content early.
3. **Never auto-grade prose.** A `short` item scores `None` (pending), never `False`. A labeled provisional AI assessment is allowed; the settled mark waits for review.
4. **Never commit real question banks.** Code and synthetic fixtures only; `itembank guard .` enforces it in CI.
5. **Evidence and banks stay on disk.** No telemetry or vendor-held data. Learner-initiated export, backup, and sync are allowed under export and share grants.
6. **Do not rewrite by default.** Choose per objective: direct reading, excerpt, lesson, notes/terms, example, visual, practice, or test.
7. **AI may do useful work** but must cite sources, label synthesis, disclose uncertainty and denominators, and keep changes reviewable and recoverable.
8. **Match the real target.** Standardized tests need a sourced blueprint and faithful construct, difficulty, and format mix; other courses follow their real objectives.
9. **Find before creating.** Search every approved root (Obsidian vault included) before drafting.
10. **Link deliberately.** Link, import, copy, move, and supersede differ. Preserve identity, provenance, and citations; never merge on similar names.
11. **Enhance progressively.** Lesson files must stay coherent in plain Markdown. Every interactive feature needs a static form that conveys the core meaning and an accessible interaction.
12. **Audit before upgrading.** Inspect first, preserve identity and history, propose a reviewable diff, validate after. No cosmetic rewrites; never silently change keys, difficulty, or alignment.
13. **Preserve direction.** Keep user quotations separate from interpretations; trace accepted work from vision to verification.
14. **Preserve viable breadth.** Every idea gets a disposition; untimely is not rejected. The rejection ledger is append-only (archiving completed ledgers is fine), and each rejection records evidence, reason, conflicting rule, alternative, date, and reconsideration condition.
15. **Name authority and recovery.** Every operation names its object, owner, source of truth, rights, egress, revision, conflict behavior, validation, and recovery. Presentation is not authorization.

## Object and authority model

Full text: `docs/AGENT-REFERENCE.md §Object and authority model`. Rules that gate changes:

- Accepted files are canonical; indexes, HTML, caches, and progress views are derived and disposable.
- Keep content, workflow, confidence, validation, rights, and availability states separate; `unavailable`, `unsupported`, `unknown`, `empty`, `error` each need their own recovery.
- Durable writes are compare-and-swap: expected fingerprint, temp file, validate, atomic commit, journal. Same ID, divergent bytes is a conflict. Discovery is read-only.
- Read, quote, transform, remote-process, package, export, and share are separate grants; unknown rights stay restrictive; hosted operations disclose exact egress.
- An agent never self-certifies accessibility. Export is not complete until a clean offline restore validates a manifest and reports every loss.

## Course artifact workflow

Read vision and contract; set roots; inventory; reconcile (never by filename alone); update objectives and treatments; create only what is missing; keep learner notes learner-owned; verify; report undo. Full steps: `docs/AGENT-REFERENCE.md §Course artifact workflow`.

## Prose style

No em dash characters in repository-authored prose, docs, comments, fixtures, lessons, or questions. Exceptions: verbatim source quotations and `.planning/USER-VISION.md` statements.

## Reading the code (context discipline, a standing rule)

Several modules cost 26k to 44k tokens each. Work symbol-first:

1. Locate before reading: grep the symbol and read a window around each hit.
2. Read whole files only under about 400 lines or when the task is file-shaped.
3. Prefer the contract (`python itembank.py spec`, schemas, test names) to the implementation.
4. For behavior changes, read the failing assertion and its helper, not the suite.
5. Say in your summary which touched modules you only sampled.

Rationale: `docs/AGENT-REFERENCE.md §Context discipline`.

## Quick start

More commands (`serve`, `study`, `day`): `docs/AGENT-REFERENCE.md §Quick start`.

```bash
python itembank.py spec                 # the whole format contract
python itembank.py lint bank.md         # validate; exits non-zero on error
python itembank.py build bank.md out.html   # offline quiz (holds the key, saves nothing)
python itembank.py stats bank.md        # item mix, objective coverage, position skew
python itembank.py start bank.md --count 10 --mode practice --out s.json  # JSON session
```

- Authoring a bank: spec, lint, `id-assign`, stats. Walkthrough: `docs/AGENT-REFERENCE.md §Authoring loop`.
- Tutoring with `start`/`next`/`submit`/`report`: never reveal the key or higher-tier content, decide the hint tier, imply a score, select items, mark prose as graded, replace the activity with chat, or retry indefinitely. Walkthrough: `docs/AGENT-REFERENCE.md §Tutoring loop`.

## Commit discipline (standing rule)

- Git authorization comes from the user or explicit standing workflow; this rule does not grant it.
- When authorized: one atomic commit per GSD plan, after it verifies, with only its files.
- Never leave a plan's work uncommitted in a nested worktree; concurrent processes can remove it.
- Other agents may have uncommitted edits here: stage your files by name, never `git add -A`.
- Message shape: `<type>(<plan>): <summary>`, e.g. `feat(10-01): ...`.

## Testing

Tests are stdlib-only scripts (no pytest); CI (`.github/workflows/ci.yml`) runs every `tests/*.py` plus extra gates.

```bash
python scripts/preflight.py --quick    # fast gates (~15 s); run before handing work back
python scripts/preflight.py            # adds the Python and JS suites
python scripts/preflight.py --list     # which gate mirrors which CI step
python tests/<name>_roundtrip.py       # one suite
```

CI detail: `docs/AGENT-REFERENCE.md §Testing and CI`.

## Skills

Playbooks live in `.agents/skills/<name>/SKILL.md` and are mirrored at `.claude/skills/`. Edit one, copy to the other; CI fails on drift (`diff -rq`). Catalog: `docs/AGENT-REFERENCE.md §Skills catalog`.

## Recording operational findings

Before the session ends, persist findings that cost turns (tool quirks, launch recipes, environment limits, concurrency hazards):

1. Reusable project findings go in the owning project file; provider memory only when available and authorized.
2. Machine-specific runtime notes go in `.reasonix/REASONIX.md` when in scope; a dated gate observation does not bind another harness.
3. Keep machine-specific paths and usernames out of committed docs; the CI path-leak step fails them.

Example and history: `docs/AGENT-REFERENCE.md §Recording operational findings`.

## Where to look next

- `docs/AGENT-REFERENCE.md`: full rules, object model, loops, skills.
- `README.md` (user docs), `ROADMAP.md` (public product contract).
- `.planning/` (GSD workspace); `.claude/CLAUDE.md` (GSD context, reading guide).

Personal working agreement: loaded globally from the planning vault's `_templates/portable_agent_rules.md`; do not paste it here.
