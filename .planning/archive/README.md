# Planning archive

Historical operator files, moved here on 2026-09-03 so that the live planning
root holds only documents an agent should read. Nothing was deleted; every file
keeps its git history (`git log --follow`). Older records that cite the old
paths are left as written, and this index is the map.

Rule for this directory: read a file here only when investigating how a past
decision was reached. Nothing here states current status. Current status lives
in `.planning/STATE.md` (current position), `.planning/ROADMAP.md` (checklist
and subphase table), and the per-phase `*-FREEZE.md` and `*-GATES.md` files.

| Was | Now | Why archived |
|---|---|---|
| `.planning/PROMPT-*.md` (12 files) | `archive/PROMPT-*.md` | One-shot operator prompts for sessions that have run; several name a Windows machine that is gone |
| `.planning/NEXT-2026-08-27.md` | `archive/NEXT-2026-08-27.md` | Superseded by `NEXT-2026-08-31.md`, which is live |
| `.planning/DECISIONS-PRE-14A-2026-08-14.md` | `archive/` | Its three decisions are resolved; cited by 14B and 15A phase details as history |
| `.planning/DECISIONS-17A04-DRIVER-2026-08-25.md` | `archive/` | Resolved; 17A-04 Task 1 ran 2026-08-31 |
| `.planning/DECISIONS-PACED-LESSON-2026-08-28.md` | `archive/` | Its eight decisions are closed and Phase 16D shipped |
| `.planning/POST-RESEARCH-PROMPTS-2026-08-09.md`, `-10.md` | `archive/` | Inputs to the August research waves, all run |
| `.planning/RESEARCH-BRIEF-learning-platform-2026-08-09.md`, `RESEARCH-BRIEF-2-lesson-styles-2026-08-10.md` | `archive/` | Briefs for completed research; the outputs live in `.planning/research/` |
| `.planning/OX-RUNBOOK-finish-the-sitting-2026-08-25.md` | `archive/` | The sitting queue finished 2026-08-25 |
| `.planning/RULE-AUDIT-2026-08-15.md`, `RULE-AUDIT-PLAN-2026-08-15.md`, `RULE-AUDIT-ROADMAP-DELTA-2026-08-15.md` | `archive/` | A completed audit whose adopted rules now live in `AGENT-WORKFLOW.md` |
| `.planning/BLOCKER-AUDIT-2026-08-08.md`, `BRANCH-ARCHIVE-2026-08-12.md`, `tmp-decisions-06-01.txt` | `archive/` | v1.0-era bookkeeping |
| `.planning/HANDOFF-*.md` except `HANDOFF-MAC-2026-08-21.md`, and `HANDOFF.json` | `archive/handoffs/` | Session handoffs for phases that closed; the JSON still said phase 03.1 was paused |
| repo root `HANDOFF-PHASE*.md` (9 files) | `archive/handoffs/` | Same, for phases 3 through 10 and 999.4 |
| `.planning/STATE.md` log entries dated 2026-08-30 and earlier, plus its retired sections | `archive/STATE-LOG-through-2026-08-30.md` | The live file keeps the current position and the two most recent days |

Still live at the planning root, deliberately: `NEXT-2026-08-31.md` (the owed
human reviews), `DECISIONS-14B-DRIVER-2026-08-27.md` and
`DECISIONS-12.6-REMAINING-2026-08-14.md` (partly open),
`HANDOFF-MAC-2026-08-21.md` (machine setup), `READINESS-AUDIT-14A.md` and
`AUDIT-REPORT-14A-2026-08-14.md` (gates A9 and A10 are still cited),
`PROPOSAL-WORKSPACE-2026-08-27.md` (accepted in principle, unscheduled).
