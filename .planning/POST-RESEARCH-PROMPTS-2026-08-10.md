# Prompt Pack — 2026-08-10 (supersedes the 2026-08-09 pack's §1)

The 2026-08-09 pack's §1 (roadmap surgery) is **done** — five phases inserted, eight
updated. Its §2–§6 still stand and are folded into the sequence below.

Read `.planning/PLANNING-DIRECTIVES.md` first, every session. Run `/gsd-progress`
before anything and trust it over this file.

---

## Step 0 — the round-two research (do this first)

> **Status 2026-08-10: research DONE.** All five slices landed (R1, R2, R3, R4, R5),
> run as five concurrent agents. Five artifacts in `.planning/research/2026-08-10-*.md`;
> verdicts, cross-slice reconciliations, four new open rulings and the
> could-not-determine list are in §4 of the brief. The `/gsd-explore` prompt below has
> been executed and must not be re-run.
>
> **NEXT ACTION: the `/gsd-phase` fold below.** Nothing else in this pack has started.

```text
/gsd-explore Run the research pass specified in
.planning/RESEARCH-BRIEF-2-lesson-styles-2026-08-10.md — answer every question in
its section 2 (R1.1-R1.7 lesson style registry including R1.1a's take-this/fix-that
pass per style, R2.1-R2.3 style enforcement, R3.1-R3.5 round-one loose threads,
R4.1-R4.5 the scoring boundary between deterministic verdicts and model suggestions,
R5.1-R5.5 whether lesson prose and items belong in one file or two) under the rules
in its section 3. R4 carries a hard constraint: no finding may propose a model
deciding correctness. Write durable
artifacts to .planning/research/2026-08-10-*.md, then append verdicts, phase
assignments and open rulings to section 4 of the brief, mirroring the shape of
round one's section 7.
```

Then fold the verdicts in:

```text
/gsd-phase Apply the section 4 findings of
.planning/RESEARCH-BRIEF-2-lesson-styles-2026-08-10.md to ROADMAP.md per its
section 5 embedding table. Additive edits only, no renumbering. Phase 3.1 criteria
3a/3b get their real specification; record anything still unruled as an OPEN
decision on the phase it blocks.
```

---

## Step 1 — per-phase chains, in roadmap order

Each phase: **discuss → ui (if it has a surface) → plan**. Chains for different
phases are independent and can run in separate sessions. Phases with existing
artifacts get reconciled, never regenerated.

**UI state as of 2026-08-10** — check this column before running `/gsd-ui-phase`, it
is the most commonly wasted step. The global `.planning/UI-SPEC.md` (487 lines, 14
sections, checker-signed) already exists and binds on every phase. Ten per-phase
UI-SPECs exist: 02, 02.1, 03, 04, 05, 06.1, 08, 09, 10, 11.

| # | Phase | Chain | UI-SPEC | Notes |
|---|---|---|---|---|
| 1 | **3.2** Seeding, Import & Provenance | discuss → plan | n/a — CLI/import only | **Critical path.** Everything after Phase 5 is judged against the content this seeds |
| 2 | **3.1** Lesson Rich Blocks & Styles | discuss → **ui (new)** → plan | **missing** | The biggest UI gap: gloss popovers, `[!KEY]` blocks, the reading layout, print CSS, and whatever the style registry needs. Blocked on Step 0 for the registry only |
| 3 | **5** Check Item Type & Code Editor | discuss → **ui (revise)** → plan | exists | Revise only if ruling 5 puts CM6 in the learner-facing editor; otherwise the existing spec stands |
| 4 | **6** Hint Ladder & Feedback Modes | discuss → **ui (new)** → plan | **missing** | Second-biggest gap. The visible-lock card is the differentiator's whole UI surface. B15 latency/duration fields are non-deferrable |
| 5 | **6.1** Visual Assessment Protocol | plan (reconcile only) | exists | 3 plans + UI-SPEC + VALIDATION already exist |
| 6 | **6.2** Executable Textbook Loop | discuss → **ui (new)** → plan | **missing** | Gated reading surface; should reuse 3.1's spec rather than invent a second reading layout |
| 7 | **7** Selection Engine | discuss → **ui (new, small)** → plan | **missing** | Mostly headless, but `select --explain` and the "why this item" trace are learner-facing |
| 8 | **8** Model Adapter & Tier Gate | plan (audit only) | exists | Adapter and tier mechanics LOCKED; only copy, provenance and generated-hint surfaces may change |
| 9 | **9** Subject-Invariant Loop | plan (reconcile only) | exists | Add `## SCENARIO` staged reveal, numeric equivalence |
| 10 | **9.1** Audio Drill Export | discuss → plan | n/a — export only | Small |
| 11 | **10** Retention, Pacing & Trends | discuss → plan | exists | FSRS baseline replayed from the log |
| 12 | **11** Authoring Loop & Auditor | discuss → plan | exists | Shrunk — seeding moved to 3.2 |
| 13 | **13** Desktop Packaging | discuss → **ui (new, small)** → plan | **missing** | Window chrome, installer, and first-launch only. Not a redesign |

