# Note: seeding automation and editing source files in place

- **Date:** 2026-08-10
- **Context:** follow-up to the resource inventory (`.planning/notes/RESOURCES.md`).
  Questions answered: (1) can the conversion and the next steps be automated,
  (2) can itembank edit the source files where they live, (3) what else is worth
  considering.
- **Status:** planning note. No code was changed and no real content was copied
  into this repo (`03.2-CONTEXT.md` D-17).

## 1. Can the conversion be automated? Yes -- but the importer is planned, not built.

Phase 3.2 has five ready plans and zero executed. Today there is no
`surfaces/import_anki.py`, no `itembank import` subcommand, and no seeding loop.
What the tool can already do today:

- `itembank lint` the two passing banks (EMT 21 items, CSCI 19 items, both
  0 errors) and `serve`/`study`/`build` them.
- `itembank id-assign` -- the one existing command that writes into a bank in
  place, adding `[ID:]`/`[HASH:]` lines. That is the first automatable
  provenance step for the EMT and CSCI banks.
- `itembank day` with the vault wiring -- reads Anki counts over AnkiConnect,
  renders the plan, and edits the plan/log/notes in place.

The conversion automation is exactly the 03.2 plan stack:

| Plan | Wave | What it automates |
|---|---|---|
| 03.2-01 | 1 | `.apkg` importer: ZIP + zstd + sqlite3 container reader, note-type map with loud per-note refusals, `model.lint()` gate, exhaustive per-note report, `itembank import anki <file> --out <dir>` -- stages candidates, never writes a bank |
| 03.2-02 | 1 | `## SOURCES` registry + `[SRC:]`/`[OBJ:]` resolution with unresolvable-id lint errors; on-demand objective coverage map (never stored) |
| 03.2-03 | 2 | draft -> lint -> retry -> one-item human-accept seeding loop, CLI + daemon route, six-stage locked order, batch UI with cancel, refuse-by-name when no model backend (D-06/07/08/09/10) |
| 03.2-04 | 2 | paraphrase lint over fingerprints only (no source text stored), `style.unsourced_specific`, `[CASE:]`/`[PREREQ:]` grammar + cycle/unresolvable detection |
| 03.2-05 | 3 | verify phase: `itembank guard` glob extension (real banks stay out of this repo) + calibration corpus evidence for Phase 3.1 style warnings |

So the honest automation answer: the machine is ready, the plans are ready, and
the first real conversion can run only after 03.2-01 + 03.2-02 land. The
human gate (accept one item at a time) is deliberately not automatable -- that
is the phase's contract, not a limitation.

## 2. Can itembank edit the source files where they are? Yes, and it already does.

Three facts from the code:

1. **The day surface edits vault files in place today.** `POST /day/<stem>/open`
   hands a lane's notes file to the OS editor and `POST /day/<stem>/edit`
   (plus the `--edit --set --revision` CLI twin) edits plan cells in place
   with an optimistic-concurrency guard (mtime + size + revision; a save is
   refused if the file changed on disk since it was loaded). Paths resolve
   through `lanes.md`; absolute paths are deliberately supported by
   `resolve_notes()` and `lane_files()`.
2. **`cmd_id_assign` writes into bank files in place** -- the only command that
   mutates a bank, adding `[ID:]`/`[HASH:]` with global uniqueness enforcement.
3. **Phase 3.2's accept loop will write into the bank files in the vault**, not
   into this repo. That is D-17 by design: the real corpus lives beside the
   private bank outside the repository, and `itembank guard` keeps it out of CI.
   The wiring already points at the vault; nothing about "editing where they
   are" requires moving content.

What does not exist yet: a general in-place bank editor (item add/edit UI) and
the one-item-per-commit reversibility. Both are later phases -- the accept loop
in 03.2-03 and reversibility in Phase 11. D-19 (two-file lesson layout) exists
specifically so item writes and prose writes never contend for one file, which
is what keeps one-action reversibility possible later.

## 3. More to consider (beyond the plan text)

The inventory surfaced things the plans leave as open decisions or that need a
stated route before execution:

