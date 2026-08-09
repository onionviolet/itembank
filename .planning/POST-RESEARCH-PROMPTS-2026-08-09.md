# Post-Research Prompt Pack — 2026-08-09

Copy-paste prompts to run **after** the research pass lands in
`.planning/research/2026-08-09-*.md` and the Findings section is appended to
`.planning/RESEARCH-BRIEF-learning-platform-2026-08-09.md`.

Run them in order. Each is one session. Per the execution split recorded in the
brief: **Claude plans here; DeepSeek V4 runs `/gsd-execute-phase`. Never execute
from a planning session.**

Ground truth before starting any prompt: run `/gsd-progress` and trust it over
this file — phase states move.

---

## 0. State check (every session, first)

```text
/gsd-progress
```

Confirm which of Phases 2.1, 3, 4, 5, 6, 6.1, 7, 8, 9, 10, 11 are actually
complete before touching their plans. The roadmap checkboxes lag; Phase 4's
token system and shell are implemented even though the roadmap box is unchecked.

---

## 1. Roadmap surgery — insert the new phases, rescope the old ones

```text
/gsd-phase Apply the research conclusions in
.planning/RESEARCH-BRIEF-learning-platform-2026-08-09.md section 7 (Findings)
and .planning/research/2026-08-09-*.md to ROADMAP.md:

1. INSERT Phase 03.1 "Lesson Rich Blocks, Glossary & Style" — D1 [[term]] hover
   glossary (## TERMS), D2 [!KEY] memorizable blocks with Anki export ids, D3
   LESSON-STYLE.md + lint rules, callout/figure/type-scale rendering on Phase 4
   tokens. Depends on Phase 3, Phase 4. Use the format grammar from
   .planning/research/2026-08-09-differentiators-d1-d2-d3.md verbatim as the
   phase's format contract.
2. INSERT Phase 03.2 "Source Provenance & Extraction Standard" — [SRC:] tag
   grammar, objective coverage map format, paraphrase-not-transcribe lint, per
   .planning/research/2026-08-09-extraction-subjects-bilingual.md. Shrinks
   Phase 11 accordingly; update Phase 11's description and dependencies.
3. INSERT Phase 06.2 "Executable Textbook Loop" — prose → inline check → spaced
   re-exposure, per the landscape research. Depends on Phase 5, Phase 6, 03.1.
4. UPDATE the descriptions/success criteria of Phases 5, 6, 7, 8, 9, 10, 11 with
   their absorbed findings per brief section 5's embedding table and the
   Findings section. Do not renumber anything; additive edits only.
5. Record the packaging decision from
   .planning/research/2026-08-09-packaging.md as the Phase 2.1/packaging
   direction (keep-Python-sidecar vs replace — whichever the Findings section
   adopted), as an OPEN decision if Weibao has not ruled.
```

---

## 2. Re-plan phases that already have artifacts (do NOT regenerate from scratch)

These phases have PLAN/SPEC files on disk that predate the research. For each,
reconcile rather than rewrite; keep LOCKED decisions unless the Findings section
explicitly supersedes them.

### 2a. Phase 6.1 (plans 01–03 + UI-SPEC + VALIDATION exist)

```text
/gsd-plan-phase 6.1 — reconcile the existing 06.1-01/02/03 plans with
.planning/research/2026-08-09-extraction-subjects-bilingual.md (Math
manipulables verdict: Desmos/GeoGebra vs our SVG protocol) and the visual
direction in .planning/research/2026-08-09-visual-design.md. Preserve the
approved 06.1-UI-SPEC.md accessibility contract; change plans only where a
research finding names a cheaper or better mechanism, and record each change
with a reason.
```

### 2b. Phase 8 (plans 01–06 + 08-AI-SPEC + 08-UI-SPEC + VALIDATION exist)

