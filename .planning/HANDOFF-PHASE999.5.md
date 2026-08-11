# Handoff — Phase 999.5 (Agent onboarding & skill library) closed

- **Created:** 2026-08-11
- **Phase:** 999.5 — agent-onboarding-skill-library
- **Status:** CLOSED (plan 999.5-01 EXECUTED, `Status: complete`)
- **Handing off to:** later phases that change the CLI or session protocol — the
  skills must be re-synced to the shipped surface (ROADMAP 999.5 maintenance
  obligation), and the mirror/CI convention keeps that mechanical.

---

## 1. What phase 999.5 delivered

- **Skills synced to the shipped command surface** in both `.agents/skills/`
  and `.claude/skills/` (byte-identical): `guiding-questions` gained the
  tier-gated hint ladder (`hint --session s.json [--retry]`, D-09/D-12),
  `rubric-review` (D-25, `pending`-token rule), and the inspectable `select`
  preview (Phase 7, `--explain`); `curriculum-design` gained the on-demand
  `coverage` map (D-12) tied to the `## SOURCES` registry; `author-bank` gained
  the `guard .` ship gate and the `seed` one-accept drafting loop (D-07/D-08).
- **Five-skill set completed** — the `ocr` playbook (previously missing from
  both README and AGENTS.md tables) now ships in both trees with its runtime
  (`scripts/ocr.py`, `scripts/ocr_lib.py`, `scripts/ocr_mcp.py`), a local
  Ollama vision bridge for text-only models.
- **No machine-specific config ships.** `reasonix.toml` (permissions grant,
  sandbox mirror, OCR plugin — all absolute paths to one machine) is removed
  from version control and gitignored; the portable `reasonix.toml.example`
  ships in its place stating Reasonix needs no config for this repo
  (auto-discovers `.agents/skills/` as a convention root).
- **Per-tool discovery documented** in README.md and AGENTS.md: Claude Code →
  `.claude/skills/`; Codex / Gemini CLI / Cursor / GitHub Copilot / agents.md
  readers → `.agents/skills/`; Reasonix → `.agents/skills/` convention root;
  anything else → point the skill root at `.agents/skills/`.
- **CI enforces the convention** (`.github/workflows/ci.yml`): `diff -rq
  .agents/skills .claude/skills` fails on mirror drift, and a path-leak grep
  fails on a machine-specific path (`C:/Users`, `C:\Users`, `/Users/wayba`,
  `wayba`) in agent docs/config.

## 2. Verification (re-run at close, 2026-08-11)

- `diff -rq .agents/skills .claude/skills` — **clean** (empty, exit 0).
- `python tests/*_roundtrip.py` — **25/25 isolated roundtrips pass**:
  protocol, agent, serve, anki_keys, config, day, due, durability, gift_export,
  hint, import, launcher, lesson, model_adapter, model_evidence, model_gate,
  model_surface, presentation, seeding, selection, style, surface, theme,
  update, day_edit.
- Four failures are **environment-caused, not regressions** (the working tree
  carries zero runtime-code changes — this phase touched docs/skills/config
  only):
  - `scoring_roundtrip` / `evidence_roundtrip` — the one-scorer/one-writer
    structural scan walks the repo and counts `runtime.py` / `evidence.py`
    copies inside the in-repo worktrees (`.phase*-wt/`) that parallel phase
    sessions are actively using.
  - `daemon_roundtrip` — another session ran the same test concurrently; both
    create `/tmp/work-*` dirs, so each tripped the other's hostile-path
    directory snapshot.
  - `packaging_roundtrip` — the built Windows sidecar `.exe` cannot handshake
    under WSL2/systemd (known binfmt interop limitation; see
    `.reasonix/REASONIX.md`). `packaging_shell_roundtrip` not runnable in this
    shell for the same reason.
  - All four pass on a clean checkout (CI runs clean).

## 3. What this close commit contains

- `.planning/phases/999.5-agent-onboarding-skill-library/` (PLAN + SUMMARY)
- `.agents/skills/ocr/` + `.claude/skills/ocr/` and `scripts/ocr*.py`
- Modified skill files in both trees (author-bank, curriculum-design,
  guiding-questions)
- README.md, AGENTS.md (999.5 portion only — see §4), `.github/workflows/ci.yml`,
  `.gitignore`
- `reasonix.toml` de-shipped (`git rm --cached`; file stays local and ignored)
- `reasonix.toml.example` (portable template)

## 4. Deferred / left for other sessions (reported, not silently dropped)

- **`.planning/ROADMAP.md`** — the 999.5 session already wrote its entry
  ("**Plans:** 1 plan — 999.5-01 … shipped 2026-08-11") but the file also
  carries phase 08's in-flight changes (3/6→4/6, 08-04 checkbox). ROADMAP is
  claimed by the phase 08 session; the 999.5 entry stays in the working tree
  and should ride the next phase-08 ROADMAP commit. Not staged.
- **`.planning/STATE.md`** — phase 08's state file (`current_phase: 08`); it
  has no 999.5 checkbox to mark and is maintained by the phase 08 session.
  Untouched.
- **`.planning/config.json`, `06-VERIFICATION.md`** — carry another session's
  changes (test_command config; line-ending tweak). Not 999.5. Not staged.
- **AGENTS.md "Reasonix runtime notes"** — appended by a concurrent headless
  session; machine-specific (launcher flags, WSL2 interop, prompt caching,
  contains `wayba` paths) and would fail 999.5's own CI path-leak grep. The
  staged AGENTS.md is the 999.5 portion only; the notes remain in the working
  tree, uncommitted, and belong in `.reasonix/REASONIX.md` (which they already
  reference).

## 5. Follow-ups

- Relocate the AGENTS.md "Reasonix runtime notes" content to
  `.reasonix/REASONIX.md` (machine-local) so the external-user-facing AGENTS.md
  stays path-clean.
- Next phase that changes the CLI or session protocol: re-run the skill
  maintenance loop (ROADMAP 999.5 entry) and let CI's `diff -rq` + path-leak
  steps catch drift.
