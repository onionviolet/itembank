---
date: 2026-08-09
topic: Blind spots B1-B15 — verdicts, competitor practice, cost, phase ownership
brief: .planning/RESEARCH-BRIEF-learning-platform-2026-08-09.md §3.5
confidence:
  B1_cold_start: HIGH (import formats and open-content licensing web-verified; internal cost verified against ROADMAP.md)
  B2_mobile: HIGH (Tauri status from official blog; Anki/Mochi practice web-verified)
  B3_audio_tts: MEDIUM-HIGH (TTS quality from community benchmarks, not vendor docs; export-surface cost estimate is internal reasoning)
  B4_B15: MEDIUM (one-source web verification each; internal cost claims verified against ROADMAP.md and UI-SPEC.md)
  added_blind_spots: MEDIUM (mostly internal reasoning over verified project state)
  Q9_Q10: argued positions, not verifiable facts
---

# Blind Spots B1–B15 — Research Findings

Scope: one learner (Weibao), three subjects (EMT / Math 1400 / CSCI 1100),
Python runtime + markdown banks + browser surfaces, packaged desktop app as end
goal. Non-negotiables honored throughout: runtime gates the learner; one
parser / one scorer / one evidence store; evidence on disk, no telemetry;
additive format; accessibility gates; no punitive mechanics.

Classification key: **FORMAT** (bank grammar), **RENDERER** (surfaces),
**RUNTIME** (scorer/evidence/selection), **PACKAGING**, **CONVENTION**
(docs, policy, workflow — no code contract).

---

## B1 — Cold Start (HIGH PRIORITY) — VERDICT: REAL, ROADMAP-CHANGING

**(a) Real?** Yes — the single largest risk in the roadmap. Phases 5–10 build
teaching machinery (hint ladder, selection, model adapter, retention) that is
only exercisable against a populated bank, and the authoring loop that
populates banks is Phase 11 — dead last. The current sequence means the first
*full-size real* bank appears after the entire teaching loop was built and
"verified" against synthetic fixtures. For a one-learner product, abandonment
risk peaks in week one, not at Phase 11.

**(b) How competitors handle it:**
- **Anki** — shared-deck ecosystem: the first deck is someone else's download,
  not authored. `.apkg` is the de-facto interchange format. [CITED: brandur.org/fragments/apkg]
- **Quizlet** — search other people's sets; but as an *export source* it is now
  effectively closed: export is creator-only, website-only, blocked entirely
  for copied sets, and gated behind a paid subscription. [CITED: help.quizlet.com/hc/en-us/articles/360034345672]
  Do not plan around Quizlet import; screen-scraping is the only path and it is
  ToS-hostile.
- **Knowt / Revisely / Quizlet Magic Notes** — AI generation from pasted notes
  or photos is now table stakes in the flashcard market. [ASSUMED: product
  positioning from search results, not tested]
- **AI item generation research (2025–26)** — four documented hallucination
  classes in MCQ generation: reasoning inconsistencies, insolvability, factual
  errors, mathematical errors. Multi-stage pipelines with rule-based + LLM
  detection agents cut hallucination >90% vs. naive generation.
  [CITED: arxiv.org/abs/2601.14280; arxiv.org/pdf/2602.18891] This maps
  *exactly* onto our architecture: draft → `lint` (rule-based gate) → second
  quality gate (Phase 11's distractor-overlap/near-duplicate checks). The
  research validates the design we already have; the problem is only its
  position in the sequence.

**Import source inventory (verified):**

| Source | State | Usable? |
|---|---|---|
| Anki `.apkg` | ZIP + SQLite (`collection.anki2`/`.anki21`; `.anki21b` is Zstd-compressed) [CITED: github.com/5mdld/anki-apkg-extractor] | **Yes** — stdlib `zipfile` + `sqlite3` reads legacy formats; `.anki21b` needs Zstd (ask Anki to export legacy, or accept one dep). Cards→`short`/term items. |
| Quizlet | Creator-only, paywalled, copied sets blocked | **No** — dead end |
| OpenStax College Algebra | CC-BY, includes review exercises + answer keys per chapter [CITED: openstax.org/details/books/college-algebra-2e] | **Yes** — legally derivable for Math 1400 with attribution |
| Runestone Academy | Open textbooks with embedded exercises (CS1 books) [CITED: runestone.academy/ns/books/index] | **Yes** for CSCI 1100 concepts; exercise extraction is manual-ish |
| Open EMT/NREMT banks | Free-to-*use* prep sites exist (OpenExamPrep etc.) but **none found under an open license** — free ≠ derivable | **No as import**; EMT cold start must be AI generation from Weibao's own course materials (AAOS-12e derivative risk already accepted 2026-08-05) |

**(c) Cost in our stack:** Low, because the hard assets already exist —
format contract, machine-readable lint (`lint --json`, Phase 1), `spec` good
enough for a context-free authoring agent (Phase 3 SC4), and the model adapter
seam (Phase 8). A *thin* seeding capability is: (1) `itembank import anki
<file.apkg>` — stdlib zipfile+sqlite3, ~1 plan; (2) a draft→lint→retry
generation command that is a strict subset of Phase 11's AUTH-01/02 (no
auditor, no autonomy ladder, human approves every batch) — ~2 plans;
(3) `[SRC:]` provenance tags, already planned as insert 03.2.