1. **The machine's decks are mostly not `.apkg`.** Real artifacts: live
   `collection.anki2` (legacy plain SQLite -- no zstd on this profile),
   `backups/*.colpkg`, `Downloads/_study_exports/*.txt` (Anki text), and one
   `mandarin_capture.apkg`. The importer reads `.apkg` containers. Decide the
   path for each: export `.apkg` from Anki, read `collection.anki2`/`.colpkg`
   directly through the same container reader, or accept Anki text. Recommend:
   the container reader accepts the collection file and `.colpkg` as first-class
   inputs; Anki text stays a documented non-goal (lossy note-type metadata) or a
   later companion reader.
2. **Basic -> mc is a fidelity question, not a mechanical one.** Basic cards are
   Q/A with no options; mapping to `mc` means authoring distractors (model work
   + human accept), while mapping to `short` is faithful and cheap but never
   auto-graded. Cloze -> cloze/short is mechanical. Image Occlusion and Mandarin
   Recognition refuse loudly (D-04). The plan leaves the table to the executor;
   write the chosen mapping into 03.2-01 task 2 with a per-type rationale.
3. **Overlap with the existing banks.** The EMT/CSCI banks and the decks were
   authored from the same sources (AAOS 12e, Exam1Prep). Conversion without
   objective-level dedupe doubles the corpus. Use `[OBJ: subject/path]` as the
   dedupe key and the on-demand coverage map to show the overlap before accept.
4. **Math has no bank.** `MATH::1400` (41 notes) + `Math_1400_Anki_Capture.md`
   are the only Math items; converting the deck is the cheapest first Math
   content. Everything else is notes-to-bank authoring via 03.2-03.
5. **Concurrency is real, not theoretical.** Obsidian, obsidian-git auto-backup,
   agents, and the day surface all touch the same vault files. Any new in-place
   writer (import staging, accept loop) must reuse the same
   optimistic-concurrency discipline, and the one-writing-home rule (M1)
   applies. The vault is a git repo, so per-item commits there give Phase 11
   reversibility without waiting for it.
6. **Guard before anything moves.** Extend `itembank guard` globs
   (`BANK_FILE_HINTS`) per 03.2-05 before the first staged candidates exist, so
   a stray real bank can never land in this repo's CI.
7. **Degrade, never block.** Import, lint, `[SRC:]` resolution, and the coverage
   map must work with no model backend; only seeding refuses by name (D-10).
   The conversion pipeline should be runnable on a laptop with Anki closed and
   no API key.
8. **No source text on disk.** Paraphrase lint uses fingerprints only (D-13).
   This matters here specifically: the primary EMT source is a purchased AAOS
   textbook, so storing source text would be a copyright and residency problem
   to unwind.
9. **Batch UX is the contract.** ~9 model calls per lesson, staged progress,
   cancel, nothing written on cancel (D-09). The conversion of a 50-note deck
   is a batch job, and the UI must say so rather than pretending to chat.

## 4. Recommended next-actions order

1. (Optional, reversible, ~seconds) run `itembank id-assign` on the EMT and
   CSCI banks in the vault -- unblocks evidence recording and starts the
   `[ID:]` trail; commit the vault first so it is reversible.
2. Execute 03.2-01 (importer) with the container-input decision from 3.1
   resolved, then 03.2-02 (provenance registry).
3. Backfill provenance on the two passing banks and the Anki capture files:
   `## SOURCES` entries naming the textbook/source and the capture file as the
   `[SRC:]` target; subject-prefixed `[OBJ:]` on every item.
4. Execute 03.2-03 (accept loop), then convert the CSCI and EMT decks first
   (dedupe against the banks), then `MATH::1400`.
5. Execute 03.2-04 (paraphrase + structural checks) and 03.2-05 (guard +
   calibration evidence).
6. Leave Sec+ out until its duplicate-numbering errors are fixed.

## 5. What phase each resource is in

