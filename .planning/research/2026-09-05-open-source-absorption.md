# Open-source absorption pass: Canvas, Moodle, PrairieLearn, and open corpora

**Research date and access date for all web sources:** 2026-09-05

**Prompt:** Weibao, in chat, 2026-09-05: look at open-source systems such as
Canvas and see whether anything is worth absorbing.

**Scope:** a prior-art absorption pass, not a product decision and not a plan.
Sections label **Observed fact**, **Inference**, and **Recommendation** in the
manner of the Phase 16 streams. Recommendations bind nothing until they are
accepted; the dispositions they produced are in `IDEA-LEDGER.md`
(`IL-20260905-01` to `IL-20260905-05`).

## 1. What was already covered, so this pass did not redo it

**Observed fact.** The repository's own research already samples this
landscape heavily. Occurrence counts across `.planning/research/`: Anki 208,
Runestone 65, FSRS 50, H5P 45, Open edX 21, Moodle 22, PrairieLearn 15,
mdbook 7, OpenStax 4, LibreTexts 3. Canvas LMS itself is covered outside the
research directory, in `ROADMAP-ARCHIVE.md` Phase 999.4 (LTI surface,
completed 2026-08-11) and in the `REQUIREMENTS.md` backlog block at line 215.
Moodle GIFT ships as the interchange format (`PROJECT.md` line 272), and a
Moodle 4.x specimen was already absorbed once, for activity-purpose tokens
(`IDEA-LEDGER.md` line 751).

**Observed fact.** None of PrairieLearn, Runestone, H5P, FSRS, LibreTexts,
OpenStax, QTI, or Common Cartridge has an `IDEA-LEDGER.md` entry. Their
findings live only inside research prose and the Phase 16 synthesis tables
(`14-synthesis.md` lines 388 and 740, which park full QTI, SCORM, OLX, and
H5P behind a named consumer).

**Inference.** The landscape is well surveyed; what is thin is durable
disposition. A survey that repeated the landscape would produce nothing. The
value left is in the two or three places where an open-source system does
something itembank has half-built, and in writing those down where a future
agent will find them.

**Recommendation.** Treat this pass as narrow: four findings, one licence
rule, and no new landscape prose.

## 2. Certainty-based marking, against a field itembank already writes

**Observed fact, itembank side.** `confidence` is captured end to end and read
by nothing. It is a CLI flag (`surfaces/cli.py:988`, values high, medium,
low), a daemon field validated against `CONFIDENCE_LEVELS`
(`surfaces/daemon.py:3608`), an evidence field (`evidence.py:448`), a column
in the SQLite index (`evidence.py:1150`), and a migration default
(`surfaces/migrate.py:344`). `REQUIREMENTS.md` EVID-07 asked for exactly this
and said so plainly: recorded "whether or not anything reads them yet".
Nothing does. A grep for `confidence` across `retention.py`, `selection.py`,
`blueprint.py`, `progress_claims.py`, and `auditor.py` returns no consumer.
`surfaces/quiz.py:305` passes `confidence=None`, so the offline page does not
even collect it.

**Observed fact, Moodle side.** Moodle's question engine treats grading
behaviour as a pluggable axis separate from the question, and ships
certainty-based marking (CBM) as one behaviour: the learner states how sure
they are (not very, under 67 percent; fairly, over 67; very, over 80), and the
mark is adjusted so that a confident wrong answer costs more than a hedged
one. Community behaviours extend it with per-question learner comments.

**Observed fact, itembank side again.** `REQUIREMENTS.md:1116` already names
the exact failure CBM is designed to expose, in the anti-pattern table:
keyword matching "cannot separate a correct explanation from a confident wrong
one with the right nouns".

**Inference.** The cheap half of CBM is already paid for. What Moodle supplies
is the reading: confidence crossed with correctness is four cells, and the
interesting one is confident-and-wrong, which is a different remediation
problem from unsure-and-wrong. That reading needs no new field, no new item
type, and no new format surface.

