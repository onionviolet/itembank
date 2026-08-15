---
phase: 16A-semantic-capability-activity-contract
plan: 10
type: execute
wave: 10
depends_on: ["16A-09"]
files_modified:
  - fixtures/lesson_capability_corpus.py
  - tests/capability_stress_corpus_tracer.py
  - .planning/phases/16A-semantic-capability-activity-contract/16A-TRACER-REPORT.md
  - .planning/phases/16A-semantic-capability-activity-contract/16A-REVIEW.md
  - .planning/phases/16A-semantic-capability-activity-contract/16A-FREEZE.md
  - .planning/phases/16A-semantic-capability-activity-contract/16A-DECISIONS.md
  - .planning/phases/16A-semantic-capability-activity-contract/16A-VALIDATION.md
autonomous: false
requirements: [CAP-01, CAP-02, CAP-03, ACTIVITY-01, ACTIVITY-03, A11Y-02, PORT-01]
estimate:
  tokens: 92000
  raw_tokens: 92000
  tasks: 3
  confidence: low
must_haves:
  truths:
    - "The portable rich-lesson stress corpus exists as one buildable artifact: build_all_16a produces every fixture this phase named, including the medical evolving-case lesson with its dated jurisdiction warning and the disputed-timeline lesson preserving disagreement, locators, and uncertainty, and one tracer run walks all of them."
    - "The medical evolving-case fixture proves no premature reveal against shipped machinery rather than by inspection: under [GATE: required] the server emits nothing below the first open check, so the heading that names the resolution is absent from the served bytes and is present in the canonical Markdown, which is truncation at the server and not a DOM hide."
    - "The disputed-timeline fixture preserves disagreement rather than resolving it: both conflicting accounts appear, each carries a resolvable source locator through the shipped ## SOURCES registry, an uncertainty block states that the question is open, and lint reports no unresolvable source reference."
    - "PORT-01 is proven by execution, not by claim: the corpus is opened with every derived HTML, index, and cache deleted, every capability's core meaning, caption, citation, definition, static activity instruction, and media alternative is found in the plain Markdown, and every derived view rebuilds to equal bytes while the canonical files' SHA-256 values are unchanged by the cycle (PORT-01 adjacency probe)."
    - "Preamble section order stays free: a corpus lesson whose ## TERMS, ## SOURCES, ## MEDIA, and ## ACTIVITIES sections are written in two different orders parses to equal dicts, because every one of them reads through the same _preamble_section boundary rule (PORT-01 ordering probe)."
    - "The tracer measures rather than asserts: every duration, byte count, fixture count, and file count in 16A-TRACER-REPORT.md is a figure the run produced on the machine and Python version the report names, and no budget number appears that was not measured."
    - "No 16A freeze record is written on a red tracer, a red adversarial suite, a missing or rejecting human review, or an unresolved leak finding from plan 16A-09. On any missing leg the file opens with a Freeze withheld section naming that leg, the string Frozen at 16A appears nowhere in it, and the phase stays open."
    - "The shipped runtime is unregressed: the full suite runs green and the two golden SHA-256 values recorded in 16A-PRECONDITION.md are unchanged, so the whole phase's format growth is proven additive by comparison against a baseline taken before any of it existed."
  prohibitions:
    - statement: "An agent must not sign its own contract; the judgment that fourteen roles, fifteen capability profiles, eleven activity fields, eight backburner triggers, and two degraded paths are legible and honest is a human's, and a green tracer is not that judgment."
      status: kept
      verification: flagged-unverified
    - statement: "The freeze record must not claim a leg that was not run; a leg that could not be executed is named as withheld rather than described as satisfied or omitted from the list."
      status: kept
      verification: flagged-unverified
    - statement: "A derived view must not become the only understandable copy; with every rendered page, index, and cache deleted, the canonical Markdown must still carry the complete core meaning, captions, citations, definitions, static activity instructions, and media alternatives."
      status: kept
      verification: flagged-unverified
    - statement: "Real course, exam, learner, or clinical material must not enter the repository through the corpus; the medical evolving case is a fictional presentation with a fictional jurisdiction and a fictional date, and it is not clinical guidance."
      status: kept
      verification: flagged-unverified
  artifacts:
    - "fixtures/lesson_capability_corpus.py gains build_medical_case, build_disputed_timeline, build_section_order_permutation, and build_all_16a"
    - "tests/capability_stress_corpus_tracer.py gains scenario_medical_case, scenario_disputed_timeline, scenario_portability, and scenario_section_order"
    - ".planning/phases/16A-semantic-capability-activity-contract/16A-TRACER-REPORT.md"
    - ".planning/phases/16A-semantic-capability-activity-contract/16A-REVIEW.md"
    - ".planning/phases/16A-semantic-capability-activity-contract/16A-FREEZE.md"
    - "16A-DECISIONS.md gains the dated D-16A-10 freeze-scope answer"
    - "16A-VALIDATION.md with its Per-Task Verification Map complete, its runtime placeholder replaced by a measured figure, and its sign-off boxes resolved"
  key_links:
    - "The medical case's no-premature-reveal claim must be asserted on the SERVED bytes, not on a rendered string a test built in memory. Phase 6.2's gate truncation is a server-side stop, and asserting on an in-memory render would test the renderer rather than the gate. If the corpus can only be rendered statically in this suite, the assertion must say so and the freeze record must record the weaker proof rather than the stronger claim."
    - "The portability scenario must delete derived artifacts and rebuild in a fresh temporary tree, not in the repository. Deleting derived files in the working tree would pass by accident on a machine where they were never generated, and would be destructive on one where they were."
    - "Task 3 re-runs the tracer and the adversarial suite rather than trusting Task 1's recorded result, because the review in Task 2 may have prompted a fix and a freeze record must describe the tree it is freezing rather than the tree that was tested."
    - "Plan 16A-09's Task 3 may have recorded an open leak finding. The freeze decision reads that summary explicitly: a recorded leak in this phase's own new grammar is a withholding leg, because CAP-01's roles shipping with a disclosure hole is exactly the kind of thing a freeze would make expensive to fix."