The reconcile-don't-regenerate prompts for phases 6.1, 8, 9, 10 and 11 are written
out in `.planning/POST-RESEARCH-PROMPTS-2026-08-09.md` §2 and still apply verbatim.

**Do not regenerate an existing UI-SPEC.** Where one exists, reconcile it against new
findings and record each change with a reason. Accessibility gates and the
copywriting contract are LOCKED everywhere.

---

## Step 2 — global UI-SPEC revision (do before the new per-phase UI-SPECs)

> **Status 2026-08-10: DONE.** `.planning/UI-SPEC.md` went 487 → 654 lines, section 7
> only, no renumbering. New §7.1 tokens, §7.2 `--pending` LOCKED rule, §7.3 the
> distinctive move, §7.4 typeface asset note on the KaTeX precedent, §7.5 checker
> sign-off re-run. Font *vendoring* remains gated on ruling 1; no font file was
> downloaded. **New constraint discovered:** both faces carry OFL Reserved Font Names
> (Source Serif's "Source"; iA Writer Quattro's "iA Writer" and "Plex"), so a subset
> build must be renamed or shipped unmodified — this binds ruling 1.
> The prompt below has been executed and must not be re-run.

Still pending from the 2026-08-09 pack §3. Run it **before** writing the five missing
per-phase UI-SPECs, so they inherit the adopted direction instead of being written
against §7 and revised twice.

```text
/gsd-ui-phase — revise .planning/UI-SPEC.md section 7 to adopt the visual direction
in .planning/research/2026-08-09-visual-design.md: extend the Phase 4 token set
(surfaces/theme.py stays the single palette source, never replaced), record the
distinctive move, and add the vendored-typeface decision as a dated, licensed asset
note following the KaTeX precedent. Re-run the checker sign-off list. All
accessibility gates and the copywriting contract stay LOCKED.
```

Blocked on **ruling 1** for the font vendoring specifically. The token extensions
(`--font-paper/--font-ledger/--font-chrome/--font-code`, `text-lesson 18/1.65`,
`measure-prose 66ch`, and the missing `--unknown/--pending/--warn-bg`) do not depend
on that ruling and can land either way — the direction degrades to today's look
exactly when the faces are absent, which is what makes it safe to adopt early.

---

## Step 3 — stop line

Planning is done. Hand off to DeepSeek V4 for `/gsd-execute-phase`, sequentially.
Never execute from a planning session.

---

## Open rulings for Weibao (brief §7.7, plus round two)

| # | Ruling | Blocks |
|---|---|---|
| 1 | Adopt "Paper & Ledger", vendor Source Serif 4 + iA Writer Quattro (OFL)? | 3.1 font task, UI-SPEC §7 |
| 2 | 18px lesson body vs the locked 16px `text-body` | 3.1 |
| 3 | Confirm keep-Python + Tauri sidecar + NSIS, and Phase 13 as the number | 13 |
| 4 | Approve widening/moving 3.2 — the seeding pull-forward | 3.2 (largest change) |
| 5 | CM6 replacing the learner-facing textarea contract, or authoring-only? | 5, 11 |
| 6 | Confirm "The Bottom Up" = Wienand-style runnable-artifact-first | 3.1, 5, 9 |

None of these blocks starting. Each is recorded on the phase it affects.
