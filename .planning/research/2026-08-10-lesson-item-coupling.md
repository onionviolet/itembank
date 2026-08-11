# Lesson and Item: What Couples, What Separates (Brief 2, R5)

- **Created:** 2026-08-10
- **Answers:** `RESEARCH-BRIEF-2-lesson-styles-2026-08-10.md` §2 R5.1 through R5.5
- **Binding:** `PLANNING-DIRECTIVES.md` all six sections, especially §4.2 (one parser)
  and §4.4 (additive format changes proven by a byte-identical fixture)
- **Must land before:** `/gsd-plan-phase 3.1`. Phase 3.2 and Phase 11 consume it.
- **Codebase verified against:** `model.py` (parse_lesson 167-256, content_fingerprint
  259-294, assign_ids 314, lint 593-820), `surfaces/daemon.py:126` scan_dir,
  `fixtures/lesson_bank.md`, `fixtures/lesson_src_bank.md`, `fixtures/lesson_shared.md`,
  `.planning/ROADMAP.md` Phases 1, 3, 3.1, 3.2, 9, 11.

---

## 0. The two facts that decide this

**Fact 1 — the fingerprint already ignores everything that couples.**
`content_fingerprint()` (`model.py:259-294`) builds its payload from `type`, `stem`,
options, `correct`, `select`, `cats`, `rows`, `steps`, `model`, `rubric` and nothing
else. `lesson_ref` is not in it. Neither is `objective`, `why`, `disc`, `second`,
`trap`, `conf`, `da`, `notes`, `difficulty` or `number` — the docstring names the
exclusions explicitly. **Therefore: rewriting a lesson for style cannot drift an item
hash, in either file layout.** The lifecycle argument for separation, as stated in the
brief ("accidental hash drift"), is empirically false in this codebase. It has to be
re-argued on other grounds, and it can be — see §2.

**Fact 2 — both shapes already parse through one function.**
`parse_lesson()` resolves `[LESSON-SRC:]` (line 213) into `head` *before* the
`## LESSON` search (line 228), so every downstream step — section match, heading walk,
returned key set — runs over one string regardless of provenance. The existing fixture
pair is the byte-identical proof §4.4 demands: `lesson_bank.md` is the one-file shape,
`lesson_src_bank.md` + `lesson_shared.md` is the two-file shape, both green today.
**Nothing in this document requires a parser change.** Every recommendation below is a
default, a lint code, a CLI transform, or a settings field.

---

## 1. R5.1 — Which shape is the default

### Verdict

**Two-file is the default.** A bank's `## LESSON` section lives in its own markdown
file beside the bank and is named by `[LESSON-SRC:]`. This is the shape the seeding
loop emits, the shape `spec` documents first, and the shape a new bank is scaffolded
into.

**The answer differs by subject, and the override is a subject-profile field, not a
global ruling.** New closed-entry key on the Phase 9 `subject_profiles` registry:

```
lesson_layout: "separate" | "inline"     # default "separate"
```

Shipped values: **EMT `separate`, Math `separate`, CS `inline`.**

The field governs exactly three things and nothing else:

1. what `itembank` scaffolds for a new bank in that subject,
2. what the Phase 3.2 seeder and Phase 11 authoring loop emit,
3. which of one warning pair fires (`lesson.layout_off_profile`, warning only — see
   §3.7; never an error, because both shapes are valid forever).

It governs **no parser branch, no renderer branch, and no scorer branch.** A reviewer
must be able to grep `lesson_layout` and find it only in settings, the scaffolder, the
authoring prompt builder, and one lint warning.

### Why two-file beat one-file

Every system with independent content and assessment lifecycles converged on
separation, and the one prominent counterexample bought inline-ness by adding exactly
the identity machinery this project already has:

