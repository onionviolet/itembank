# RESOURCES.md: learning-resource inventory (EMT / Math 1400 / CSCI 1100)

- **Date:** 2026-08-10
- **Context:** Phase 3.2 (Seeding, Import & Provenance) intake. Inventory of
  existing learning resources so the day surface and the seeding loop can start
  from real content instead of synthetic fixtures.
- **Rule honored:** no real bank or lesson content was copied into this repo
  (`03.2-CONTEXT.md` D-17; `itembank guard`). This file is a pointer table.
- **Scan coverage:** `Downloads/CTF` (itembank, weibao-planing, ankictl,
  grimoire, weibao-anki-decks, mythcorp-gen2, obsidian-scroll-memory),
  `Documents/Codex`, `Downloads/Personal` (incl. `wl-course-headstart`, `Notes`),
  `Downloads/School` (Coursework, Math, Continuing_Ed), `Downloads/_study_exports`,
  `Downloads/delete`, and the Anki profile `%APPDATA%\Anki2\User 1`
  (live `collection.anki2` + `backups/*.colpkg`).

## Lint results (banks only; `python itembank.py lint <file>`)

| Bank | Items | Errors | Warnings | Verdict |
|---|---|---|---|---|
| `weibao-planing/02_Skills_Learning/EMT/EMT_Exam_Bank.md` | 21 | 0 | 67 | PASS (exit 0) |
| `weibao-planing/02_Skills_Learning/CSCI_1100/CSCI_1100_Exam_Bank.md` | 19 | 0 | 38 | PASS (exit 0) |
| `weibao-planing/02_Skills_Learning/Cybersecurity/SecPlus/SecPlus_MC_Bank.md` | 388 | 366 | 1770 | FAIL (exit 1) |

Warning categories on the two passing banks: every item lacks an `[ID:]` line
(run `itembank id-assign`), every `OBJECTIVE` lacks a `subject:path` prefix, and
distractors do not state when they WOULD be correct. These are Phase 3.2's exact
provenance gaps (no `[SRC:]`, no `[OBJ:]`, no `## SOURCES`).

The Sec+ bank fails on **duplicate question numbers**: each exam section
restarts numbering at Q1, so the parser sees q1..qN repeated per section (366
errors), plus the same warnings as above. It is outside the three target
subjects but is the largest bank on the machine.

## Inventory

