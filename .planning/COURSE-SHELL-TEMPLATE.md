# Course shell template, v0 (tentative)

Date: 2026-08-26
Status: **tentative proposal.** Not an accepted product clause. Derived from
`.planning/research/2026-08-26-navigate2-teardown.md`, which is the evidence.
Binding scope remains `.planning/SOURCE-TO-COURSE.md`.

Purpose: give itembank a way to hold **more than one course at once**, so EMT,
Math 1400, CSCI 1100 and whatever comes next sit in one workspace with one
runtime, one scorer, one evidence store. Navigate2 is the first specimen. It is
a starting template to beat, not a model to imitate; the intent is to keep
studying other learning programs and to raise this template each time.

## 0. Why a template at all

Today itembank has banks, sessions, lessons and a `day` cockpit, but no durable
object that says "this is a course, these are its parts, here is where the
learner is in it". Every additional subject currently costs bespoke wiring.
The shell is the missing container.

## 1. The three levels

Navigate2's one defensible structural idea, kept:

```
workspace          all courses the learner owns
  └── course       EMT, Math 1400, CSCI 1100, ...
        └── unit   chapter, module, week, topic
              └── treatment   one thing to actually do
```

Deliberately only three levels below the workspace. The 2026-08-13 vision entry
asks for deeper nesting (field > subject > subcourse > concept). That is
recorded and NOT resolved here; see section 7. v0 ships three and is designed so
`unit` can nest later without breaking existing courses.

## 2. Durable objects

Per the CLAUDE.md rule that every feature names its actor, source of truth,
authority and recovery:

| Object | Source of truth | Authority | Derived? |
|--------|-----------------|-----------|----------|
| workspace index | `courses.md` at the workspace root | learner | no |
| course | `<course>/course.md` manifest | course builder | no |
| unit | a section in `course.md` | course builder | no |
| treatment | a row in a unit, pointing at an artifact | course builder | no |
| artifact | the bank, lesson, or source file itself | existing contracts | no |
| progress / mastery | evidence store | **runtime only** | **yes, disposable** |
| course card, outline, next-actions | rendered view | none | **yes, disposable** |

The manifest is plain Markdown so it stays readable and editable in Obsidian,
per the existing dual-form rule. Progress is never written into it.

## 3. Treatment purposes, and the evidence contract per purpose

The closed set. Purpose decides the icon, the colour, AND what evidence the
runtime will accept from it. This is the correction to Navigate2, where eight of
nine activities emitted nothing and the shell still showed `Progress: 0 / 9`.

| Purpose | Typical artifact | Evidence emitted | Counts toward mastery |
|---------|------------------|------------------|-----------------------|
| `orient` | objective card, unit map | viewed only | no |
| `read` | source binding, direct reading | `self_report` | no |
| `teach` | lesson with checkpoint items | scored checkpoints | yes |
| `drill` | term bank, Anki export | attempt records | yes |
| `apply` | case / scenario items | scored, advisory mark allowed | yes |
| `check` | blueprint form from the bank | full session evidence | yes |
| `reflect` | learner note, error log | learner-owned | **never** |

Two hard rules, both of them things Navigate2 gets wrong:

1. **A treatment that emits no runtime evidence is labelled as such in the UI**
   and cannot move a mastery number. `orient` and `read` show as done-by-claim,
   visibly distinct from done-by-evidence.
2. **`reflect` never becomes truth.** Direct restatement of the existing rule
   that learner notes never silently become source truth, answer keys, scores,
   or mastery.

There is no `Mark as done` primitive. The nearest thing is `self_report` on a
`read`, and it is typed, dated, and visibly a claim.

## 4. The manifest

Sketch, additive to existing formats, no change to bank parsing:

```markdown
# COURSE: EMT
ID: emt
SOURCE: AAOS Emergency Care and Transportation, 12e
FRAMEWORK: National EMS Education Standards
BLUEPRINT: nremt-emt

## UNIT: Chapter 1 EMS Systems
OBJECTIVES: emt.1.1, emt.1.2, emt.1.3

- orient  Objectives          -> objectives/emt-01.md
- read    Chapter 1           -> sources/aaos12e.md#ch1        pages 4-29
- teach   EMS system roles    -> lessons/emt-01-roles.md
- drill   Chapter 1 terms     -> banks/emt-01-terms.md
- check   Chapter 1 check     -> banks/emt-01.md  blueprint: 10 mc, 2 multi
```

Every row is `purpose  label  -> artifact`. A unit may omit any purpose. That
omission is the point: the treatment-selection rule says direct reading is
sometimes enough, and a uniform nine-slot grid per chapter is precisely the
failure mode observed in the specimen.

## 5. The two surfaces

### 5.1 Workspace view, "which course"

A card per course. Each card shows: subject, unit count, and **two separate
numbers that must never be merged**:

- `coverage`: units with any accepted treatment, out of total units
- `mastery`: objectives with sufficient evidence, out of total objectives

Navigate2 shows one number, `Progress: 0 / N`, computed from self-pressed
checkboxes. Showing coverage and mastery separately is the fix, and it keeps
the accepted-content / workflow-state / confidence axes uncollapsed as the
CLAUDE.md state-axes rule requires.

### 5.2 Course view, two panes

- **Next actions**: evidence-driven, prerequisite-aware, short. This is the
  `day` cockpit scoped to one course, and it is the default pane.
- **Browse**: the full unit outline, explicitly labelled a reference index and
  not a plan.

The specimen's left drawer of 41 chapters, each expanding to 9 leaf links, is a
table of contents pretending to be a path. Keeping it as `Browse` is fine.
Letting it be the primary navigation is the mistake.

## 6. Degraded and offline behaviour

Unchanged from the standing rule: the shell must render, and every `read`,
`drill`, `apply` and `check` must run, with the network unplugged. Only
model-assisted `teach` and next-action ranking may go quiet. A course whose
source is a remote binding shows the binding as unavailable rather than hiding
the unit.

## 7. Open questions, carried not answered

1. **Depth.** The 2026-08-13 vision asks for field > subject > subcourse >
   concept and for "completing a field". v0 ships three levels. What counts as a
   field, and what completion of one means, is unresolved and needs ideaboarding.
2. **Evidence event for a non-scored treatment.** No type exists today for
   "read this". `self_report` needs an honesty story before it ships.
3. **Surface or mode.** Is the course view a new surface, or a mode of `day`?
4. **Where the manifest lives** relative to banks and to an Obsidian vault, and
   how discovery binds it without mutating anything.
5. **Cross-course scheduling.** `day` already spans subjects. Does the workspace
   view compete with it, or feed it?

## 8. How this template is meant to improve

Explicitly a v0 to be beaten. Each further learning program studied gets a
teardown note in `.planning/research/` on the pattern of the Navigate2 one:
observed structure as fact, implementation as fact, interpretation kept
separate, proposals marked as recommendations, and a rights note. Ideas that
lose stay in `IDEA-LEDGER.md` with the reason, per the append-only rule.

Candidate next specimens, in rough order of expected yield: Brilliant (guided
teaching), Albert (practice and blueprint reporting), Anki and its scheduler,
Khan Academy (mastery model and prerequisite graph), Duolingo (path and streak
mechanics), edX or Coursera (multi-course workspace at scale).

## 9. Rights note

Nothing from the specimen is vendored. Moodle core is GPLv3 and the `navigatexl`
theme and JB Learning branding are not ours; the observed design tokens are
stock Boost defaults and were used only to confirm that nothing bespoke exists
worth copying. This template is clean-room derived from the information
architecture, which is an idea rather than an expression. Raw capture is kept
outside the repository.