| System | Shape | What it cost them |
|---|---|---|
| **Open edX OLX** | Problems live in `problem/` as their own files, referenced from verticals by `url_name`. Embedding verticals in `course.xml` is the documented shortcut; ORA problems are *always* separate files. | A manifest layer (`course.xml`) and a reference indirection. |
| **mdbook-quiz** (Rust Book) | Quizzes are TOML files in `quizzes/`, referenced from prose by `{{#quiz ../quizzes/rust-variables.toml}}`. Each question carries a UUID `id`. | An id scheme, and a validator crate (`mdbook-quiz-validate`) whose entire job is catching what drifts across that boundary. |
| **JupyterQuiz** | "The typical use pattern is for question sets to be created and stored in a separate JSON file"; inline-in-notebook is the documented alternative. | Questions leave markdown entirely and become JSON. |
| **QTI 3.0** | Each `assessmentItem` is its own XML file and its own `cp:resource` in `imsmanifest.xml`; tests reference items; shared assets get `cp:dependency` edges. | The whole manifest apparatus. QTI does not model the *lesson* at all — separation there is item-from-test, not item-from-prose. |
| **PreTeXt / Runestone** | Exercises are authored **inline** in the book source. | A mandatory durable `@label` per exercise, because "the label attribute is required by Runestone to generate database identifiers for the questions and student responses." Inline is affordable there *precisely because* exercise identity is a stable string independent of position. |

PreTeXt is the important row. It proves one-file works at open-textbook scale, and it
names the price: a durable per-exercise identifier that survives edits and moves.
`[ID:]` plus `[HASH:]` is that price, already paid in Phase 1. So one-file is **safe**
here in a way it is not in systems without item ids. It is not, however, **preferable**
— see §2 for the two costs that remain after hash drift is ruled out.

### Why CS overrides to inline

A CS lesson in the Bottom-Up shape *is* its exercises: the prose exists to set up a
runnable artifact, the artifact is the item, and the reading unit and the assessment
unit are the same three screens. Splitting a 40-line lesson away from the three
`check` items it exists to set up produces a file with a worse
signal-to-ceremony ratio than the thing it replaced, and the generation loop (§5)
gains nothing because the model is writing prose and exercise as one act.

EMT is the opposite extreme and the reason the field exists: one AAOS-shaped chapter
teaches forty items across many objectives, and those items will not all be authored,
reviewed, or revised at the same time as the prose. Math sits with EMT because the
Phase 9 worked-example form has the same one-chapter/many-items ratio.

### What this costs

| Cost | Size |
|---|---|
| One new key in `schemas/settings.schema.json` `subject_profiles.entries` — a **closed** object per `09-02-PLAN.md`, so this is a registry `version` bump | One task in Phase 9, or fold into 09-02 before it is planned |
| Scaffolder honours the field | One task, Phase 3.1 |
| `lesson.layout_off_profile` warning | One lint code |
| Nothing in `model.py`'s parser | Zero |

---

## 2. R5.2 — The lifecycle argument, restated correctly

Hash drift is off the table (§0, Fact 1). Two real costs remain, and they are the
actual argument for the default:

### 2.1 Concurrent writers on one file (the strong argument)

Phase 11 SC4 commits **each autonomous authoring write as its own commit**, and SC5
requires every auditor write to be undone by a single documented action. Phase 3.1's
style pass rewrites lesson prose. If prose and items share a file:

- a per-write revert of a machine-authored item also reverts any prose edit that
  landed in the same commit, or forces a hunk-level revert that SC5's "one documented
  action" does not cover;
- the style pass and the seeder contend for the same file, and a bank being restyled
  cannot be safely appended to;
- `git blame` on an item stem is polluted by prose rewrites and vice versa.

None of this is hypothetical bookkeeping — it is a direct conflict with two Phase 11
success criteria. This is the finding that decides §1.

### 2.2 Review noise (the weaker but real argument)

A style rewrite of a 2000-word chapter and a one-line distractor fix produce diffs of
the same file. Reviewing "did any item change?" becomes a diff-reading exercise rather
than a file-listing exercise. With separation it is: did any `*-lesson.md` change, or
did the bank change? Two questions, each answerable without reading a hunk.

### 2.3 What breaks in the systems that separate — and the rule it yields