**Inference on the boundary.** Moodle's version adjusts the *mark*. That half
sits badly here: `REQUIREMENTS.md` lines 972 to 981 refuse a mastery
percentage and demand stated denominators, and a certainty-weighted mark is a
score whose derivation is not visible in the numerator. The diagnostic half
carries none of that cost.

**Recommendation.** Absorb the reading, not the marking. Surface
confident-and-wrong as a distinct error signal available to selection and to
the blueprint report, with its own denominator, and leave the verdict itself
untouched. If a weighted mark is ever wanted it is an additive extension
inside the one scorer under `IL-20260815-05`, and it needs its own argument.
Collect the field on the quiz surface first, since a signal nobody can produce
cannot be read. Registered as `IL-20260905-01`.

## 3. Canvas outcome rollups, mostly as a counter-example

**Observed fact.** Canvas LMS is AGPLv3, published at `instructure/canvas-lms`.
Its outcomes API computes mastery by a named calculation method, the
documented ones including `decaying_average`, `n_mastery`, `highest`, and
`latest`. Its New Quizzes item API distinguishes a `QuestionItem`, a
`BankItem` (an item that lives in a bank), and a `BankEntry` (a pinned
instruction to draw a random selection from a bank into a quiz).

**Inference.** Three of the four calculation methods are exactly what this
project refuses. `decaying_average` produces a single number whose denominator
is unrecoverable, which is the collapse `IDEA-LEDGER.md:800` forbids and which
`blueprint.py`'s `uncertainty_for()` was written to avoid.

**Inference.** `n_mastery` is different in kind, and the difference is worth
naming. N of the last M attempts at or above a threshold is a countable claim
with both numbers visible. It is not a percentage, it degrades honestly when M
is small (which `uncertainty_for()` already bands), and it is expressible in
the vocabulary `progress_claims` uses. Canvas is a useful specimen here
precisely because it puts an honest method and three dishonest ones behind one
configuration switch.

**Inference, timing.** The G5 default rollup choice is currently owed to
Weibao (`17B-GATES.md` row G5, provisional recorded 2026-09-01). This finding
is input to that decision and nothing more; ROLLUP-DIM and ROLLUP-MAP are
about the shape of the tree, `n_mastery` is about what a leaf may claim, and
they are orthogonal.

**Recommendation.** Record `n_mastery` as the one absorbable rollup form and
`decaying_average` as a named rejection with its reason, so neither is
re-argued. `IL-20260905-02` (registered) and `IL-20260905-03` (rejected).

**Recommendation, not pursued.** `BankEntry` and Canvas stimulus grouping map
onto work itembank already has (`## SCENARIO`, blueprint sampling), and
`ROADMAP-ARCHIVE.md:223` already records the Canvas item-bank failure this
project deliberately avoided, where editing an answered item breaks the
bank-to-quiz link. No new disposition.

## 4. The question as a generator (PrairieLearn)

**Observed fact.** PrairieLearn's core idea is that a question is a generator:
`server.py` produces randomized variants of itself and grades each variant,
so one authored question yields many. It is in use across roughly 800 courses
at 20 universities, and it publishes 15 shared OER courses and question banks
covering calculus, linear algebra, physics, statics, and CS. The Community
Edition is AGPLv3, with parts MIT and an Enterprise directory under a separate
proprietary licence. The OER banks are reachable only through a free account
and an instructor course space, not as a downloadable corpus.

**Inference.** The generator idea is the strongest fit of anything surveyed to
the one subject with no course yet, Math 1400, where the practice value is in
many instances of one form. But runtime generation collides with three settled
things at once: stable item identity and `content_fingerprint()`, evidence
keyed per item id, and the rule at `IDEA-LEDGER.md:843` that a shuffled variant
is not a new item.

**Inference.** The collision disappears if generation happens at authoring
time. Expanding one parameterized form into N concrete items, each minted with
its own id and hash and written into the bank, adds no runtime concept, no
second parser, and no second scorer. It is an authoring feature that emits
ordinary items, and `author-bank`'s write, lint, fix loop already validates
the output.