**(d) Phase ownership — RECOMMENDATION (roadmap-changing):** Widen the
already-proposed insert **03.2 "Source Provenance & Extraction"** into
**"Seeding, Import & Provenance"** and land it before Phase 5. It owns: Anki
import, OpenStax/Runestone-derived starter content for Math/CS, the thin
draft-lint-approve generation loop for EMT, and `[SRC:]`. Phase 11 keeps the
auditor, autonomy ladder, and second quality gate. This is the pull-forward
the brief asked about, and the answer is yes.

**(e) Classification:** RUNTIME (import command) + FORMAT (`[SRC:]`, already
planned) + CONVENTION (generation loop policy: human approves every write at
this stage).

---

## B2 — Mobile (HIGH PRIORITY) — VERDICT: REAL PROBLEM, WRONG SOLUTION SPACE — DESCOPE THE APP, OWN THE RECIPE

**(a) Real?** The *need* is real — between-shift studying is phone studying.
But "build a mobile app" is the wrong conclusion for a one-user product.

**(b) Competitors:**
- **Anki** — three-codebase strategy: AnkiDroid (free, community, separate
  codebase), AnkiMobile (paid iOS, funds development), AnkiWeb (free web
  review + sync hub). [ASSUMED: well-known ecosystem structure, not re-verified
  this session] The lesson: even Anki, with millions of users, never unified
  mobile — it's three products sharing a sync protocol.
- **Mochi** — local-first, offline-capable mobile apps; sync is a $5/mo Pro
  feature; free tier is single-device. [CITED: mochi.cards]
- **Tauri 2 mobile** — stable since Oct 2024, current 2.9.x, production apps
  exist; but plugin coverage lags desktop and the team calls it a foundation,
  not the finished mobile story. [CITED: v2.tauri.app/blog/tauri-20]
  **Critical conflict:** the brief's packaging recommendation is Python as a
  sidecar under Tauri. iOS does not permit spawning sidecar subprocesses, and
  Android makes it painful — Tauri mobile would require porting the runtime
  (parser, scorer, evidence store) out of Python, i.e., a rewrite of the
  project's core asset. [ASSUMED: iOS process-model limitation from platform
  knowledge, not re-verified] So yes: **the desktop-app goal and a native
  mobile app actively conflict** under the recommended architecture.

**(c) Cost in our stack:** Nearly zero for the right scope, ruinous for the
wrong one. We already hold the pieces:
- Phase 2 SC2: `--lan` reaching a phone on the same wifi is a *shipped*
  success criterion. [VERIFIED: .planning/ROADMAP.md, Phase 2 SC2]
- UI-SPEC already gates all surfaces at 320 CSS px and 200% zoom.
  [VERIFIED: .planning/UI-SPEC.md, surface coverage table]
- The offline static HTML quiz is a shipped feature — it is already a
  read-only sync bundle; it just isn't framed as one.

**(d) Phase ownership:** Phase 4 (responsive gates — largely done) + a
CONVENTION doc: "Studying on your phone" — daemon `--lan` at home; Tailscale
(user-level install, zero code) away from home [ASSUMED: standard practice for
local-first apps]; static quiz bundle + Anki export + B3 audio pack as the
fully-offline away-from-home story. **Write the descope rationale into the
roadmap: no native mobile app this milestone; revisit only if the LAN-PWA
recipe demonstrably fails in practice.**

