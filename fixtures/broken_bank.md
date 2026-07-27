# Broken bank (synthetic, deliberately defective)

Every item below is wrong on purpose. `itembank lint fixtures/broken_bank.md`
must report each defect, and CI asserts it does. If a change to the linter makes
this file pass, the linter regressed.

Q1. SELECT disagrees with CORRECT: says pick two, keys three.
[TYPE: multi]
[SELECT: 2]

A) One
B) Two
C) Three
D) Four
E) Five

CORRECT: A, B, C

WHY BEST: Placeholder.

TRAP: Placeholder.

CONFIDENCE: high

Q2. CORRECT names an option that does not exist.

A) One
B) Two
C) Three
D) Four

CORRECT: F

WHY BEST: Placeholder.

TRAP: Placeholder.

CONFIDENCE: high

Q3. A row is assigned to a category that was never declared.
[TYPE: table]
[CATEGORIES: Alpha | Beta]

ROW) First thing :: Alpha
ROW) Second thing :: Gamma

WHY BEST: Placeholder.

DISTRACTOR ANALYSIS:
- Placeholder bullet.

TRAP: Placeholder.

CONFIDENCE: high

Q4. A build list with a duplicate step.
[TYPE: build]

STEP) Same
STEP) Same

WHY BEST: Placeholder.

DISTRACTOR ANALYSIS:
- Placeholder bullet.

TRAP: Placeholder.

CONFIDENCE: high

Q5. No WHY BEST field, no TRAP field, low confidence, and distractors that never say when they would be correct.

A) First option
B) Second option
C) Third option
D) Fourth option

CORRECT: A

DISTRACTOR ANALYSIS:
- A) Correct.
- B) This is simply wrong.
- C) This is also wrong.
- D) Wrong as well.

CONFIDENCE: low

Q6. No WHY BEST field, no TRAP field, low confidence, and distractors that never say when they would be correct.

A) First option
B) Second option
C) Third option
D) Fourth option

CORRECT: A

DISTRACTOR ANALYSIS:
- A) Correct.
- B) This is simply wrong.

CONFIDENCE: low

Q9. Explain, in your own words, why the residual matters at the far end of the distribution system.
[TYPE: short]

RUBRIC:
- Mentions contact time

TRAP: Reciting the number instead of explaining what it protects against.

CONFIDENCE: high