The roadmap state that matters: Phase 3 (lesson format) is 6/6 complete and
marked in progress; Phase 3.1 (rich blocks, glossary, style) is 3/7 in
progress; Phase 3.2 is 0/TBD not started; Phase 4 is 6/6 complete
(parallel-eligible with 3); Phase 5+ is planned but gated on 3.2 landing
first. Within that:

| Resource group | Phase home | Consumed by | Status / gate |
|---|---|---|---|
| EMT + CSCI exam banks | Phase 3.2 (provenance), Phase 4/9 (surface) | 4, 5, 6, 7, 9, 10, 11 | consumable today; evidence blocked on `id-assign`; provenance blocked on 03.2-02 |
| Math 1400 content (deck 41n, capture, notes) | Phase 3.2 (first Math items), Phase 9 (integration) | 9, 10, 11 | thinnest lane: no bank, no LESSON sections; Phase 9's math leg depends on it |
| EMT/CSCI notes + chapters + blocks | Phase 3 (done), Phase 3.1 (in progress) | 3.1 style lint, 6.2 executable textbook loop, 9 | lesson conversion open now against Phase 3 grammar; mass conversion before 3.1's style contract lands risks style rework |
| Anki decks + captures + txt exports | Phase 3.2 import | 3.2 accept loop, 10 (due shown apart) | importer is planned, not built; the reverse direction (`itembank export` bank -> Anki) already exists in Phase 2.1 |
| Textbooks (AAOS, Mistovich, Rosen, Levin, BoP, TLCL) | Phase 3.2 `[SRC:]` sources | any authored bank/lesson | always outside the repo; cited, never stored |
| Status_Dashboard + lanes.md + daily_log | Phase 2 (complete) | day surface today | live and linting clean; vault evidence log not migrated yet |
| wl-course-headstart mirrors, 100 Days of Code | Phase 3.1/9 lesson material | 6.2, 9 | demoted to optional in the plan; mirrors need ownership notes |
| Sec+ bank + decks | none (out of scope subjects) | - | renumber (366 errors) before any future use; not a roadmap subject |

## 6. Sequencing tensions worth naming

1. **3.1 and 3.2 calibrate each other, so 3.2 is not purely downstream.**
   Phase 3.1's style warnings ship only with a recorded false-positive rate
   measured against the Phase 3.2 corpus (D-18). 3.1 is mid-flight while 3.2
   has not started, and the corpus already exists in the vault -- the inventory
   is the unblocked half of that loop. The corpus work can proceed in the vault
   now (annotate sources, collect style evidence) even before the 03.2 plans
   execute; only the tooling (registry, paraphrase lint, calibration run) waits.
2. **The banks are already Phase-4/9-ready, but their evidence is gated on
   `id-assign`.** Nothing else blocks serving them and recording responses
   today. That matters because Phase 10 (retention, pacing, trends) reads
   accumulated evidence -- the earlier real sittings start, the more Phase 10
   has to work with.
3. **Math is the resource risk for Phase 9.** The subject-invariant loop needs
   all three legs (EMT prose, Math LaTeX, CS code). Math has 41 Anki notes and
   notes but no bank and no lesson sections. Converting the MATH::1400 deck is
   the cheapest first Math content and should be the first import after
   EMT/CSCI, not the last.
4. **Lesson conversion and item seeding must not contend.** Notes-to-LESSON
   prose is Phase 3/3.1 work; Anki-to-items is 3.2 work. D-19's two-file layout
   is the rule that keeps them from fighting over one file, and it is also why
   Phase 3.1's lesson format should be applied to the notes before (or while)
   items are seeded from the decks.
5. **The vault's evidence history is unmigrated.** `itembank day` reports
   "no _evidence/evidence.jsonl; run itembank migrate" -- the Phase 1
   migration command exists and can fold the existing daily_log history into
   the evidence log today, before Phase 10 needs trends. That is automation
   available now, not a plan item.
6. **Sec+ stays out by phase, not just by quality.** Its duplicate-numbering
   errors block lint, and its subject is outside the roadmap's three lanes, so
   it has no phase home until the user says otherwise. Do not let conversion
   effort flow to it ahead of the three target subjects.