---

<objective>
Run the phase's own freeze gate and either write the freeze or name the leg that
withheld it.

`ROADMAP.md`'s Phase 16A freeze gate, quoted in full: "the portable rich-lesson
stress corpus: one synthetic lesson exercising every semantic teaching role plus
one unknown optional and one unknown required semantic, rendered in both
continuous reader and guided modes; the medical evolving-case fixture with a
dated jurisdiction warning and no premature reveal, and the disputed-timeline
fixture preserving disagreement, locators, and uncertainty; the localization
fixture set inside the corpus; the capability profile fixture with one renderer
marked unavailable showing the static instructional path; the two-output-mode
composition fixture plus one backburner catalog entry; the purpose-first
activity set including one unsupported response form falling back to its
declared static equivalent; the adversarial runtime-authority fixture in which
every leak, invented-score, auto-grade, and frozen-sitting edit attempt is
refused; and the corpus opened outside the app in a plain Markdown viewer with
every derived HTML, index, and cache deleted, staying readable and rebuilding."

Seven of those nine legs were built by plans 16A-02 through 16A-09 and are
re-run here rather than rebuilt. Two are new: the medical evolving-case fixture
and the disputed-timeline fixture. The ninth, the portability check, is the one
PORT-01 actually turns on and it is executed literally rather than claimed.

Both new fixtures are chosen to prove something against shipped machinery rather
than against this phase's own new code. The medical case's "no premature reveal"
rides on Phase 6.2's gate truncation, which stops the server below the first
open check so the resolution is never in the bytes a learner receives, rather
than on a hide-it-in-the-DOM trick. The disputed timeline rides on the shipped
`## SOURCES` registry and `[SRC: id locator]` directives from Phase 3.2, plus
this phase's `[!UNCERTAINTY]` and `[!EXCERPT]` roles, so preserving disagreement
means both accounts carry a resolvable locator and neither is presented as
settled.

The human review in Task 2 is the part a green tracer cannot supply. Fourteen
roles, fifteen capability profiles with their known limits, eleven activity
fields, eight backburner triggers, and two degraded copy strings a learner
actually reads are all things a test can prove present and cannot prove honest.
`PLANNING-DIRECTIVES.md` section 3a requires that every accepted recommendation
name its owner, its verification, its evidence class, and its failure condition,
and an agent never signs that for itself.

Decisions already made, cited, and never re-derived here:

- **`16A-DECISIONS.md` `## D-16A-1` through `## D-16A-9`**, all nine, read in
  full before Task 1. This plan resolves no grammar question.
- **`16A-PRECONDITION.md`, the Additivity baseline section**: the two golden
  SHA-256 values, which are re-asserted one final time.
- **`ROADMAP.md`'s Phase 16A freeze gate**, quoted above in full.
- **`16A-DECISIONS.md` `## D-16A-7`**: the dated jurisdiction warning is free
  prose with a stated date inside the shipped `[!WARNING]` callout; no
  structured date field is minted.
- **`16A-RESEARCH.md`'s Code Examples**, the eight-criterion proprietary-format
  gate from research report 04 section 8, quoted in full there, and its verdict:
  none of the eight is met, so the canonical lesson stays UTF-8 Markdown. The
  freeze record carries that verdict forward.
- **The phase-shape constraint**: visual system, tokens, and polish are Phase
  17A; guided mode in 16A is a data contract and a minimally rendered proof.

Purpose: prove the whole contract at once, in one run, and let a human judge it.
Output: one measured tracer report, one signed review, and one freeze record or
one named withholding.
</objective>

<context>
@.planning/phases/16A-semantic-capability-activity-contract/16A-DECISIONS.md
@.planning/phases/16A-semantic-capability-activity-contract/16A-PRECONDITION.md
@.planning/phases/16A-semantic-capability-activity-contract/16A-RESEARCH.md
@.planning/phases/16A-semantic-capability-activity-contract/16A-VALIDATION.md
@.planning/ROADMAP.md
@.planning/REQUIREMENTS.md
@.planning/PLANNING-DIRECTIVES.md
@fixtures/lesson_capability_corpus.py
@tests/capability_stress_corpus_tracer.py
@tests/assessment_authority_adversarial.py
@model.py
@surfaces/lesson.py
@capabilities.py
</context>

## Artifacts this phase produces (plan 16A-10 share)

New symbols introduced by this plan, and by nothing earlier:

- `fixtures/lesson_capability_corpus.py`: `build_medical_case`,
  `build_disputed_timeline`, `build_section_order_permutation`, `build_all_16a`
- `tests/capability_stress_corpus_tracer.py`: `scenario_medical_case`,
  `scenario_disputed_timeline`, `scenario_portability`,
  `scenario_section_order`
- The planning artifacts `16A-TRACER-REPORT.md`, `16A-REVIEW.md`,
  `16A-FREEZE.md`

No module, no CLI command, no daemon route, and no schema file is produced by
this plan. No change is made to `model.py`, `surfaces/lesson.py`,
`capabilities.py`, `runtime.py`, or `evidence.py` by this plan; if the review in
Task 2 finds a defect, the fix is a new plan and not a task here.

<tasks>

<task type="auto">
  <name>Task 1: the two remaining fixtures, the portability proof, and the measured tracer report</name>
  <files>fixtures/lesson_capability_corpus.py, tests/capability_stress_corpus_tracer.py, .planning/phases/16A-semantic-capability-activity-contract/16A-TRACER-REPORT.md</files>
  <read_first>
