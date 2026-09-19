# Structured question presentation audit

**Status:** bounded cross-subject audit and immediate repair decision, 2026-09-15.

**User direction:** show arguments and comparable depth-bearing material in a
stacked, math-like form, one meaningful unit below another. Audit the same need
across other genres and courses.

## Finding

The shared defect is flattening, not missing decoration. A question can retain
the right words and still make the learner reconstruct its structure from a
dense paragraph. The accepted Phase 16 capability catalog already requires
worked steps, comparisons, diagram relations, staged evidence and transfer to
remain semantically explicit. Quiz stimuli need the same rule.

The current renderer escapes question text safely but lets HTML collapse stem,
option and row whitespace. The current math repair adds local KaTeX, but formula
rendering alone does not separate premises, code lines, events, procedure steps
or paired language forms. Existing MATH 1400 Q5 prompts explicitly name an
argument, quote its sentences and mark the conclusion with "Therefore". That is
enough for a bounded presentation enhancement without changing course content.

## Cross-subject matrix

| Genre or course use | Separately scannable units | Fitting presentation | Plain and accessible floor | Misuse to prevent | Route |
|---|---|---|---|---|---|
| Logic arguments and proofs | premises, inference rule, conclusion, validity and truth checks | labeled stacked rows, then an argument diagram only when relations matter | ordered text with explicit premise and conclusion labels | assigning roles to unlabeled sentences or implying that a true conclusion proves validity | immediate argument formatter, then diagram capability |
| Mathematics and quantitative work | givens, transformation steps, reasons, result, units | display math with one transformation per row and optional reason column | authored lines with formula source and linear reading order | hiding an invalid step through visual alignment or animation | math capability and worked-example role |
| Computer science | prompt, code lines, trace state, output, explanation | dedicated code block plus state table or trace | fenced code with preserved indentation and a text trace | compressing executable syntax into prose or equating output with understanding | existing code-box preference and CS Dojo prototype |
| EMT, health and laboratory procedure | scene or starting state, observation, action, reason, consequence, safety warning | ordered procedure or staged case with fixed disclosure | labeled ordered steps with prior information retained | presenting screen success as physical competence or inferring unsafe missing steps | worked example and staged-reveal capabilities |
| History and social science | dated events, actor, claim, evidence, counterclaim, uncertainty | timeline for chronology, claim-evidence groups for argument | ordered event list and headed claim sections with citations | erasing disputed dates, causal uncertainty or source disagreement | timeline, comparison and source roles |
| Literature, philosophy and source reading | excerpt, speaker or author claim, evidence, interpretation, objection | excerpt block followed by claim-evidence-response groups | quoted source with locator and headed analysis | blending source words with generated interpretation | source excerpt and comparison roles |
| Language learning | source script, pronunciation or transliteration, meaning, grammar role, example | stacked labeled fields or paired rows | correct language metadata and explicit labels in reading order | relying on color, losing diacritics, or forcing side-by-side layout at narrow width | glossary and localization capability owners |
| Dialogue, interview and scenario | speaker turn, stage, new information, response or consequence | speaker-labeled turns or fixed staged reveal | chronological transcript with headings | inventing a speaker, reordering turns or hiding required context | case and staged-reveal capabilities |
| Comparison and data interpretation | common dimensions, each case or method, discriminator, tradeoff | table at wide width, repeated labeled groups when narrow | headers and row relations remain programmatic | incomparable columns, horizontal overflow or giving away the keyed discriminator | comparison capability |

## Decision

The immediate repair stays presentation-only:

1. Preserve deliberate newlines in quiz stems, options and row labels.
2. When a stem explicitly says it contains an argument, quotes two or more
   sentences and marks its last sentence with Therefore, Thus or Hence, show
   the sentences as labeled premise and conclusion rows.
3. Keep the exact authored text in the page data and as the no-JavaScript
   fallback. The adapter creates text nodes, never raw HTML.
4. Do not change bank files, hashes, keys, scoring, evidence or disclosure.
5. Route richer formats through the existing semantic catalog and require a
   representative fixture before promotion.

This is narrow enough to repair the observed MATH 1400 prompt without a format
migration. It also creates a safe authoring floor for any course: deliberate
line breaks survive even when no specialized renderer exists.

## Verification gate

- Parser fixture proves multiline stems retain their authored line breaks.
- Quiz output carries the universal structure adapter in served and offline
  modes and retains safe escaping.
- Argument rows have list and list-item semantics, readable labels and a
  one-column narrow layout.
- The adapter calls no scorer, submit route or evidence writer.
- Math rendering still runs after structure enhancement and ordinary non-math
  quizzes load no KaTeX assets.
- Browser inspection uses the current synthetic argument and the existing MATH
  1400 prompt. Automated checks do not close human visual or screen-reader
  acceptance.

## Deferred work with owners

- **Code blocks and traces:** IL-20260912-02 and CS Dojo owners. The bounded
  [code-question depth audit](code-question-depth-audit-2026-09-16.md) now
  separates faithful display, orientation, tracing, manipulation and
  construction. Promotion still needs valid source, indentation, syntax checks
  and a no-execution fallback.
- **Aligned derivations:** math and worked-example owners. Promotion needs step
  reasons, formula source, overflow behavior and screen-reader reading order.
- **Timelines, cases and dialogues:** existing timeline and staged-reveal
  capability owners. Promotion needs fixed source order, uncertainty and an
  equivalent linear representation.
- **Bilingual and dense comparison layouts:** localization and comparison
  owners. Promotion needs mixed-direction, CJK, diacritic, narrow-width and
  table-header fixtures.

## Authority and recovery

The bank remains the durable object and exact source of question text. The
runtime remains the only scorer and disclosure authority. The HTML structure is
derived and disposable. Removing the adapter restores the original readable
text without migrating content or evidence. Any recognizer that produces a
false semantic label must be disabled and replaced by the plain fallback.

## Reconciliation, 2026-09-18

The immediate argument, multiline, math, symbol-help, hint-copy, and question
focus work is present in the consolidated dirty candidate and passes its focused
suites. Code D1/D2 now has a separate disposable prototype. Aligned
derivations, timelines, cases, dialogues, production bilingual layouts, and
dense comparison layouts remain routed to their existing owners. No prototype
or automated check closes human visual, touch, or screen-reader acceptance.
