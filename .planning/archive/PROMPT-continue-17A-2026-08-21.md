# Continue: 17A visual system and the dsh embed

Paste this whole file as the first message of a new session.

---

You are continuing work on **itembank** at `C:\Users\wayba\Downloads\CTF\itembank`.

Read `.planning/EXEC-CONTEXT.md` first. Do **not** read `ROADMAP.md`,
`REQUIREMENTS.md`, `STATE.md`, `UI-SPEC.md`, `AGENT-WORKFLOW.md`, or
`PLANNING-DIRECTIVES.md` unless a specific question needs them. That stack is
about 122,000 tokens and re-reading it every turn is what a previous run spent
5.1 billion tokens on.

## Where things stand

Phase 17A-01 is executed and 17A-02 is decided. The prototype is
`prototypes/17a/itembank-prototype.html`, one self-contained file with no
JavaScript: eight screens, three looks, three navigation shapes, four accents,
all switched by radio inputs and CSS. `tests/visual_system_roundtrip.py` is at
29 checks and passing.

Chosen defaults, recorded in `17A-DIRECTION.md`: **structured-studio**,
**sidebar**, **indigo `#4a4ad4`**. Every other option stays selectable. A
default is a starting point, never a deletion.

`theme.DEFAULT_ACCENT` is still the shipped teal on purpose. Moving the real
default belongs to 17A-04 with its accessibility pass, not to a drive-by edit.

## The next job: 17A-06

The plan is `.planning/phases/17A-visual-system-component-foundation/17A-06-PLAN.md`.
Task 1 is resolved; the record is `17A-06-DECISIONS.md`. Read both.

The decision: **adopt `deepseek-ai/deepseek-harness` (`dsh`), and embed its web
UI as the Agent tab.** Verified by running it on 2026-08-21, not by reading:

- Installs on Node 22, serves at `127.0.0.1:3080`
- Sets no `X-Frame-Options`, no CSP, no `frame-ancestors`, so it frames cleanly
- Already driving `qwen3.8-27b:latest` under a `weibao-planing` profile
- MIT, 180,182 stars, pushed the same day

Weibao's position, which the evidence supported over an earlier objection of
mine: the interface is clean enough that embedding helps coherence rather than
harming it, and rebuilding a worse console would cost months for nothing.

**Both paths ship**, per `PLANNING-DIRECTIVES.md` section 1. The Agent tab
embeds the `dsh` web UI. The Python SDK stdio seam stays for operations
itembank drives from other screens.

### Do these next, in order

1. **Pin the `dsh` version.** The published package already differs from the
   README: the README documents `--no-open` and the shipped build rejects it.
   Pin exactly, and treat an upgrade as a tested change. `SESSION_FORMAT_VERSION`
   is `0` with no compatibility promise.
2. **Task 2:** add the `local-qwen` profile to `itembank.json` and write
   `tests/local_harness_roundtrip.py` first. The field is **`endpoint`**, not
   `base_url`; `base_url` fails with `settings.invalid_value` and that is the
   likeliest setup mistake, so cover it.
3. **Task 3:** the Agent tab embeds `dsh` in a frame with an **explicit `lang`**,
   because the served document is `<html lang="zh-CN">`.
4. **Open question worth one probe:** whether `dsh` exposes theming through
   plugin config. The indigo accent cannot reach inside a cross-origin frame, so
   either the tab visibly hands off to a different-looking tool, which is
   honest, or a patch aligns it. Not investigated.

## Facts already measured, so do not re-derive them

- `model_adapter.TRANSPORT_REGISTRY` has `hosted_cli` and `openai_compatible`.
  `_transport_openai_compatible` already tags its result `"local"`, so a local
  model needs a settings entry, not a module.
- `hosted_cli` is one-shot `subprocess.run`. `dsh` is a persistent
  newline-delimited JSON-RPC session over stdio. That gap is the entire content
  of any new `dsh_stdio` transport.
- `journal.commit_operation` does compare-and-swap with an operation log and a
  prior revision. Undo already works. Do not invent a second writer.
- `dsh` customization has three tiers: a `cordis.patch.yml` row replacement with
  no code, a plugin package via `dsh plugin --profile web add`, or a fork under
  MIT. `packages/skill/` is a skill provider registry, which is where
  itembank's ten skills in `.claude/skills/` eventually belong.

## The boundary that does not move

`dsh` may draft, run tools, and show a diff. `journal.commit_operation` is what
makes a change real. One parser, one scorer, one evidence store. A harness that
could settle a mark or release a key would be the second authority the whole
architecture exists to prevent.

## How to not waste the budget

Measured this session, not guessed:

1. **Context is the bill.** The 5.1B run was 99.24% cache-hit input re-reading a
   122k prompt. Output was 0.32%. Keep the standing prompt small.
2. **Model choice, 81x.** On 2026-08-11 the `reasonix` key spent $11.34 and the
   `coding` key spent $0.14 on the same day's work. Use a non-reasoning model
   for mechanical work.
3. **A test is cheaper than an explanation.** Every bug this session became a
   guard, and two of those guards were proven by deleting the fix and watching
   the suite fail. Do that.
4. **End every turn with something openable.** Twelve phases closed without
   Weibao seeing output, which is why 5.1B read as nothing. Every correction
   this session came from him looking at a rendered file.

## Housekeeping

- `main` is **29 commits ahead of `origin/main`**. Push when convenient.
- `scripts/preflight.py` and `tests/preflight_roundtrip.py` are untracked, from
  the Codex night run. They are a CI-gate mirror and look useful. Not mine to
  commit.
- A concurrent Codex track commits into this same tree (four `docs(14C)` commits
  landed mid-session). **Always use pathspec-limited commits**:
  `git commit -- <paths>`, never a bare `git commit -a`.
- `tests/journal_roundtrip.py` fails in `check_lock_busy` with a Windows
  `msvcrt` unlock error. Pre-existing, confirmed by stashing every change.
- `tests/lesson_roundtrip.py` fails on a pre-13.5 golden fixture drift. Also
  pre-existing, also confirmed the same way.

## The thing nobody has done yet

Phase 13.9-03 is still open. It requires Weibao to put one real EMT bank through
`itembank serve` and sit it. It is `autonomous: false` because no model can do
it. Twelve phases are marked complete and the product has never been used on
real material. If a choice ever comes up between another architecture phase and
closing 13.9, close 13.9.