| Path | Subject | Type | Usable-now | What's missing to make it usable |
|---|---|---|---|---|
| `Downloads/CTF/weibao-planing/02_Skills_Learning/EMT/EMT_Exam_Bank.md` | EMT | bank | yes | `[ID:]` via `id-assign`; subject-prefixed `[OBJ:]`; `[SRC:]`/`## SOURCES` provenance; distractor would-be-correct notes (67 warnings) |
| `Downloads/CTF/weibao-planing/02_Skills_Learning/CSCI_1100/CSCI_1100_Exam_Bank.md` | CS | bank | yes | same as EMT bank (38 warnings); `short` items need the Phase 1 marking path |
| `Downloads/CTF/weibao-planing/02_Skills_Learning/Cybersecurity/SecPlus/SecPlus_MC_Bank.md` | Sec+ | bank | no | renumber questions per section (366 errors); then same provenance work. Out of scope for the 3 lanes but largest bank on disk |
| `%APPDATA%/Anki2/User 1/collection.anki2` (decks `EMT::AAOS-12e` 53n, `MATH::1400` 41n, `CSCI::1100` 50n, plus Mandarin, Sec+) | EMT/Math/CS (+others) | Anki deck (live) | yes | day surface reads counts via AnkiConnect today; Phase 3.2 .apkg/collection import (plan 03.2-01) is what turns these into linted bank candidates with a per-note report |
| `Downloads/_study_exports/emt_basic.txt`, `emt_cloze.txt`, `csci_1100_basic.txt`, `csci_1100_cloze.txt` | EMT/CS | Anki deck (portable text export) | yes (Anki import) | not `itembank lint`-able as-is: Anki text format, not bank markdown. Conversion goes through the Phase 3.2 import + accept loop; no provenance yet |
| `Downloads/delete/mandarin_capture.apkg` (+ duplicates of the _study_exports .txt files) | Mandarin | Anki deck (.apkg) | no | only .apkg on the machine and it is Mandarin, not the 3 subjects; sits in a delete/cleanup folder. Would exercise the .apkg importer once built |
| `Downloads/CTF/weibao-anki-decks/` (`security-plus/basic.txt`, `cloze.txt`, `mandarin-domain/cards.tsv`) | Sec+/Mandarin | Anki deck source | yes (Anki import) | not the 3 subjects; same conversion gap as _study_exports |
| `weibao-planing/02_Skills_Learning/Anki/{EMT,CSCI_1100,Math_1400,Mandarin,SecPlus}_Anki_Capture.md` | per subject | Anki deck source (markdown capture log) | yes | human-readable card source, already reachable from day-surface globs; no machine linkage from deck back to capture (Phase 3.2 provenance would add the trail) |
| `weibao-planing/02_Skills_Learning/EMT/EMT_Notes.md`, `Chapters/ch01..ch09`, `Lessons/unit1_*` | EMT | notes / lesson material | yes | none for the day surface (already wired); banks/lessons lack `[SRC:]` provenance for authored specifics |
| `weibao-planing/02_Skills_Learning/EMT/{EMT_Assignments,EMT_Course_Cadence,EMT_Advance_Sprint}.md` | EMT | study plan / notes | yes | none; cadence is the study-plan source for the lane |
| `weibao-planing/02_Skills_Learning/Discrete_Math_1400_Notes.md` | Math | notes | yes | no exam bank exists for Math yet; bank authoring from these notes is Phase 3.2 seeding work |
| `weibao-planing/02_Skills_Learning/Math_1400_Orientation_Lessons.md` | Math | lesson material | yes | none |
| `weibao-planing/02_Skills_Learning/Foundations/Book_of_Proof_Map.md` | Math | study plan | yes | none |
| `weibao-planing/02_Skills_Learning/Concept_Glance_Sheets.md` | Math/CS/EMT | notes | yes | none |
| `weibao-planing/02_Skills_Learning/CSCI_1100/CSCI_1100_Notes.md`, `Blocks/01..18`, `CSCI_1100_Orientation_Lessons.md` | CS | notes / lesson material | yes | none for day surface; same provenance gap as EMT |
| `weibao-planing/02_Skills_Learning/CSCI_1100/{CSCI_1100_Assignments,CSCI_1100_Course_Cadence}.md` | CS | study plan / notes | yes | none |
| `weibao-planing/02_Skills_Learning/Cybersecurity/Bandit/{Syllabus,Bandit_Completions}.md` | CS (Linux, exam content) | study plan | yes | already wired as the Linux lane |
| `Downloads/Personal/wl-course-headstart/csci1100_intro_to_cs/` (`course_mirror_sprenkle_w26`, `course_mirror_levy_f2019`, `course_mirror_lambert_2014`, `local_labs`, `my_work`) | CS | lesson material (mirrored course) | yes | provenance/ownership: mirrored public course sites and lab specs; keep out of public repos; cite per Phase 3.2 `[SRC:]` |
| `Downloads/School/Continuing_Ed/100 Days of Code The Complete Python Pro Bootcamp (Dec 2025)/` + `100_Days_Course_Resources/` | CS (supplementary) | lesson material | yes | demoted in the plan to optional evening reps; purchased-course content, keep out of repos |
| `Downloads/Personal/` PDFs: `Emergency Care and Transportation ... (AAOS 12e)`, `Prehospital Emergency Care, 12th (Mistovich)`, `Discrete Mathematics and Its Applications (Rosen)`, `Discrete_Math_Levin`, `Book_of_Proof_Hammack`, `The_Linux_Command_Line_Shotts` | EMT/Math/CS | lesson material (textbooks) | yes (reading/authoring source) | copyrighted books: never in repo; usable only as cited `[SRC:]` sources for authored banks/notes |
| `weibao-planing/02_Skills_Learning/Skills_Learning_Roadmap.md` | all | study plan | yes | none |
| `weibao-planing/00_Dashboard/{Status_Dashboard.md, lanes.md, daily_log.md}` | all | study plan / day surface | yes | live wiring already lints clean; fuses expire Sep 3 |
| `weibao-planing/_daily/` | all | notes | yes | none; not wired into day surface |

## Scanned, not learning resources

| Path | Why not a resource |
|---|---|
| `Downloads/CTF/ankictl/` | tooling (reads Anki via AnkiConnect), no content |
| `Downloads/CTF/grimoire/` | Deadlock mod-manager app (Electron), no study content |
| `Downloads/CTF/mythcorp-gen2/`, `Documents/Codex/2026-07-23/.../mythcorp-gen2/` | game/web project + worktree copy |
| `Documents/grimoire-recovered-mods/`, `Downloads/CTF/obsidian-scroll-memory/`, `Downloads/Personal/Notes/obbty_obsidian/` | game mods / plugin / personal junk |
| `deadlock-mods`, `curseforge` | not present anywhere on this machine under those names |
| `Downloads/_study_exports/*.html` (`EMT_Exam_Bank_quiz.html`, `SecPlus_MC_Bank_*.html`) | build artifacts (rendered quizzes), derived from the banks above; regenerable, not source |