**(e) Classification:** RENDERER (responsive, already gated) + CONVENTION
(recipe + descope rationale). Explicitly NOT PACKAGING.

---

## B3 — Audio / TTS (HIGH PRIORITY) — VERDICT: REAL, CHEAP, BEST LEVERAGE-PER-COST IN THE LIST — BUILD AS AN EXPORT SURFACE

**(a) Real?** Yes. EMT protocol memorization is rote-recall-heavy and
commute-compatible; it is the one modality where "studying happens anyway"
time exists. And it is the away-from-home mobile story B2 needs.

**(b) Competitors:** Anki's `{{tts}}` template tags + AwesomeTTS; the
anki-handsfree addon (configurable question→pause→answer→repeat with audible
countdown) [CITED: github.com/angel333/anki-handsfree]; `anki_tts` CLI that
renders a whole deck to one audio file [CITED: github.com/andrewimpellitteri/anki_tts];
Pimsleur-style prompt→pause→confirm loops in language learning. **Nobody in
the assessment space ships a first-class audio drill export** — this is a
differentiator, not a catch-up feature.

**Local TTS state (2026):**
- **Kokoro** (82M params) — benchmark local quality, near-early-ElevenLabs,
  runs on CPU, 54 voices / 8-9 languages. [CITED: offlinetts.com/blog/browser-tts-showdown-kokoro-piper-kitten]
- **Piper** — fastest and smallest (RTF ~0.03), 900+ voices, noticeably more
  robotic on long passages. [CITED: same benchmark]
- **edge-tts** — free Microsoft neural voices via reverse-engineered Edge API;
  ToS-gray (officially Edge-reader-only), network-required, item text transits
  to Microsoft. [CITED: github.com/rany2/edge-tts]
- **Windows built-in** — legacy SAPI voices are robotic; Win11 natural voices
  are locked to Narrator/Edge, third-party access only via the
  NaturalVoiceSAPIAdapter hack that can break on any update.
  [CITED: github.com/gexgd0419/NaturalVoiceSAPIAdapter] Don't depend on it.

**(c) Cost in our stack — LOW, because of one framing decision: audio is an
EXPORT surface, not an interactive one.** `itembank export audio <bank>
--objective X` renders a drill pack: stem → N-second silence → key → one-line
why, concatenated per objective into mp3/m4b chapters. Playback is any podcast
app in the car — **zero hands-free interaction to build**, and the safety
framing comes free: "recall drill; no interaction required or possible while
driving." Generation runs at the desk, so the degrade-never-block rule is
untouched (an export that needs network can fail loudly without blocking
study). Engine is a config: edge-tts for quality-now (same accepted-risk class
as hosted models — item text transits; per-subject opt-out applies), Piper for
fully-local-now, Kokoro when the 7900 XTX arrives. Audio-expressible content:
`## TERMS` entries, `[!KEY]` blocks (D2!), `short` items, and mc stems read
as recall ("what is the adult compression depth?" → pause → key) — table /
dnd / build refuse loudly by item number, exactly the GIFT precedent.
Stitching: per-segment WAV + stdlib `wave` concatenation, or accept ffmpeg for
mp3/chapters. Roughly one plan, two at most.

**(d) Phase ownership:** New small insert after 03.1 (it consumes TERMS and
`[!KEY]`), or bolted to the widened 03.2 seeding phase. No evidence writes —
no scoring happens in a car; optionally a later "mark what you missed" desk
flow.

**(e) Classification:** RENDERER (export surface) + CONVENTION (safety
framing, engine config). RUNTIME untouched.

---

## B4 — Print / PDF export — REAL, CHEAP, YES

(a) Real for EMT (paper drilling, skill-sheet culture). (b) Quizlet prints;
Anki barely; the true competitor is the prep book. (c) We already ship a
static HTML quiz — a print stylesheet + browser print-to-PDF is nearly free;
an answer-key-on-last-page variant reuses `explain_payload`. (d) Attach to
Phase 9 (subject media polish) or the theming debt of Phase 4; one plan.
(e) RENDERER.

## B5 — First-run and empty states — REAL, PARTIALLY OWNED ALREADY