- `.planning/ROADMAP.md`, the Phase 16A freeze-gate paragraph, in full. Its nine
  legs are this task's checklist.
- `.planning/REQUIREMENTS.md` `CAP-01`'s Fixture sentence, especially the clause
  "The corpus also carries a medical evolving-case fixture with a dated
  jurisdiction warning and no premature reveal, and a disputed-timeline fixture
  preserving disagreement, locators, and uncertainty".
- `.planning/REQUIREMENTS.md` `PORT-01`'s Fixture sentence, verbatim.
- `model.py` lines 717 to 800, `parse_sources`, and its `[SRC: id locators]` and
  `[OBJ:]` directive handling, which the disputed-timeline fixture uses for its
  locators.
- `model.py` lines 530 to 535, the `[GATE:]` directive and its default, and
  `model.GATE_VALUES`.
- `surfaces/lesson.py` lines 1515 to 1535, the gate truncation branch in the
  block classifier, in full. Its comment describes the server-side stop the
  medical case's assertion depends on: "under required, the server emits nothing
  below the first OPEN check". Read it before writing the assertion so the
  assertion targets the right bytes.
- `tests/gate_roundtrip.py` in full, for how the repository already drives a
  gated sitting end to end, so the medical case's scenario reuses that path
  rather than inventing one.
- `fixtures/lesson_capability_corpus.py` in full as it stands after plan
  16A-09.
- `tests/capability_stress_corpus_tracer.py` in full.
- `.planning/phases/16A-semantic-capability-activity-contract/16A-PRECONDITION.md`,
  the Additivity baseline section.
  </read_first>
  <action>
1. Add `build_medical_case(dest_dir)` to
   `fixtures/lesson_capability_corpus.py`, following the established shape:
   literal fictional content, no `random`, deterministic bytes, no em dash
   characters.

   The bank's preamble carries `[GATE: required]`. Its `## LESSON` section has
   three `### ` headings, in this order:
   - The first presents an evolving fictional presentation: a fictional patient,
     fictional findings, no name of any real condition, protocol, or drug. It
     carries one `> [!WARNING]` callout whose prose states a date and a
     fictional jurisdiction, in the form
     `Protocol current as of 2026-03-01 for the fictional Kestrel County
     service. Check your own service's current protocol before acting.` That is
     `D-16A-7`'s free-prose-with-a-stated-date form; no structured date field is
     minted.
   - The second presents further findings and ends with one
     `> [!CHECK: <id>]` block whose id names a real `mc` item in the same bank.
   - The third names the resolution. Its heading text and its body both contain
     a distinctive fictional token, for example `KESTREL-RESOLUTION`, that
     appears nowhere else in the file, so an assertion can look for exactly one
     string rather than for a paraphrase.

   Add a module-level comment above the constant stating that this is a
   fictional teaching fixture, not clinical guidance, that the jurisdiction and
   the date are invented, and that no real protocol is reproduced or paraphrased.

2. Add `build_disputed_timeline(dest_dir)`. Its `## SOURCES` registry carries
   two fictional source ids with locators. Its `## LESSON` section presents two
   conflicting fictional accounts of when a fictional event happened, each in a
   `> [!EXCERPT]` callout carrying a `[SRC: <id> <locator>]` directive resolving
   to one of the two registered sources, followed by one `> [!UNCERTAINTY]`
   callout stating in plain words that the question is open and that neither
   account is settled. Neither date is presented as the answer anywhere in the
   file, and no `[!KEY]` block asserts one.

3. Add `build_section_order_permutation(dest_dir)`. It writes two banks whose
   content is identical except that one orders its preamble sections
   `## TERMS`, `## SOURCES`, `## MEDIA`, `## ACTIVITIES` and the other orders
   them `## ACTIVITIES`, `## MEDIA`, `## SOURCES`, `## TERMS`. It returns both
   paths. This is PORT-01's ordering probe made buildable.

4. Add `build_all_16a(dest_dir)`. It calls every builder this phase created, in
   a documented order, into one directory, and returns a dict mapping a short
   name to each written path. This is the one entry point the freeze gate and
   any later phase uses to materialize the whole corpus, so no caller has to
   know the builder list.

5. Add four scenarios to `tests/capability_stress_corpus_tracer.py`:

   - `scenario_medical_case()`: builds the medical case; drives a real gated
     sitting through the same path `tests/gate_roundtrip.py` uses; and asserts
     that the served bytes, while the check is open, do not contain the
     `KESTREL-RESOLUTION` token, and that the same token is present in the
     canonical Markdown source. Then clears the check and asserts the token
     appears in the served bytes afterward. Also asserts the warning's date
     string and jurisdiction string are both present in the rendered page.

     If the suite cannot drive a served sitting and can only render statically,
     do not fake it: assert what a static render can prove, mark the scenario
     result as a WEAKER PROOF in the tracer report with one sentence naming what
     could not be exercised, and let Task 3's freeze decision weigh it. A test
     that claims a server-side truncation it did not exercise is worse than one
     that says it could not.

   - `scenario_disputed_timeline()`: builds the disputed timeline; parses it;
     and asserts both fictional dates appear in the rendered page, that
     `model.parse_sources` resolves both `[SRC:]` directives, that `model.lint`
     reports no `prov.src_unknown`, that the rendered page contains a
     `callout-uncertainty` container, and that no `[!KEY]` block and no
     `CORRECT:` field anywhere in the lesson body asserts either date as
     settled.

   - `scenario_section_order()`: builds both permutations; parses each with
     `parse_terms`, `parse_sources`, `parse_media`, `parse_activities`, and
     `parse_lesson`; and asserts each pair of results is equal. This resolves
     PORT-01's ordering probe and proves the one boundary rule holds across all
     five readers.

   - `scenario_portability()`: this is PORT-01's Fixture executed literally, and
     it runs entirely inside a fresh temporary tree, never in the repository.
     In order: build the whole corpus with `build_all_16a`; render every lesson
     to HTML into that tree; compose both output modes and write them; record
     the SHA-256 of every canonical Markdown file and of every derived file;
     delete every derived artifact, meaning every `.html` file, every composed
     record file, and any index or cache the run produced; assert every
     canonical Markdown file's SHA-256 is unchanged by the deletion; then, for
     each capability the phase added, assert its meaning survives in the plain
     Markdown by finding, in the raw bytes, each of: every callout body, every
     `## TERMS` definition, every `## MEDIA` row's `credit` and `alt`, every
     `## ACTIVITIES` row's `static_fallback`, and every `[SRC:]` locator;
     finally rebuild every derived artifact and assert each rebuilt file's
     SHA-256 equals the value recorded before deletion.

     The rebuild-equality assertion resolves PORT-01's adjacency probe: a
     derived view and its canonical source touch exactly here, and the answer is
     that they separate cleanly, with the derived side reproducible and the
     canonical side untouched.

