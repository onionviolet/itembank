# Prompt: clear the human checkpoints that are clearable today

Paste this whole file as the opening message of a fresh session on
`itembank` (`C:\Users\wayba\Downloads\CTF\itembank`, branch `main`). It is
self-contained. Read `.claude/CLAUDE.md`, `.planning/PLANNING-DIRECTIVES.md`,
and `.planning/STATE.md` (the 2026-08-17 plan-the-rest session record) before
acting. Weibao is present and interactive in this session; that is the point
of it.

Standing rules: no em dash characters in anything you write; every commit is
pathspec-limited (`git commit -- <paths>`); do not write to
`scripts/preflight.py`, `tests/preflight_roundtrip.py`, `AGENTS.md`,
`.gitattributes`, or anything under `fixtures/` if `git status` shows them
dirty (a concurrent agent's in-flight work); an unanswered question stays
open, never silently defaulted.

## What this session can and cannot clear

Can clear today, no execution needed: the 13.5 human-verify tail (Part 1)
and two standing decisions (Part 2). Can clear only if execution is safe
right now: the 17A direction preview (Part 3). Cannot clear today, do not
attempt: the 17B-03 rollup default pick, the 17A-04 and 17B-04 A11Y and
freeze acceptances, the 17C-01 audit acceptance, and the Phase 18
second-person cold install; each needs its phase executed first.

## Part 1: the 13.5 human-verify tail (shipped surfaces, ready now)

Procedures live in
`.planning/phases/13.5-reading-teaching-surface-quality-pass/13.5-GATES.md`.
Launch the daemon (`python itembank.py daemon` from the repo, or the route
the GATES file names) and walk Weibao through each remaining row, one at a
time, reading him the exact steps and recording his observation verbatim:

1. Screen-reader announcement behavior (never agent-certifiable). He needs
   Narrator or NVDA running; guide the keystrokes.
2. Gloss bottom-sheet painted geometry on a touch device or narrow displayed
   pane.
3. The script-free and truly network-free ladder walkthrough (disable JS,
   unplug network, confirm reading, sitting, and scoring still work).
4. The perceptual font-face comparison.
5. Optional: a real 200 percent zoom rasterization spot check.

Record each outcome in 13.5-GATES.md under its row, dated, named to Weibao.
If all pass, update the 13.5 row wording in `ROADMAP.md` (the
"13.5 remaining human-verify tail" backlog row) and the 13.5-VERIFICATION
status if its criteria are now met. Commit with a pathspec limited to those
files. If any row fails, record the defect with mechanism observed, 13.5
D1/D2 precedent, and do not fix it in this session.

## Part 2: two decisions that need no execution

**2a. Code signing (V2-DEL-01, 18-CONTEXT D-02).** Gather one real, dated
Windows Authenticode OV certificate quote (vendor named). Present Weibao
exactly three options: (1) buy the OV certificate at the quoted price per
year; (2) Apple Developer Program at 99 USD per year, only relevant if a
macOS artifact ever ships, currently a deferral; (3) ship unsigned for v1
with SmartScreen and Gatekeeper workarounds documented where the user hits
them, recommended default, revisit on wider distribution. Record his answer,
the quote, and the date in
`.planning/phases/18-external-user-v1/18-DECISIONS.md` (create it), and add
a one-line note to 18-01-PLAN.md Task 3 that the checkpoint was pre-answered
on this date and the executor records rather than re-asks. If he declines to
decide, leave the checkpoint live and say so in 18-DECISIONS.md.

**2b. PyMuPDF AGPL (IDEA-LEDGER IL-20260815-07, 2026-08-17 note).** Explain
in two sentences: pdfplumber is the chosen PDF path; PyMuPDF is technically
stronger but AGPL-licensed, and the supply-chain policy routes copyleft to
an explicit decision. Ask whether he (a) pre-declines AGPL, keeping
pdfplumber unconditionally, or (b) leaves the question open until real
extraction quality on his sources is known, recommended default. Record the
answer as an additive dated note under IL-20260815-07 in
`.planning/IDEA-LEDGER.md`.

## Part 3: the three rendered prototypes (only if execution is safe)

The three directions (Structured Studio, Quiet Workbench, Guided Canvas) do
not exist until plan 17A-01 executes; it builds the synthetic tracer and
serves the same flow in all three. Precondition checks, all must hold or
skip this part and say why:

1. `git status` shows `fixtures/` clean (17A-01 writes
   `fixtures/visual_system_flow.json`; skip if the concurrent agent still
   has fixtures/ dirty).
2. No other agent is mid-execution on plans touching `server.py` or
   `surfaces/` (check STATE.md and recent commits).

If safe, execute 17A-01 properly as its wave-1 plan (it is `depends_on: []`
and autonomous): follow
`.planning/phases/17A-visual-system-component-foundation/17A-01-PLAN.md` to
the letter, run its verify commands, write 17A-01-SUMMARY.md per the
template, commit pathspec-limited. Then serve the tracer and show Weibao the
same flow in all three directions at 1280, 768, and 375 widths, capturing
screenshots to `.planning/phases/17A-visual-system-component-foundation/
preview/` (repo-safe: synthetic content only).

Weibao may record a provisional preference, dated, in a new
`17A-DIRECTION-PREVIEW.md` beside the plans. Make explicit to him and in
the file: the binding pick is still the 17A-02 Task 1 checkpoint, which
also carries the hypothesis default (Structured Studio structure, Quiet
Workbench density, bounded Guided Canvas accents, per 17A-CONTEXT D-05);
this preview only lets that checkpoint be answered fast when it arrives.
Do not run 17A-02, do not freeze tokens, do not migrate the day route.

## Exit report

End with: which 13.5 rows passed or failed, both decision outcomes (or
their explicit deferrals), whether Part 3 ran and what Weibao's provisional
preference was, every file changed with its commit, and the remaining human
checkpoints with the execution milestone each one waits on.