(a) Real. (b) Every polished competitor (Mochi, Notion, Linear-class apps)
treats first-run as a product surface. (c) UI-SPEC already binds empty/zero
states per surface kind [VERIFIED: .planning/UI-SPEC.md UI Considerations
table]; what's missing is the *zero-bank, day-one* flow, which is really B1
wearing UI clothes: first run should offer "import an Anki deck / generate
from your materials / open the sample bank." (d) The widened 03.2 seeding
phase owns the flow; Phase 4 shell owns the rendering. (e) RENDERER +
CONVENTION.

## B6 — Search — REAL, DEFERRABLE, CHEAP WHEN DONE

(a) Real but not urgent at one-user bank sizes. (b) Anki's browser/search is
its power-user core; Obsidian search is the benchmark for markdown vaults.
[ASSUMED] (c) Banks are grep-able markdown today; in-app search rides the
disposable sqlite3 index Phase 1 already built [VERIFIED: ROADMAP.md 01-08] —
add an FTS5 table at reindex time, one route + one CLI command. (d) Phase 10
(report/inspection surfaces) or a later insert. (e) RUNTIME (index) +
RENDERER.

## B7 — Backup and portability — REAL, MUST NOT STAY UNOWNED

(a) Real: local-first without backup is data loss with extra steps. (b) Anki
keeps automatic rolling local backups [ASSUMED: documented Anki behavior];
the local-first community standard is Syncthing for cross-device replication
[CITED: howtogeek.com free-open-source-tool-solves-the-main-problem-with-local-first-apps].
(c) Cheap: banks are already git-friendly; evidence store needs (1) a rolling
zip snapshot on daemon start (stdlib), (2) `itembank backup` command, (3) a
documented Syncthing/git recipe. **Warning that interacts with M1 below: the
evidence log is append-only single-writer — bidirectional file sync of a live
log risks conflict-file corruption; the recipe must say "one writing machine,
others read or restore."** (d) Small insert or attach to Phase 10; the
CONVENTION doc can be written now. (e) RUNTIME (snapshot) + CONVENTION.

## B8 — Adherence and motivation — REAL, THE GENUINELY HARD ONE

(a) Real — the top determinant of outcomes and the least tractable. (b)
Duolingo's streak guilt is forbidden by our spec; Anki's motivator is the
brutal honesty of the due count; FSRS communities lean on load smoothing.
(c) Our non-punitive positive mechanisms, all cheap: exam-fuse countdown
framing (fuse dates already exist in `lanes.md` [VERIFIED: CLAUDE.md day
surface description]), "what you're ready for today" as the day cockpit's
lead (readiness, not debt), short-session default (Phase 10 SC6 already
mandates this [VERIFIED: ROADMAP.md]), and visible evidence of progress per
objective. (d) Phase 10 owns it; UI-SPEC principle 5 is the guardrail.
(e) CONVENTION + RENDERER copy.

## B9 — Image ingestion / OCR — REAL, GATED ON PHASE 8

(a) Real: serves B1 (photograph course handouts) and EMT figures. (b) Quizlet
Magic Notes does photo→cards; Mathpix is the OCR benchmark for math
[CITED: mathpix.com/handwriting-recognition]. (c) The cheap path is not an OCR
dep — it's the Phase 8 model adapter with a vision-capable hosted model:
photo → model extracts text/items → same draft-lint-approve loop as B1. Zero
new architecture; one input path on the seeding loop. Item text transiting to
a hosted model is the already-accepted risk. (d) Seeding phase (03.2 widened),
feature-flagged on Phase 8 adapter landing; sequence-wise this argues for the
adapter's *interface* (not tier-gate UX) landing early. (e) RUNTIME (input
path) + CONVENTION.

## B10 — Handwriting / stylus — REAL CONCERN, DESCOPE RECOGNITION

(a) The concern (typed math is painful) is real; the solution (handwriting
recognition) is not worth it for one user. MyScript/Mathpix are the
state of the art [CITED: myscript.com/math; mathpix.com] but both are heavy
deps or paid APIs, and our scorer needs canonical text regardless. (c/d) The
honest workflow: do the work on paper; type or photograph the final answer;
`short` items are human/rubric-marked already, and a photo can ride B9's path
for the *tutor to comment on* (never to score). Write the descope rationale;
backlog recognition. (e) CONVENTION (descope note). 

