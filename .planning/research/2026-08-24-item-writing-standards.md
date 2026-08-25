# Item-writing standards, and what they do and do not govern

Researched 2026-08-24, prompted by Weibao asking whether recognized national
testing bodies publish requirements about making answer options mutually
exclusive and not open to misinterpretation.

**Reading rule for this file.** Every source below was fetched and checked.
Where something could not be verified it says so, and nothing is attributed to
a source that was not read. The negative findings are the most useful part: they
stop later work citing authorities that do not say what we would want them to.

## Sources

| Source | Publisher | Free | URL |
|---|---|---|---|
| Item-Writing Guide, *Constructing Written Test Questions for the Health Sciences*, 6th ed | NBME | yes, no login | https://www.nbme.org/institutions/nbme-item-writing-guide/ |
| *Standards for Educational and Psychological Testing* (2014) | AERA, APA, NCME | yes, open access | https://www.testingstandards.net/open-access-files.html |
| EMT Examination Specifications / Test Plan | NREMT | yes | https://nremt.org/getmedia/4cb170ab-35fa-4ec0-a76c-634847005bc4/EMT-Test-Plan_Public |
| Haladyna, Downing and Rodriguez (2002), review of multiple-choice item-writing guidelines | Applied Measurement in Education 15(3) | publisher paywalled; ERIC record EJ660246 | https://eric.ed.gov/?id=EJ660246 |
| National EMS Education Standards (2021) | NHTSA | yes | https://www.ems.gov/ |

## What each source actually governs

**NBME governs item craft.** Two rules answer Weibao's question directly:
"Avoid overlapping options. Ask for minimum or maximum value to avoid multiple
correct answers", and the homogeneity rule, that options "all directly address
the lead-in in the same manner and can be rank ordered along a single
dimension". Its technical-flaw table also names absolute terms, vague frequency
words, negatively structured stems, non-parallel options, none-of-the-above,
grammatical cueing, and the correct answer standing out by length. NBME uses
one-best-answer only, and recommends against select-all-that-apply.

**Haladyna guideline 22 states the same rule most crisply:** "Keep choices
independent; choices should not be overlapping."

**NREMT governs structure and scoring, and is binding for EMT.** Multiple
Choice is one correct of exactly four options. Multiple Response is two correct
of five, or three of six, with exactly three incorrect. And the scoring rule,
quoted: "All items are scored dichotomously; that is, candidates receive full
credit for a correct response. No credit is provided for a partially correct
response." The test plan also names Options Table, Build List and Drag-and-Drop,
so the real examination is NOT all multiple choice, and itembank's five
corresponding item types already match it.

**The National EMS Education Standards govern curriculum, not items.** Verified
mechanically: the 2021 document was extracted in full, 6,592 lines, and grepped
for "distractor", "item writing", "test item" and "multiple choice". Zero
occurrences of any. It is the right source for objectives and sequence and the
wrong source for item construction. Do not cite it for the latter.

**AERA/APA/NCME governs process, not craft.** Standards 4.7 to 4.9 require a
documented item development and review process, empirical analysis, and expert
review that identifies material "likely to be inappropriate, confusing, or
offensive". They never say to make options mutually exclusive. What they oblige
is that we HAVE a review process and can show it.

## Could not verify

- The adopted 2021 NCCA accreditation standards, or whether they are free. Only
  a September 2021 draft revisions PDF is publicly reachable. Nothing in this
  file is attributed to NCCA.
- NREMT's internal item-writing style guide. Its own test plan refers to
  "adherence to style guidelines" but the guide is not published.
- The Haladyna paper on its publisher's host; a university-hosted copy was read
  and matched the ERIC abstract.

## What this means for the linter

Three tiers, and the split matters more than the list: a lint rule with a high
false-positive rate is worse than no rule, because it teaches the author to
ignore the linter.

**Tier 1, mechanically checkable, suitable as errors.** All-of-the-above and
none-of-the-above option text; absolute terms as standalone words; negatively
structured stems; NREMT option counts per type; overlapping numeric ranges,
when every option parses as a number or range and bailing out otherwise; the
key being longest by a margin; duplicate or near-duplicate options; grammatical
cueing in its narrow forms, article agreement and mixed singular/plural.

**Tier 2, heuristic, suitable as suppressible warnings.** Vague phrasing such as
"may", "usually", "is associated with"; non-parallel grammatical structure;
option-length variance generally; convergence, where a small set of terms
recombines across options.

**Tier 3, needs judgement, must not be a lint rule.** Whether options are
mutually exclusive IN MEANING, which is Weibao's actual question; homogeneity
and single-dimension rank ordering; whether a distractor is plausible to a naive
learner; whether an option is defensibly second-best rather than ambiguously
also-correct.

Tier 3 belongs to a model-assisted review pass whose output is advisory and
human-accepted. That is not a special case: it is the standing rule that a model
proposes and the human or the runtime settles.

## The check we are not doing, and should

Empirical distractor analysis. Flag any distractor chosen by zero learners
across N attempts. It needs no language model and no new authority, only the
evidence store that already exists, and it is the strongest signal available
about whether an option is doing any work.

## On per-option feedback

No source addresses it. Post-answer per-option rationale is instructional
design, not certification item-writing. NBME, NREMT, Haladyna and the AERA
Standards are all silent. It is therefore a free design choice, constrained only
by our own disclosure rule: whatever practice mode shows, exam mode must stay
silent to preserve fidelity to how the real examination behaves.