6. Write
   `.planning/phases/16A-semantic-capability-activity-contract/16A-TRACER-REPORT.md`.
   Every figure in it is measured on this machine during this run, and the
   report names the machine's operating system and the Python version that
   produced them. Sections, in this order:
   - **What was run.** The exact commands, verbatim, with their final lines.
   - **The nine freeze-gate legs.** One row per leg from `ROADMAP.md`'s
     paragraph, each marked `passed`, `weaker proof`, or `not run`, with the
     scenario or suite that covered it named. A leg marked anything but `passed`
     carries one sentence saying what was not exercised.
   - **Measured figures.** Tracer wall-clock duration, adversarial-suite
     wall-clock duration, full-suite wall-clock duration, the number of files
     `build_all_16a` wrote and their total byte count, the number of derived
     files deleted and rebuilt in `scenario_portability`, and the scenario and
     attack counts. No figure appears that was not produced by the run, and no
     budget or target number appears at all.
   - **Additivity evidence.** The two golden SHA-256 values from
     `16A-PRECONDITION.md` re-verified, side by side with the values found now.
   - **Open findings.** Every open item, including any leak finding plan
     16A-09's summary recorded, every scenario marked `weaker proof`, and every
     gap this phase deliberately deferred: media rights enforcement, media
     integrity recomputation, the annotated worked-example structure, interface
     localization of the new labels and copy, and every Phase 17A CSS handoff
     the earlier summaries recorded.

   No em dash characters anywhere in the file.
  </action>
  <verify>
  <automated>python tests/capability_stress_corpus_tracer.py</automated>
Expected final line: `TRACER: 18 passed, 0 skipped, 0 failed`, exit code 0. Then
run `python tests/assessment_authority_adversarial.py`, expecting
`ADVERSARIAL: 18 attempted, 18 refused, 0 succeeded` and exit 0, and
`for t in tests/*.py; do python "$t" || exit 1; done`, expecting exit 0. The
degraded state this task must also prove is that the portability scenario is
non-destructive: confirm `git status --porcelain` is unchanged by the run, since
`scenario_portability` deletes files only inside its own temporary tree.
  </verify>
  <acceptance_criteria>
- `python tests/capability_stress_corpus_tracer.py` exits 0 with the final line
  `TRACER: 18 passed, 0 skipped, 0 failed`.
- `python tests/assessment_authority_adversarial.py` exits 0 with the final line
  `ADVERSARIAL: 18 attempted, 18 refused, 0 succeeded`.
- `for t in tests/*.py; do python "$t" || exit 1; done` exits 0.
- `python itembank.py guard .` reports `0 offending files`.
- `git status --porcelain` reports no deleted file after the run.
- The two golden SHA-256 values in `16A-PRECONDITION.md` are unchanged.
- `scenario_portability` runs entirely inside a temporary directory; a grep of
  the scenario for `os.remove`, `shutil.rmtree`, or `unlink` shows every such
  call taking a path derived from the temporary root.
- The medical case's served bytes, while its check is open, do not contain
  `KESTREL-RESOLUTION`, and the canonical Markdown does. If only a static render
  was possible, the scenario is marked `weaker proof` in the report with a
  naming sentence.
- `16A-TRACER-REPORT.md` exists with all five named sections; its nine-leg table
  has nine rows; every figure in its Measured figures section is a measured one
  and no target or budget number appears.
- `16A-TRACER-REPORT.md` contains no em dash character.
  </acceptance_criteria>
  <reversibility rating="reversible">Two fixture builders, four test scenarios,
  and a report. None changes a published surface.</reversibility>
  <done>The whole freeze-gate corpus builds and walks in one run, PORT-01 is
  proven by a delete-and-rebuild cycle rather than by claim, and every figure in
  the report was measured.</done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Task 2: the contract-legibility review a human signs</name>
  <files>.planning/phases/16A-semantic-capability-activity-contract/16A-REVIEW.md</files>
  <read_first>
- `.planning/phases/16A-semantic-capability-activity-contract/16A-TRACER-REPORT.md`
  as written by Task 1, in full.
- `.planning/phases/16A-semantic-capability-activity-contract/16A-DECISIONS.md`
  in full, all nine decisions.
- `.planning/ROADMAP.md`, the Phase 16A goal paragraph and freeze-gate
  paragraph.
- `.planning/REQUIREMENTS.md`, the seven Fixture sentences for CAP-01, CAP-02,
  CAP-03, ACTIVITY-01, ACTIVITY-03, A11Y-02, and PORT-01, verbatim.
- `.planning/PLANNING-DIRECTIVES.md` section 3a, the accepted-recommendation
  discipline paragraph, which names owner, verification, evidence class, and
  failure condition as required of every accepted recommendation.
- `capabilities.py`'s fifteen profiles and eight backburner entries, read as
  prose rather than as code.