## B11 — Exam-format fidelity — REAL, AND WE ARE ACCIDENTALLY EXCELLENT AT IT — ELEVATE

(a) Real and under-priced by the brief. The 2026 NREMT is a CAT exam whose
technology-enhanced item types are: drag-and-drop categorization, build/ordered
lists, multiple response, checkbox grids, and case studies.
[CITED: medictests.com/2026-nremt; open-exam-prep.com/blog/nremt-emt-exam-guide-2026]
**Our six item types map almost one-to-one: dnd→drag-and-drop, build→ordered
list, multi→multiple response, table→checkbox grid.** No flashcard competitor
can say that. (b) Prep products (Kaplan, MedicTests, UWorld-style) sell
exactly this fidelity. (c) What's missing is small: a case-study grouping
(several items sharing one evolving scenario stimulus) — an additive
`[CASE:]`/case-block grammar — plus an "exam sim" preset = exam feedback mode
(Phase 6, exists) + exam selection composition (Phase 7, exists) + case
grouping (new) + a blueprint-weighted mix (Primary Assessment ~40% at EMT
level per the 2026 blueprint [CITED: medictests.com/2026-nremt — prep-site
figure, treat as MEDIUM confidence]). (d) FORMAT change in the seeding/format
phase; selection preset in Phase 7; sim preset assembled in Phase 9 or 10.
(e) FORMAT + RUNTIME.

## B12 — Bank versioning and diffing — REAL ASSET, ALREADY MOSTLY OWNED

(a) Real as a differentiator, nearly free: banks are markdown in git; Phase 11
already specifies one-commit-per-machine-write and single-step reversibility
[VERIFIED: ROADMAP.md Phase 11 SC4/SC5]. (c) Optional sugar later:
`itembank diff` that renders item-level (not line-level) changes using item
IDs from Phase 1. (d) Defer; Phase 11 adjacency. (e) CONVENTION now, RENDERER
sugar later.

## B13 — Reading accessibility beyond WCAG — HALF-REAL; DO THE EVIDENCE-BACKED HALF

(a) Mixed evidence. Dyslexia-specific fonts do **not** work: controlled
studies show OpenDyslexic reads slower and less accurately than Arial/Times,
with no participant preference [CITED: ncbi.nlm.nih.gov/pmc/articles/PMC5629233;
edutopia.org/article/do-dyslexia-fonts-actually-work]. What *is*
evidence-backed and font-agnostic: increased letter/word spacing, generous
line-height, and controlled measure (line length). (c) Cheap: Phase 4's token
system gets a measure token and an optional focus/pacing mode (dim everything
but the current block); skip specialty fonts entirely. Weibao has stated no
specific need — keep this low priority. (d) Phase 4 debt / Phase 9 reader
polish. (e) RENDERER.

## B14 — Degraded-model UX — REAL, ALREADY OWNED, NEEDS ONLY EXECUTION

(a) Real but not a gap in ownership: UI-SPEC's agent-support surface already
enumerates model-unavailable / policy-blocked / tool-failed / cancelled states
with typed-state fixtures and degraded-provider UAT [VERIFIED:
.planning/UI-SPEC.md UI Considerations, agent support row], and Phase 8 SC3 is
the degrade guarantee [VERIFIED: ROADMAP.md]. What remains is the copy/design
pass inside Phase 8's UI-BLOCKED work. Nothing to insert. (e) RENDERER.

## B15 — Time-on-task honesty — REAL, DECIDE EARLY BECAUSE EVIDENCE IS APPEND-ONLY

(a) Real: pacing (Phase 10) and trend quality improve materially with item
latency and session duration; all-local measurement is compatible with
no-telemetry by definition. (c) Cheap *if decided early*: additive fields on
response events (elapsed ms, session wall time). Because the log is
append-only, retrofitting is impossible for past evidence — the one reason
this can't just wait for Phase 10. Guardrail: latency is a *selection signal*,
never a displayed speed score (UI-SPEC principle 5). (d) Field addition ASAP
(next phase that touches response events — Phase 6 records `hints_used` and
mode, add timing there); consumption in Phase 10. (e) RUNTIME (evidence
fields).

---

## Blind spots the list MISSES