The instructive failure is **Canvas New Quizzes item banks**. Editing a bank item that
students have already answered forces "Edit a Copy," and doing so **breaks the link
between the item bank and the quiz already taken**. The edited version lives on in the
bank; the answered version survives only inside that one quiz. The bank and the
delivered assessment silently fork.

That is the failure mode of sharing **items** across contexts. mdbook-quiz's separate
validator crate is the same class of problem in miniature: once quizzes are their own
files, something has to check that the reference still resolves.

**The rule this yields, and it is the single most important sentence in this
document:**

> **Separate the prose. Never separate — or share — the item.**
> Many banks may point at one lesson file (`[LESSON-SRC:]`, already shipped and
> already fixtured). One bank must never point at many lesson files, and one item must
> never live in, or be referenced by, two banks.

`[LESSON-SRC:]`'s direction of sharing is the safe one: the shared artifact is prose,
which carries no evidence, no `[ID:]`, and no attempt history. Reversing that arrow —
a shared *item* pool — imports the Canvas fork problem wholesale and is rejected here
and in §4.

### 2.4 What separation costs that one-file does not

Honest accounting, all of it real:

- **Discovery.** `surfaces/daemon.py:scan_dir()` classifies a `.md` file as a bank
  (`parse_bank()` non-empty), else a day plan, else **skipped silently**. A standalone
  lesson file is invisible to the index by design — the `lesson_shared.md` fixture
  header says so. A two-file default makes "silently skipped" the common case, so an
  orphaned or misnamed lesson file is invisible rather than loud. Fix: §3.7's
  `lesson.src_orphan_file` warning, computed from a directory walk, not a parser change.
- **Cross-bank drift.** A heading renamed in a shared lesson breaks `[LESSON-REF:]` in
  banks the editor never opened. `lint` is per-bank today. Fix: §3.6.
- **One more file per bank.** Accepted.

---

## 3. R5.3 — Coupled or separable, item by item

| Candidate | Verdict | Where it lives | New lint |
|---|---|---|---|
| Objective (`[OBJECTIVE:]`, `[OBJ:]`) | **Coupled to the item; separable from the lesson file** | Item block, authoritative. Lesson headings *may* declare a covering set. | `lesson.objective_mismatch` (warning) |
| `[SRC:]` provenance | **Coupled to the assertion, not the file** | Both sides may carry it; ids resolve in the referencing bank's `## SOURCES` | `lesson.src_id_unknown` (error), `sources.id_conflict` (error, cross-bank) |
| `[[term]]` glossary scope | **Coupled to the lesson** | `## TERMS` travels with the prose; visible to every bank naming that lesson | `term.undefined_in_scope` (error) |
| `[!KEY]` block identity | **Coupled to the lesson file it is authored in** | Carries its own `[ID:]`/`[HASH:]` per 3.1 SC2 | `key.duplicate_id` (error, cross-file) |
| LESSON-REF backlink | **Coupled, and it is the one edge that actually drifts** | Item names heading text; slug is the join | `lesson.src_shared_drift` (error, cross-bank) |

### 3.1 The objective

Authoritative on the item and nowhere else. `content_fingerprint()` excludes it
(`model.py:264`) and `item.objective_unnamespaced` already lints its shape
(`model.py:654-659`). Do **not** make the lesson the source of truth: Phase 3.2 SC3
computes the coverage map on demand from items so it cannot go stale, and a second
authority would give it two inputs to reconcile.

What separation permits, and 3.2's `[OBJ:]` makes cheap: a `###` heading may
optionally declare the objectives it teaches. Then:

> **`lesson.objective_mismatch` — warning.** An item's `[OBJECTIVE:]` is not in the
> declared set of the heading its `[LESSON-REF:]` names, and that heading declares a
> non-empty set. Warning, not error, because an item legitimately integrates across
> objectives and headings will often declare nothing.

### 3.2 `[SRC:]`

Coupled to whoever makes the claim. A lesson paragraph citing a source and an item
citing a source are two independent assertions; an item **must not silently inherit**
the lesson's citation, because Phase 11 SC2 requires every "covered" claim to cite the
exact passage behind it, and an inherited citation cites the wrong granularity.