- `.planning/phases/16A-semantic-capability-activity-contract/16A-09-SUMMARY.md`,
  specifically any open leak finding it recorded.
- `.planning/phases/15B-quality-blueprint-acceptance/15B-REVIEW.md` if it
  exists, and
  `.planning/phases/14B-graph-course-package-prototype/14B-AUTHORABILITY-REVIEW.md`
  if it exists, as the precedent shape for a human review artifact here.
  </read_first>
  <what-built>
Plans 16A-02 through 16A-09 built the semantic capability and activity contract
and plan 16A-10 Task 1 walked it: all fourteen CAP-01 teaching roles rendering
in both continuous and guided modes, seven of them catalogued rather than
rebuilt; a required-versus-optional distinction with two named degradation paths
for an unknown semantic; fifteen capability support profiles with their
accessible behavior, offline fallback, renderer availability, version,
validation, and known limits, published as a schema the shipped validator
accepts; a media registry carrying rights, credit, accessible alternative,
derivation, availability, and integrity per asset, with three readable degraded
paths; a purpose-first activity declaration covering ten purposes over eight
shipped response forms with one unsupported form falling back; two registered
output modes composed from shared schemas and eight parked with a primitive, a
dependency, a cost, and a trigger; language and direction metadata with a
ten-case localization corpus and a proof that nothing normalizes authored text;
and an adversarial suite in which three attackers fail all four assessment
authority attacks against the real shipped gates. The tracer is green, the
adversarial suite is green, and the measured figures are in
`16A-TRACER-REPORT.md`.

What none of that can decide is whether the contract is legible and honest. A
green test proves a field is present and a refusal fires. It cannot tell you
that a capability profile's `known_limits` names the limitation a reader would
actually hit rather than a safe one; that a backburner trigger is a condition
someone could test rather than a phrase that will never fire; that the
unsupported-block copy a learner reads makes sense to a learner; or that the
seven new role labels mean, in English, what the roles are for. That judgment is
the freeze gate's actual subject, and an agent never signs it for itself.
  </what-built>
  <how-to-verify>
1. Read
   `.planning/phases/16A-semantic-capability-activity-contract/16A-TRACER-REPORT.md`
   end to end, and note every row in its nine-leg table that is not `passed`.

2. Run both suites yourself and watch them:

```
python tests/capability_stress_corpus_tracer.py
python tests/assessment_authority_adversarial.py
```

   Expected final lines: `TRACER: 18 passed, 0 skipped, 0 failed` and
   `ADVERSARIAL: 18 attempted, 18 refused, 0 succeeded`, exit code 0 from both.

3. Read the fifteen capability profiles in `capabilities.py` as prose. For each,
   answer in `16A-REVIEW.md`:
   - Does `known_limits` name a limitation you would actually hit, or a safe one
     that costs nothing to admit?
   - Does `offline_fallback` describe what a learner would really see with the
     network unplugged and scripting off?
   - Does `validation` name a check that exists, and could you run it?

4. Read the eight backburner entries. For each, answer:
   - Is the `trigger` a condition someone could test and notice, or a phrase
     that will never fire?
   - Does the `cost` sentence read like an honest estimate or like a
     discouragement?
   - Would you know, from the entry alone, what building it would involve?

5. Read the user-visible copy this phase added, as a learner would:
   - `This block needs a lesson feature this reader does not have. Its text is
     below, unchanged.`
   - `This image is not available on this machine. Its description is below.`
   - `This image lives outside this course and is not loaded here. Its
     description is below, and the link opens it.`
   For each: is it clear what happened, is it clear what to do, and does it
   sound like this product?

6. Read the seven new role labels: `Before this`, `Common mistake`,
   `Expert tip`, `Counterexample`, `From the source`, `Not settled`,
   `In short`. Would you know, seeing one on a page, what the block is for?
   Would you reach for the right one when authoring?

7. Open the built corpus in a plain Markdown viewer or a text editor, with no
   rendered HTML present. Build it first with:

```
python -c "import sys; sys.path.insert(0,'fixtures'); import lesson_capability_corpus as c; import tempfile; d=tempfile.mkdtemp(); print(c.build_all_16a(d)); print(d)"
```

   Read the medical evolving-case lesson and the disputed-timeline lesson as
   plain text. Answer:
   - Does the lesson make sense with no renderer at all?
   - Is the dated jurisdiction warning something you would act on correctly?
   - Does the disputed timeline read as genuinely open, or does one account feel
     like the answer?

8. Read plan `16A-09`'s summary. If it recorded an open leak finding in this
   phase's own new grammar, state in `16A-REVIEW.md` whether that finding should
   withhold the freeze.

9. Record your verdict in
   `.planning/phases/16A-semantic-capability-activity-contract/16A-REVIEW.md`
   as one of the literal words `accept`, `accept-with-findings`, or `reject`,
   followed by your answers above, followed by your name or initials and the
   date. `accept-with-findings` means the freeze may be written and the findings
   are carried into the freeze record's open-items list.

   No em dash characters anywhere in the file.
  </how-to-verify>
  <verify>
`16A-REVIEW.md` exists, carries one of the three literal verdict words, carries
answers to all of steps 3 through 8, and carries a signature and a date.
  </verify>
  <acceptance_criteria>
- `.planning/phases/16A-semantic-capability-activity-contract/16A-REVIEW.md`
  exists.
- It contains exactly one of the literal strings `accept`,
  `accept-with-findings`, or `reject` as its recorded verdict.
- It contains a named response for each of the fifteen capability profiles and
  each of the eight backburner entries.
- It contains a response for each of the three copy strings and for the seven
  role labels.
- It contains a response to step 8 about plan 16A-09's leak finding, or the
  sentence `no leak finding was recorded` if there was none.