| # | Blind spot | Why it matters | Lands |
|---|---|---|---|
| M1 | **Multi-machine, one user.** The 7900 XTX build is *planned* — day one it exists, evidence lives on two machines. Bidirectional sync (Syncthing-style) of an append-only single-writer log is a corruption risk, not a convenience. [CITED: howtogeek.com Syncthing pattern; risk analysis internal] | Silent evidence forking would poison Phase 10 trends permanently. | CONVENTION now ("one writing home; others are clients over LAN or restore-from-backup"), RUNTIME merge tooling only if ever needed. Pairs with B7. |
| M2 | **Licensing of derived items at the export boundary.** AAOS-12e-derivative items are fine as personal use on disk; GIFT/Anki/audio/print exports are the moment derived content can leave the machine. OpenStax requires attribution (CC-BY). | One-page policy prevents accidentally publishing infringing exports; guard already covers the repo, not the exports. | CONVENTION, written during the seeding phase where `[SRC:]` lands. |
| M3 | **Interruption and resume UX.** Sessions are resumable JSON already [VERIFIED: CLAUDE.md], but the *experience* — phone rings mid-case-study, return three hours later — is undefined; interacts with Phase 6 cursor-hold and B11 case groups. | EMT life is interruption-shaped. | RENDERER: "resume where you were" as the index page's first affordance; Phase 4/6. |
| M4 | **Recognition bias.** mc/multi/table drill recognition; NREMT is recognition-shaped so EMT is fine, but Math 1400 mastery is production-shaped. A bank that grows by AI generation will over-produce mc (easiest to generate and score). | Trains the wrong skill precisely where the scorer is most comfortable. | CONVENTION (per-subject item-type mix targets in the subject profile, Phase 9) + Phase 7 selection weighting by type. |
| M5 | **Data migration over years.** Schema versions exist (Phase 1) and the updater ships new code against old data (Phase 2.1), but no stated compatibility promise (how many versions back a log/session upgrades cleanly). | A learning tool's value compounds over years; a silent format break in year 2 destroys it. | CONVENTION: an N-version upgrade promise + a migration test in CI. Attach to Phase 2.1 debt. |
| M6 | **Model cost budgeting.** "Out of credits must never stop you studying" is a constraint with no meter behind it. | Cost surprise is the most likely reason the model layer gets turned off in anger. | RUNTIME: Phase 8 already logs every model interaction to evidence [VERIFIED: ROADMAP.md Phase 8 SC5] — add token/cost fields and a monthly local rollup on `/report`. Cheap. |
| M7 | **Accessibility of authored content.** Our gates check the renderer, not the author: nothing lints missing figure alt text, table headers in lessons, or link text. AI-generated content makes this worse at scale. | The auditor will happily mass-produce inaccessible content that passes every gate we have. | FORMAT/CONVENTION: lint codes land with figures/callouts in 03.1; the Phase 11 second quality gate inherits them. |

(Exam-day simulation, suggested by the task prompt, is folded into B11.)

---

## Q9 — What are we not asking? Assumptions in the brief that are probably wrong.

1. **The brief assumes the bottleneck is features. It's content and adherence.**
   Fifteen blind spots and a huge visual-design research prompt, and the two
   things that decide whether Weibao is still using this in November — a
   populated bank (B1) and showing up daily (B8) — are two rows in a table.
   The differentiator list (D1–D8) is a list of things to build; nothing in
   the brief measures whether the *existing* loop is being used.
2. **"A packaged desktop app is an end goal" is probably optimizing the wrong
   surface.** Weibao's own framing of study time — between shifts, driving —
   is phone-and-audio-shaped. Desktop is where authoring and deep work
   happen; consumption is mobile/audio. The brief treats mobile as a blind
   spot to patch rather than as the primary consumption context to design
   for. The desktop app should be framed as the *studio*; the LAN
   page + audio pack are the *product* most days.
3. **"Phase 11 authoring is deliberately late for risk reasons" conflates two
   different things.** The risky subsystem is the *auditor with autonomy*
   (coverage claims, machine writes). The draft-lint-approve loop is the
   *safe* half and is desperately needed early (B1). Splitting them costs
   nothing architecturally — the brief already half-knows this (insert 03.2)
   but doesn't say the second half out loud.
4. **The brief assumes Quizlet is part of the import landscape.** It isn't —
   creator-only, paywalled, copied-sets-blocked export makes it a dead end
   [CITED: help.quizlet.com]. Anki's `.apkg` is the only interchange format
   worth code.