**Inference, licence.** Neither the code nor the OER content is takeable. AGPL
is the same one-way distribution problem that parked `ebooklib` in
`IL-20260828-05` and was decided as `D-14C-2`, and Phase 18 ships a packaged
app to other people.

**Recommendation.** Register the generator idea with the authoring-time
boundary stated as part of the proposal, not as a later caveat. Take nothing
but the idea. `IL-20260905-04`.

## 5. Open-licensed corpora, the actionable one

**Observed fact.** OpenStax publishes College Algebra and Elementary Algebra
free online, and LibreTexts mirrors them as remixable bookshelves. Licensing
is per title and not uniform: OpenStax's own licensing article describes the
library as CC BY-NC-SA, while individual titles and the LibreTexts mirrors are
commonly CC BY. Instructor DOCX downloads exist behind an educator account.

**Observed fact.** `STATE.md` records that no Math 1400 or CSCI 1100 course
exists yet, and that the one real sitting to date was EMT.

**Inference.** This is the only finding in the pass that is content rather than
mechanism, and it is the one that unblocks something. A CC-licensed algebra
text is a legitimate bound source with a rights answer that can actually be
recorded, unlike the AAOS-derivative EMT material whose accepted risk is
already on the books. The rights grants are per operation and unknown rights
stay restrictive, so the licence must be read per title at binding time and
never inferred from the publisher. NC matters: it constrains nothing for
Weibao's own study and would constrain a packaged redistribution, which is the
same Phase 18 asymmetry as the AGPL finding.

**Recommendation.** When Math 1400 is built, bind an OpenStax or LibreTexts
algebra title as a first-class source through the normal discovery and binding
path, with the licence read from the title itself and recorded in rights
state. Do not bulk-import; the source-to-course path already covers direct
reading as a treatment. `IL-20260905-05`.

## 6. One cross-cutting rule, worth stating once

**Observed fact.** Every substantial open-source system in this space is
copyleft: Canvas AGPLv3, Moodle GPLv3, PrairieLearn CE AGPLv3, and
`ebooklib` AGPL, already parked on those grounds. `COURSE-SHELL-TEMPLATE.md`
line 336 already states the practice for the one specimen it used: "Nothing
from the specimen is vendored. Moodle core is GPLv3".

**Inference.** That sentence is a general rule written in one file about one
specimen. Since 2026-08-14 made external installation a supported goal and
Phase 18 packages a desktop app, the asymmetry it protects against now applies
to every future absorption, not just that one.

**Recommendation.** State it generally: absorb observed behaviour, format
semantics, and vocabulary from copyleft ed-tech; never vendor the code, and
never assume a licence from a publisher's reputation. This is a restatement of
`SUPPLY-CHAIN-POLICY.md` section 2.4 and `D-14C-2` rather than a new rule, and
it is recorded as the boundary clause on `IL-20260905-04` rather than as a
sixth entry.

## 7. What was looked at and dropped

- **H5P, QTI 3.0, Common Cartridge, SCORM, OLX.** Already parked behind a
  named consumer by `14-synthesis.md` line 740 and by `V2-INT-01`. Nothing in
  this pass supplies a consumer, so the parking stands.
- **FSRS and Anki internals.** Covered at length already; the boundary
  (Anki owns card review, itembank owns objective scheduling) is settled by
  `SCHED-03` and the 2026-08-22 note.
- **Runestone Parsons problems.** Already mapped to `build` items by
  convention, `ROADMAP-ARCHIVE.md:363`.
- **nbgrader and code autograders.** Not pursued. CSCI 1100's AI-use ban is an
  accepted risk on the books, and an execution sandbox is a large surface for
  a course that does not exist yet.

## 8. Filing note

`IL-20260828-01` through `IL-20260828-05` are appended below the `## Rejected`
heading although four of the five carry a Registered or Parked disposition.
This pass did not move them, because the ledger is append-only and moving
records is riskier than the confusion it fixes. The four registered entries
from this pass are filed at the end of `## Open and registered` and the one
rejection at the end of `## Rejected`, which is where the file's own convention
puts them.