```text
/gsd-plan-phase 8 — audit the six existing 08-*-PLAN.md files against the
tutor-refusal copy and hint-pacing findings in
.planning/research/2026-08-09-landscape-widening.md and the degraded-model UX
findings (B14) in .planning/research/2026-08-09-blind-spots.md. The adapter
interface and tier-gate mechanics are LOCKED; only learner-facing copy,
provenance presentation, and generated-hint surfaces may change. Update
08-UI-SPEC.md copy tables if the research produced better refusal wording.
```

### 2c. Phase 9 (plans 01–05 + RESEARCH.md exist)

```text
/gsd-plan-phase 9 — reconcile the existing 09-*-PLAN.md files with the
per-subject findings in
.planning/research/2026-08-09-extraction-subjects-bilingual.md (EMT scenario
item needs, Math answer-equivalence verdict, CS check-type execution verdict)
and any relaxed-constraint opportunities (dependencies now allowed — e.g. sympy
if the research recommended it). Additive format changes only; one scorer.
```

### 2d. Phases 10 and 11 (RESEARCH.md exists, no plans yet)

```text
/gsd-plan-phase 10 — plan with FSRS as the scheduler baseline, D2 [!KEY]
memorizables entering the queue (evidence semantics from
2026-08-09-differentiators-d1-d2-d3.md), the SRS-UX findings from
2026-08-09-landscape-widening.md, and the anti-punitive pacing rules already
LOCKED in UI-SPEC.md.
```

```text
/gsd-plan-phase 11 — plan against the shrunk scope after 03.2 exists:
LESSON-STYLE.md enforcement, coverage audit consuming 03.2's map, cold-start
authoring pull-forward per B1 findings in 2026-08-09-blind-spots.md.
```

### 2e. Phases 5, 6, 7 (no plans yet — plan fresh, research-informed)

```text
/gsd-ui-phase 5    then    /gsd-plan-phase 5
— editor choice and runnable-block presentation per
2026-08-09-lesson-display-editor.md (Q2 recommendation is binding unless
overturned with a recorded reason).
```

```text
/gsd-ui-phase 6    then    /gsd-plan-phase 6
— hint/refusal UX copy per 2026-08-09-landscape-widening.md; state machine in
UI-SPEC.md section 5A is LOCKED.
```

```text
/gsd-plan-phase 7 — selection engine; absorb sequencing-engine findings
(Math Academy / ALEKS patterns) from 2026-08-09-landscape-widening.md; trace
interface per UI-SPEC gate is UPSTREAM-CONTRACT.
```

---

## 3. UI-SPEC revision — adopt the visual direction

```text
/gsd-ui-phase — revise .planning/UI-SPEC.md section 7 to adopt the visual
direction proposed in .planning/research/2026-08-09-visual-design.md: extend
the Phase 4 token set (do not replace surfaces/theme.py as the single palette
source), record the distinctive move, and add any vendored-typeface decision as
a dated, licensed asset note. Re-run the checker sign-off list. All
accessibility gates and the copywriting contract stay LOCKED.
```

---

## 4. Blind-spot roadmap items (B1/B2/B3 and any new inserts)

```text
/gsd-phase Apply the B1/B2/B3 verdicts from
.planning/research/2026-08-09-blind-spots.md: if B1 cold start demands a
pull-forward, insert the thin authoring/import phase where the research says;
add B2 mobile and B3 audio as phases or dated backlog entries with the
research's cost numbers attached; append any newly identified blind spots to
brief section 3.5 with owners.
```

---

## 5. Documentation sync

- `.claude/CLAUDE.md` — **already amended 2026-08-09** (constraint relaxation
  note in Constraints + Technology Stack). Re-check after roadmap surgery in
  case phase renumbering invalidates references.
- Update the stale memory note if the packaging decision gets ruled on by
  Weibao.

---

## 6. Stop line

After the prompts above, planning is done. Hand off to DeepSeek V4 for
`/gsd-execute-phase`, sequentially (fork-base guard forces sequential runs
here). Do not execute from the planning session.