- It carries a signature or initials and a date.
- It contains no em dash character.
  </acceptance_criteria>
  <reversibility rating="reversible">A review artifact. It records a judgment and
  changes nothing in the codebase.</reversibility>
  <resume-signal>Write `16A-REVIEW.md` with your verdict, then reply `accept`, `accept-with-findings`, or `reject`.</resume-signal>
</task>

<task type="auto">
  <name>Task 3: write the freeze record, or withhold it by name</name>
  <files>.planning/phases/16A-semantic-capability-activity-contract/16A-FREEZE.md, .planning/phases/16A-semantic-capability-activity-contract/16A-DECISIONS.md, .planning/phases/16A-semantic-capability-activity-contract/16A-VALIDATION.md</files>
  <read_first>
- `.planning/phases/16A-semantic-capability-activity-contract/16A-REVIEW.md` as
  written by Task 2, in full, including its verdict word.
- `.planning/phases/16A-semantic-capability-activity-contract/16A-TRACER-REPORT.md`
  in full, including its nine-leg table and its Open findings section.
- `.planning/phases/16A-semantic-capability-activity-contract/16A-09-SUMMARY.md`,
  for any open leak finding.
- `.planning/phases/16A-semantic-capability-activity-contract/16A-DECISIONS.md`
  in full, for the nine decisions the freeze record enumerates.
- `.planning/ROADMAP.md`, the Phase 16A entry, and the Phase 16B, 16C, and 17A
  entries, so the freeze record's scope statement says what it does not freeze.
- `.planning/phases/14B-graph-course-package-prototype/14B-FREEZE.md` and
  `.planning/phases/15B-quality-blueprint-acceptance/15B-FREEZE.md` if either
  exists, for the established freeze-record shape and the exact heading
  conventions `## Frozen at <phase>` and `## Freeze withheld`.
- `.planning/phases/16A-semantic-capability-activity-contract/16A-VALIDATION.md`
  in full.
- `16A-RESEARCH.md`'s Code Examples section, the eight-criterion
  proprietary-format gate and its verdict, for the record's format statement.
  </read_first>
  <action>
1. Re-run the evidence rather than trusting Task 1's record, because Task 2's
   review may have prompted a fix and a freeze record must describe the tree it
   is freezing:

```
python tests/capability_stress_corpus_tracer.py
python tests/assessment_authority_adversarial.py
python itembank.py guard .
```

   Then the full suite:

```
for t in tests/*.py; do python "$t" || exit 1; done
```

   Then re-verify the two golden SHA-256 values against
   `16A-PRECONDITION.md`'s Additivity baseline section.

2. Evaluate the five freeze legs. The freeze is written only when all five hold:
   - The stress-corpus tracer is green with zero failures and zero skips.
   - The adversarial suite is green with zero succeeded attacks.
   - `16A-REVIEW.md` exists, is signed, and its verdict is `accept` or
     `accept-with-findings`. A `reject` verdict or a missing signature is a
     failing leg.
   - Plan `16A-09`'s summary records no unresolved leak in this phase's own new
     grammar. A recorded leak is a failing leg: CAP-01's roles shipping with a
     disclosure hole is precisely the kind of thing a freeze makes expensive to
     fix later.
   - The full suite is green and both golden SHA-256 values are unchanged.

3. If every leg holds, write
   `.planning/phases/16A-semantic-capability-activity-contract/16A-FREEZE.md`
   opening with the literal heading `## Frozen at 16A` and carrying, in this
   order:
   - **What is frozen.** The complete published surface: the eleven
     `_CALLOUT_KINDS` members and the seven role tokens; the fourteen-entry
     `SEMANTIC_ROLE_CATALOG`; the required-semantic trailing marker and the two
     unknown-semantic behaviors with their exact copy; the four lesson
     directives `[SEMANTIC-PROFILE:]`, `[LESSON-LANG:]`, `[LESSON-DIR:]`, and
     `[EXAMPLE-ORDER:]` with their defaults; `capabilities.py`'s full symbol
     list with the fifteen profile names; `schemas/capability_profile.schema.json`;
     `MEDIA_COLUMNS` and the `[MEDIA: id]` reference form; `ACTIVITY_COLUMNS`
     and the five activity vocabularies; `RESPONSE_FORMS`; `OUTPUT_MODES` and
     `BACKBURNER_MODES`; `lesson_page`'s `mode`, `media`, and `activities`
     keywords; and every lint code this phase added, listed in full.
   - **What is NOT frozen.** Stated explicitly, following the
     prototype-before-freeze coupling clause the 15A and 15B freeze records use:
     this is not a visual system freeze, not a token freeze, not an information
     architecture or navigation freeze, not a notes or strategy freeze, not a
     learner-facing surface freeze, and not a course schema freeze. Phases 16B,
     16C, and 17A are named as the owners of each.
   - **The canonical format verdict.** One paragraph recording that the
     canonical lesson stays UTF-8 Markdown with an additive versioned semantic
     profile, that a proprietary or open-package canonical format stays
     rejected, and that none of the eight criteria in research report 04 section
     8 was met, citing `16A-RESEARCH.md`'s Code Examples section.
   - **Evidence.** The two suite final lines verbatim, the full-suite result,
     the guard result, the two golden SHA-256 values, and the review's verdict
     and signature.
   - **Open items, with owners.** Every item from `16A-TRACER-REPORT.md`'s Open
     findings section plus every finding the review recorded, each with a named
     owner and, where known, the phase that would close it. This list must
     include, by name: media rights enforcement deferred per `D-16A-8`; media
     integrity recomputation deferred; the annotated worked-example structure
     recorded as a Registered-tier enhancement per `D-16A-6`; the structured
     jurisdiction and date field deferred per `D-16A-7`; interface localization
     of the new labels and copy; every Phase 17A CSS handoff the earlier
     summaries recorded, including `.capability-static`, `.media-unavailable`,
     `.media-remote`, and `.stage`; and any scenario the tracer report marked
     `weaker proof`.