The `## SOURCES` registry (3.2 SC3) stays in the **bank**, because that is where the
paraphrase lint (3.2 SC4) and the coverage map run. Therefore:

> **`lesson.src_id_unknown` — error.** A `[SRC:]` in the external lesson file names an
> id absent from the referencing bank's `## SOURCES`. Reported against the bank, with
> the lesson file path and line in the detail.
>
> **`sources.id_conflict` — error, cross-bank.** Two banks sharing one lesson file
> define the same `## SOURCES` id with different metadata. Runs only in the `--all`
> mode of §3.6.

### 3.3 `[[term]]` and `## TERMS`

Coupled to the lesson, hard. `## TERMS` is part of the teaching text and travels with
it. **Glossary scope = the lesson file, visible to every bank that names it.** Not
per-bank (two banks sharing a lesson would need duplicate glossaries that drift), not
global (a global glossary makes `glossable()`'s answer-leak gate unanalyzable, since a
term's definition would no longer have a bounded set of items it could leak into).

> **`term.undefined_in_scope` — error.** A `[[term]]` reference resolves to no
> `## TERMS` entry in the lesson in scope. Subsumes the naive "undefined term" check;
> the "in scope" wording is what makes it correct across the file boundary.

An item stem using `[[term]]` resolves against the lesson its bank points at — one
lesson per item (§4) is what makes that resolution single-valued.

### 3.4 `[!KEY]` identity

Coupled to the lesson file. The block carries `[ID:]`/`[HASH:]` (3.1 SC2) and exports
to Anki with a round-tripping `#guid`. Two consequences separation forces:

- **Moving a lesson between files must not remint ids.** The `split`/`inline`
  transforms in §6 are pure text moves for exactly this reason.
- **Copying a lesson file duplicates ids**, and a duplicated Anki `#guid` corrupts the
  learner's collection on re-export. This is the one place where separation creates a
  new failure mode with real consequences outside the repo.

> **`key.duplicate_id` — error, cross-file.** Two `[!KEY]` blocks anywhere under the
> scanned root claim the same `[ID:]`. Cross-file by necessity; runs in `--all`.

### 3.5 LESSON-REF

Already coupled and already linted, and — verified — both checks already work across
the `[LESSON-SRC:]` boundary, because `parse_lesson()` resolves the source before the
heading walk:

- `item.lesson_ref_unknown` (error) — item names no existing heading (`model.py:667-671`)
- `lesson.orphan_heading` (warning) — heading no item references (`model.py:813-818`)
- `lesson.duplicate_heading` (error) — slug collision (`model.py:803-808`)
- `lesson.src_unreadable` (error) — missing or escaping path (`model.py:213-225, 783-798`)

Separation adds no per-bank gap here. It adds one cross-bank gap, §3.6.

### 3.6 The one genuinely new capability: `lint --all`

A shared lesson file makes per-bank lint insufficient. Renaming a `###` heading in
`lesson_shared.md` is green when linting the bank you have open and red in a bank you
did not open.

> **`lesson.src_shared_drift` — error.** In `--all` mode, a lesson file named by more
> than one bank has a heading set that fails `item.lesson_ref_unknown` for at least one
> referencing bank. Reported once per affected bank, naming the shared file and the
> other banks.

Implementation: a directory walk reusing `scan_dir()`'s classification, a
lesson-path → referencing-banks map, then the existing `lint()` per bank. **No parser
change, no new block, no dependency.** `sources.id_conflict` and `key.duplicate_id`
ride the same walk. Cost: one plan in Phase 3.1, plus one CI coupling in the shape
Phase 3's `03-03-PLAN.md` already established.

### 3.7 Two hygiene warnings the default requires

> **`lesson.src_orphan_file` — warning.** A `.md` file under the scanned root has a
> `## LESSON` section, is not itself a bank, and no bank names it via `[LESSON-SRC:]`.
> Counters `scan_dir()`'s silent skip (§2.4).
>
> **`lesson.layout_off_profile` — warning.** A bank in a subject whose profile declares
> `lesson_layout: separate` carries an inline `## LESSON`, or vice versa. Warning only,
> forever. Both shapes stay valid; this is a nudge, not a gate.

### 3.8 New lint codes, complete list

| Code | Severity | Scope |
|---|---|---|
| `lesson.objective_mismatch` | warning | per bank |
| `lesson.src_id_unknown` | error | per bank |
| `term.undefined_in_scope` | error | per bank |
| `lesson.src_orphan_file` | warning | `--all` |
| `lesson.layout_off_profile` | warning | per bank |
| `lesson.src_shared_drift` | error | `--all` |
| `sources.id_conflict` | error | `--all` |
| `key.duplicate_id` | error | `--all` |

Eight codes, four of which only run in the new `--all` mode. All are additive: a bank
using none of the new blocks produces byte-identical lint output, provable against the
existing `fixtures/lesson_bank.md` and `fixtures/sample_bank.md`.

---

## 4. R5.4 — The unit on each side

### Lesson side: one chapter, which is one reading session

**Verdict: the lesson file is one chapter — 15 to 30 minutes of reading — subdivided by
`###` headings that are the objective-sized unit.**

Not one file per objective. The `###` heading already gives objective granularity for
free: it is the `[LESSON-REF:]` target, it has a slug, it is what the reader links to,
and it is the generation unit in §5. One file per objective multiplies the shared-drift
surface (§3.6) and the orphan-file surface (§3.7) by roughly ten, buys nothing the
heading does not already give, and fights the way both EMT chapters and Math sections
are actually written.

"Chapter" and "one session's reading" are the same unit at this scale, which is why
this does not need to be two rulings.

### Item side: the bank file, scoped to the chapter

**One bank = the items for one lesson.** For EMT and Math that is one chapter's items;
for CS the bank *is* the lesson. Bank granularity is already load-bearing elsewhere —
`scan_dir()` keys the index by filename stem and reports stem collisions
(`daemon.py:139-141`), and sessions target a bank — so this ruling costs nothing new.

### Does an item belong to exactly one lesson?

**Yes, and it must stay yes. This is enforced today by construction, and the
enforcement should be made explicit rather than incidental.**

The structural facts, verified:

- `[LESSON-SRC:]` is a **preamble directive, one per bank** (`model.py:213`, grabbed
  from `head`), and an external source **wins over** an inline section.
- An item's `[LESSON-REF:]` resolves against exactly one heading set, and **only the
  first `[LESSON-REF:]` tag on an item is read** (documented `model.py:499-500`).

So an item cannot belong to two lessons without a format change (a per-item
`[LESSON-SRC:]`, or honoured multiple `[LESSON-REF:]` tags). **Do not make that
change.** What breaks if you do:

1. **The backlink becomes ambiguous.** Phase 3 SC1 requires a working link from the
   lesson to each item that references it, and the reader's return path. With two
   lessons, "back to the reading" has two answers and the runtime has to pick — which
   is the runtime making a content decision, adjacent to Directive §4.1.
2. **`lesson.orphan_heading` becomes uncomputable per bank.** It is currently a
   set-difference over one bank's refs. With many-to-many it needs a global graph, and
   a warning that requires a full-repo walk to be correct is a warning that is wrong
   most of the time it runs.
3. **The coverage map gains a join.** Phase 3.2 SC3 computes it on demand precisely so
   it cannot go stale; a many-to-many edge makes "on demand" mean a directory walk.
4. **It re-imports the Canvas fork problem** (§2.3) through the back door: an item
   serving two lessons is an item serving two contexts, and the first divergent edit
   forks it.

> **`item.lesson_ref_multiple` — warning.** An item carries more than one
> `[LESSON-REF:]`. Silently reading the first and dropping the rest is worse than
> saying so. (Ninth code; add to §3.8.)

**The sanctioned way to relate an item to a second body of teaching text is
`[[term]]` (a gloss into the shared glossary) or `[PREREQ:]` (3.2 SC6) — never a second
LESSON-REF.**

---

## 5. R5.5 — The authoring loop

**Verdict: separation helps, materially, and the mechanism is not file adjacency.**

They are two jobs with disjoint context budgets:

| | Lesson writer (3.1 style + 3.2 seeding) | Item writer (3.2 seeding, 11 authoring) |
|---|---|---|
| Needs | style file, `[SRC:]` passages, objective list, `## TERMS` so far | the **finished lesson section text**, its objective, item-type grammar, the lint contract |
| Does not need | any item grammar, distractor rules, rubric shape | the style file, the other 39 items, the rest of the chapter |
| Acceptance gate | style lint (3.1 SC3), paraphrase lint (3.2 SC4) | `lint` clean + second quality gate (11 SC3) |

The worry the brief raises — that splitting loses the coupling that keeps generated
items on topic — is answerable directly: **the coupling that keeps items on topic is
that the item generator is handed the lesson section text as its context and must emit
a `[LESSON-REF:]` that lints.** That is a machine-checked constraint
(`item.lesson_ref_unknown`, `model.py:667-671`). Co-location in a file is not
machine-checked at all; it is a hope that the model read upward. A checked constraint
beats an unchecked adjacency.

Concretely, the loop Phase 3.2 should emit:

1. Write the chapter's `###` headings first (outline-first), one heading per objective.
2. Per heading, prose-first: generate the section against the style file and `[SRC:]`
   passages. The section is the **retrieval unit** for step 3 — which is the whole
   grounding story R3.4 is otherwise looking for, obtained for free from the file split.
3. Per heading, generate N items with **only that section** in context. Short context,
   one topic, no room to wander into a neighbouring objective.
4. Lint. `item.lesson_ref_unknown` and `lesson.objective_mismatch` are the on-topic
   test. Retry on failure per 11 SC1's cap.

One-file generation actively harms this: appending an item means opening the file the
prose lives in, which invites the model to "improve" prose while adding an item — the
exact churn that Phase 11 SC5's single-action reversibility cannot cleanly undo (§2.1),
and the exact thing that would drift a `[!KEY]` hash even though it cannot drift an
item hash.

**One caveat, stated so a plan can honour it:** step 3 must be given the section text,
not the section *reference*. A prompt builder that passes a path and trusts the model
to have read the file re-creates the problem this ruling solves. That is a Phase 3.2
plan-level acceptance criterion, not a format question.

---

## 6. Migration between the two shapes

Both shapes parse today, so migration is a **pure text transform in the shape
`assign_ids()` already is** (`model.py:314` — "Pure text transform... Returns
`(new_text, ...)`"), lives in the same module, and gets the same test discipline.

**`itembank lesson split <bank>`** — moves the `## LESSON` section (and `## TERMS`, and
any `[!KEY]` blocks inside them) into `<bank-stem>-lesson.md` beside the bank, and
writes `[LESSON-SRC: <bank-stem>-lesson.md]` at the position the `## LESSON` heading
occupied.

**`itembank lesson inline <bank>`** — the inverse. **Refuses** if the source file is
named by more than one bank; merging a shared lesson into one bank would silently
strip the other bank's reading material. Refusal names the other banks.

Both hold these invariants, each a test:

1. **Every item chunk is byte-identical before and after.** No `[HASH:]` is
   recomputed, no `[ID:]` is minted, no `[!KEY]` id changes. This is checkable by
   string comparison of the question chunks, and it is the acceptance criterion.
2. **`parse_lesson()` returns an equal dict** modulo `source` — same `body`, `intro`,
   `headings`, `error`.
3. **`lint()` output is unchanged** modulo `lesson.layout_off_profile`.
4. Round-trip `split` then `inline` on a single-referrer bank is the identity on the
   bank's item chunks.

Cost: one plan. No parser change, no new block, no dependency, no schema change beyond
the §1 profile key.

---

## 7. Non-negotiables check (`PLANNING-DIRECTIVES.md` §4)

| Rule | Status |
|---|---|
| 1. Runtime decides what reaches the learner | Untouched. No model in any path here. |
| 2. One parser, one scorer, one evidence store | **Held literally.** `parse_lesson()` already resolves both shapes into one string before any structural work (`model.py:206-227`). `lint --all` is a directory walk that calls the *same* `lint()` per bank. Zero scorer or evidence changes. |
| 3. Evidence and banks on disk, no telemetry | Untouched. |
| 4. Additive, proven by byte-identical fixture | **Held.** Both shapes are already valid and already fixtured (`lesson_bank.md` vs `lesson_src_bank.md` + `lesson_shared.md`). Every new lint code fires only on a block that does not exist in a pre-3.1 bank. The subject-profile key has a default, so an entry omitting it behaves as `separate`. |
| 5. UI-SPEC accessibility gates | Untouched — no new surface. |

Directive §3 (build both) is satisfied without a fork: both layouts ship, the choice is
a settings field, and there is no second parser to pay for.

---

## 8. What I could not determine

1. **Whether the `subject_profiles` entry schema tolerates a new key without a
   migration.** `09-02-PLAN.md` specifies each entry contains *exactly* `id`,
   `version`, `lesson`, `allowed_item_types`, `verifier` — a **closed** object. Adding
   `lesson_layout` is therefore a registry `version` bump, not a free field. Phase 9 is
   not yet planned, so the cheap fix is to fold the key into 09-02 before it is
   planned. If Phase 9 is planned first, this becomes a versioned migration. **Flag at
   `/gsd-phase`.**
2. **Whether `[!KEY]` blocks may appear in item rationale fields.** Left open by the
   D1/D2/D3 artifact (its own open question 3). If they may, `key.duplicate_id` has to
   span banks and lessons rather than lesson files alone. Assumed here: **KEY is
   lesson-only**, matching that artifact's "not valid in stems" ruling.
3. **The PreTeXt `@label` stability claim rests on secondary sourcing.** The PreTeXt
   Guide states `@label` generates the Runestone database identifiers for questions and
   student responses; I could not fetch the Runestone Author's Guide directly (HTTP
   403) to confirm an explicit warning that changing a label orphans student records.
   The inference is strong but is an inference.
4. **No measurement of real one-file review churn**, because there is no real bank yet
   — Phase 3.2 exists precisely because the corpus does not. §2.1 and §2.2 are
   structural arguments against Phase 11's stated criteria, not observed data.

---

## Sources

- [The OLX Courseware Structure — Open edX docs](https://docs.openedx.org/en/latest/educators/olx/organizing-course/course-xml-file.html)
- [The OLX Structure of a Sample Course — Open edX docs](https://docs.openedx.org/en/latest/educators/olx/example-course/insider-structure.html)
- [mdbook-quiz README — cognitive-engineering-lab](https://github.com/cognitive-engineering-lab/mdbook-quiz/blob/main/README.md)
- [mdbook-quiz-validate — crates.io](https://crates.io/crates/mdbook-quiz-validate)
- [JupyterQuiz README](https://github.com/jmshea/jupyterquiz/blob/main/README.md)
- [QTI v3 Best Practices and Implementation Guide — 1EdTech](https://www.imsglobal.org/spec/qti/v3p0/impl)
- [QTI ASI XML Binding — 1EdTech](https://www.imsglobal.org/sites/default/files/spec/qti/v3/bind/index.html)
- [Interactive Exercises — The PreTeXt Guide](https://runestone.academy/ns/books/published/pretextguide/topic-interactive-exercises.html)
- [The PreTeXt Guide (PDF)](https://pretextbook.org/doc/guide/pretext-guide.pdf)
- [Writing your own Exercises — Runestone Instructor Guide](https://guide.runestone.academy/InstructorGuide-11.html)
- [Item Banks — Canvas, Colorado State](https://canvas.colostate.edu/item-banks/)
- [How Do I Use Item Banks in New Quizzes? — Canvas@UD](https://sites.udel.edu/canvas/2026/02/how-do-i-use-item-banks-in-new-quizzes/)