5. **The Tauri-with-Python-sidecar recommendation and any future mobile hope
   are in direct tension**, and the brief doesn't note it: iOS forbids the
   sidecar model outright. Choosing Tauri-sidecar is fine — but it should be
   chosen *knowing* it forecloses native mobile without a runtime rewrite,
   which strengthens the case for the LAN/audio/export mobile story (B2/B3).
6. **The tier-gate's UX legibility (D4) is over-weighted for a one-user
   product.** Weibao built the gate; he doesn't need it made legible to trust
   it. The gate's *enforcement* (Phase 8's detection/stripping mechanism)
   deserves the effort; the persuasion UI can be minimal.
7. **Nobody is asking "what gets measured to declare a phase actually
   worked?"** Success criteria are all mechanism ("X renders", "Y records");
   there is no usage criterion anywhere ("Weibao completed N real sessions on
   real content this week"). For a product with exactly one user, that number
   is cheap to collect (B15 fields) and is the only ground truth available.

## Q10 — Single highest-leverage change not in the roadmap

**Pull a thin seeding loop (import + draft-lint-approve generation) in front
of Phase 5, as the widened 03.2 insert — the bank factory before the teaching
machine.** Every phase from 5 through 10 becomes dogfoodable against real
EMT/Math/CS content instead of synthetic fixtures the moment it lands, the
NREMT-shaped item types (B11) get exercised with real scenarios, and the
riskiest Phase 11 machinery later inherits a battle-tested generation loop
rather than debuting untested. The runner-up is the audio drill export (B3) —
cheapest differentiator in the entire document — but it loses the tiebreak
because it, too, needs a populated bank first. Seeding is upstream of
everything; nothing is upstream of seeding.

---

## Phase-assignment summary

| Item | Verdict | Owner | Class |
|---|---|---|---|
| B1 cold start | Real, roadmap-changing | **Widen insert 03.2 → Seeding, Import & Provenance; before Phase 5** | RUNTIME+FORMAT+CONVENTION |
| B2 mobile | Real need; descope native app | Phase 4 responsive (done-ish) + CONVENTION recipe; rationale recorded | RENDERER+CONVENTION |
| B3 audio/TTS | Real, cheap, differentiating | New small insert after 03.1 (or inside 03.2) | RENDERER+CONVENTION |
| B4 print/PDF | Real, cheap | Phase 9 polish | RENDERER |
| B5 first-run | Real | 03.2 flow + Phase 4 shell | RENDERER+CONVENTION |
| B6 search | Real, deferrable | Phase 10 or later insert | RUNTIME+RENDERER |
| B7 backup | Real | Snapshot cmd + recipe; attach Phase 10; doc now | RUNTIME+CONVENTION |
| B8 adherence | Real, hard | Phase 10 | CONVENTION+RENDERER |
| B9 OCR/photo | Real | 03.2 input path, gated on Phase 8 adapter | RUNTIME+CONVENTION |
| B10 handwriting | Descope recognition | Backlog; workflow note | CONVENTION |
| B11 exam fidelity | Real, elevate | `[CASE:]` in format phase; presets Phase 7/9 | FORMAT+RUNTIME |
| B12 bank diffing | Owned already | Phase 11 adjacency; sugar later | CONVENTION |
| B13 readability | Half-real | Phase 4 tokens (measure, focus mode); no dyslexia fonts | RENDERER |
| B14 degraded model | Owned already | Phase 8 UI-BLOCKED work | RENDERER |
| B15 time-on-task | Real, decide early | Timing fields in Phase 6 evidence; consume Phase 10 | RUNTIME |
| M1 multi-machine | Add | CONVENTION now, pairs with B7 | CONVENTION |
| M2 export licensing | Add | 03.2 policy page | CONVENTION |
| M3 resume UX | Add | Phase 4/6 | RENDERER |
| M4 recognition bias | Add | Phase 9 profiles + Phase 7 weights | CONVENTION |
| M5 migration promise | Add | Phase 2.1 debt | CONVENTION |
| M6 model cost meter | Add | Phase 8 evidence fields + report rollup | RUNTIME |
| M7 authored-content a11y | Add | 03.1 lint codes → Phase 11 gate | FORMAT+CONVENTION |