4. If any leg fails, write the same file opening instead with the literal
   heading `## Freeze withheld`, naming the failing leg or legs, what would
   close each, and stating that Phase 16A stays open. The string
   `Frozen at 16A` must appear nowhere in the file in that case, so a downstream
   precondition check cannot read a withholding as a freeze.

5. Append `## D-16A-10. Freeze scope` to `16A-DECISIONS.md`, recording in one
   paragraph what the freeze covers and what it explicitly does not, matching
   the freeze record's own two sections, so a later phase reading only the
   decisions file gets the same answer.

6. Finalize
   `.planning/phases/16A-semantic-capability-activity-contract/16A-VALIDATION.md`:
   - Complete the Per-Task Verification Map, confirming a row exists for every
     task in plans 16A-02 through 16A-10 and that every Status is filled.
   - Replace the Estimated runtime placeholder in the Test Infrastructure table
     with the measured full-suite figure from `16A-TRACER-REPORT.md`, and name
     the machine and Python version it was measured on.
   - Fill the Manual-Only Verifications table's Test Instructions cell with the
     steps from this plan's Task 2.
   - Resolve every Validation Sign-Off checkbox honestly. Set
     `nyquist_compliant: true` in the frontmatter only if every task in the
     phase has an automated verify or a recorded Wave 0 dependency, and set
     `status: validated` and `wave_0_complete: true` only if that is true.
     Leave any box unticked whose condition does not hold and say why beside it.

   No em dash characters anywhere in any file this task writes.
  </action>
  <verify>
  <automated>python -c "import sys,io; p='.planning/phases/16A-semantic-capability-activity-contract/16A-FREEZE.md'; s=io.open(p,encoding='utf-8').read(); frozen='## Frozen at 16A' in s; withheld='## Freeze withheld' in s; assert frozen != withheld, 'freeze record must carry exactly one of the two headings'; assert not (withheld and 'Frozen at 16A' in s), 'a withholding must not contain the frozen string'; print('freeze record shape ok:', 'frozen' if frozen else 'withheld')"</automated>
Expected: prints `freeze record shape ok: frozen` or
`freeze record shape ok: withheld` and exits 0. The degraded state this task
must prove rather than paper over is the withholding path itself: the record
carries exactly one of the two headings, never both, and a withholding never
contains the string a downstream precondition check greps for.
  </verify>
  <acceptance_criteria>
- `.planning/phases/16A-semantic-capability-activity-contract/16A-FREEZE.md`
  exists and contains exactly one of `## Frozen at 16A` or `## Freeze withheld`.
- When it carries `## Freeze withheld`, the string `Frozen at 16A` appears
  nowhere in the file.
- When it carries `## Frozen at 16A`, it has all five named sections, its
  What is NOT frozen section names Phases 16B, 16C, and 17A as owners, and its
  Open items section names at least the seven deferrals listed in step 3.
- `python tests/capability_stress_corpus_tracer.py` and
  `python tests/assessment_authority_adversarial.py` were both re-run in this
  task and their final lines are quoted verbatim in the freeze record.
- `for t in tests/*.py; do python "$t" || exit 1; done` exits 0.
- `python itembank.py guard .` reports `0 offending files`.
- The two golden SHA-256 values in `16A-PRECONDITION.md` are unchanged and are
  quoted in the freeze record.
- `16A-DECISIONS.md` contains the literal heading `## D-16A-10. Freeze scope`.
- `16A-VALIDATION.md` has no `(planner fills)` placeholder remaining, its
  Estimated runtime cell carries a measured figure with a named machine and
  Python version, and its frontmatter `status`, `nyquist_compliant`, and
  `wave_0_complete` values match what the sign-off boxes actually show.
- No file this task writes contains an em dash character.
  </acceptance_criteria>
  <reversibility rating="one-way">A freeze record is what plan 16B-01's,
  16C-01's, and 17A-01's precondition checks will assert against, and what later
  phases build their imports on. Reopening a frozen surface after those phases
  plan against it means renaming or reshaping a published contract. The judgment
  it requires is the blocking human review in Task 2 immediately above
  it.</reversibility>
  <done>Phase 16A is either frozen with its surface enumerated, its evidence
  recorded, and its open items owned, or held open with the missing leg
  named.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| tracer to shipped suites | A green phase tracer could mask a regression in the shipped parser, renderer, scorer, or evidence store if it does not run those suites itself. |
| fixture corpus to repository | Synthetic clinical and historical material enters version control and could drift toward real content. |
| freeze record to later phases | Whatever this file says is frozen is what plans 16B-01, 16C-01, and 17A-01 will assert against. |
| human review to freeze | A signature is the only thing standing between a green machine and an accepted claim about contract legibility. |
| portability scenario to the working tree | A scenario that deletes derived files could delete real ones. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-16A-10-01 | Spoofing | an agent self-certifying the contract-legibility review | high | mitigate | The review is a blocking `checkpoint:human-verify` producing a signed file with one of three literal verdict words; Task 3 fails the review leg on a missing signature or a `reject` verdict, and the freeze is withheld by name. |
| T-16A-10-02 | Repudiation | a freeze record claiming a leg that was not run | high | mitigate | Task 3 re-runs both suites, the full suite, and the guard rather than trusting Task 1's record, and quotes their final lines verbatim in the record. A failing leg produces a `## Freeze withheld` file in which the frozen string appears nowhere, asserted by the automated verify. |
| T-16A-10-03 | Tampering | a regression in the shipped runtime hidden behind a green phase tracer | high | mitigate | The tracer's `shipped_suite_check()` runs shipped suites as subprocesses before any scenario and skips rather than reports passes on a red result; the full suite runs again in Task 3; and both golden SHA-256 values are re-asserted a final time. |
| T-16A-10-04 | Tampering | the portability scenario deleting real files in the working tree | high | mitigate | The scenario runs entirely inside a fresh temporary tree, the acceptance criteria require every delete call to take a path derived from that root, and `git status --porcelain` is asserted to report no deleted file after the run. |
| T-16A-10-05 | Information Disclosure | a premature reveal in the medical evolving-case fixture | high | mitigate | The resolution carries a distinctive token asserted absent from the served bytes while the check is open and present in the canonical Markdown, riding on Phase 6.2's server-side gate truncation rather than a DOM hide. If only a static render is possible, the scenario is marked `weaker proof` and the freeze decision weighs it rather than the claim being made anyway. |
| T-16A-10-06 | Information Disclosure | real clinical, course, or exam material entering the repository through the medical or timeline fixture | high | mitigate | Both fixtures are literal fictional constants with invented jurisdictions, dates, and events; a comment above the medical constant states it is not clinical guidance; and `python itembank.py guard .` reporting `0 offending files` is an acceptance criterion on every task. |
| T-16A-10-07 | Repudiation | a derived view treated as the readable copy, undetected because nothing deleted it | high | mitigate | `scenario_portability` deletes every derived artifact, asserts the canonical files' SHA-256 are unchanged, asserts every capability's meaning is findable in the raw Markdown bytes, and asserts every derived file rebuilds to its recorded digest. |
| T-16A-10-08 | Repudiation | a tracer report carrying budget numbers presented as measurements | medium | mitigate | The action forbids any figure that was not produced by the run, requires the machine and Python version be named, and the acceptance criteria assert no target or budget number appears. |
| T-16A-10-09 | Elevation of Privilege | an unresolved leak in this phase's new grammar frozen into a published contract | critical | mitigate | Plan 16A-09's recorded leak finding is an explicit freeze leg in Task 3 step 2, and a recorded leak withholds the freeze by name rather than being carried as an open item. |
| T-16A-10-10 | Tampering | supply chain: a third-party dependency introduced by this plan | high | mitigate | None is added; every new file is standard library only. Per `PLANNING-DIRECTIVES.md` section 4a the absence of dependencies is explicitly not the mitigation: the mitigation is that any dependency ever added here is vendored at a pinned version with a recorded checksum and a named license review, following the KaTeX precedent in `09-03-PLAN.md`. |
</threat_model>

<out_of_scope>
Refused by this plan, by name, so no adjacent temptation is decided by executor
judgment:

- Any change to `model.py`, `surfaces/lesson.py`, `capabilities.py`,
  `runtime.py`, or `evidence.py`. If the review or a scenario finds a defect,
  the fix is a new plan and the freeze is withheld, not a task added here.
- Any new grammar, vocabulary, lint code, or schema. Every one of them was
  settled in plans 16A-01 through 16A-09.
- Any softened assertion to make a leg pass. A leg that cannot be exercised is
  marked `weaker proof` or `not run` and the freeze decision weighs it.
- Any visual decision. Phase 17A owns the token freeze and the same-flow
  three-direction comparison that must precede it.
- Freezing anything Phase 16B, 16C, or 17A owns. The freeze record's What is NOT
  frozen section states the boundary explicitly.
- Closing any of the deferred items. Media rights enforcement, media integrity
  recomputation, the annotated worked-example structure, the structured
  jurisdiction field, interface localization, and the Phase 17A CSS handoffs are
  recorded with owners, not resolved.
</out_of_scope>

<flagged_assumptions>
- **PORT-01's adjacency and ordering probe rows are resolved by this plan** as
  explicit criteria carried in `must_haves.truths`: adjacency as the
  delete-and-rebuild cycle producing equal derived bytes and an untouched
  canonical side, and ordering as two preamble-section permutations parsing to
  equal dicts across all five readers.
- **Whether the medical case can be proven against served bytes is not known at
  plan time.** The stronger proof needs a driven gated sitting inside the tracer.
  Task 1 requires the stronger proof if it is reachable and requires the weaker
  one to be labelled `weaker proof` if it is not, rather than letting the
  scenario claim a server-side truncation it did not exercise.
- **A recorded leak from plan 16A-09 withholds this freeze.** That is a judgment
  this plan makes rather than one a requirement states, and the reason is
  recorded: CAP-01's fourteen roles becoming a published contract with a
  disclosure hole in one of them is a defect that gets more expensive to fix
  after every downstream phase plans against the freeze.
- **`accept-with-findings` permits the freeze.** The alternative reading, that
  any finding withholds it, would make the review a pass or fail gate and would
  push a reviewer toward `accept` to avoid blocking. Findings are carried into
  the freeze record's open-items list with owners, which is where
  `PLANNING-DIRECTIVES.md` section 3a's accepted-recommendation discipline
  expects them.
</flagged_assumptions>

<summary_obligations>
`16A-10-SUMMARY.md` records: the nine freeze-gate legs and the result of each,
including any marked `weaker proof` and why; whether the medical case was proven
against served bytes or only a static render; the measured figures from
`16A-TRACER-REPORT.md`, repeated, with the machine and Python version; the two
golden SHA-256 values as re-verified one final time; the review's verdict, its
signature, and every finding it recorded; whether plan 16A-09 had recorded a
leak finding and how the freeze decision weighed it; whether the freeze was
written or withheld and, if withheld, the exact failing legs; the full open-items
list with owners as written into the freeze record; the final state of
`16A-VALIDATION.md`'s frontmatter flags and which sign-off boxes were left
unticked and why; which truth was verified by which command with the command's
actual stdout; and any deviation from this plan with its reason.
</summary_obligations>

<output>
Create
`.planning/phases/16A-semantic-capability-activity-contract/16A-10-SUMMARY.md`
when done.
</output>
