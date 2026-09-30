# Synthetic question-family journeys

All content is invented for a disposable prototype. No learner evidence belongs here.

## Static case

A fictional counter starts at 3. A rule adds 2 once. Answer the result first,
then choose the reason. In a formal sitting the runtime withholds feedback
until the sitting closes. The two prompts remain usable in plain Markdown.

Q1. What does the fictional counter show after one application?
[HASH: sha256:ee9a9d05fc75ea73]
[ID: a200000000000001]
[TYPE: mc]
[OBJECTIVE: synthetic:counter-result]
[PAIR: a2-counter]
A) 5
B) 6
C) 3
D) 7
CORRECT: A
WHY BEST: Adding two to three gives five.
KEY DISCRIMINATOR: Apply the rule once.
SECOND-BEST: C. Keeping three would fit a rule that does nothing.
DISTRACTOR ANALYSIS:
- A) Correct: one addition gives five.
- B) Six would be correct if the rule doubled the starting value.
- C) Three would be correct if the rule left the starting value unchanged.
- D) Seven would be correct if the rule added four once.
TRAP: Do not substitute doubling for addition.
CONFIDENCE: high

Q2. Which reason supports your committed counter response?
[HASH: sha256:81e571334f4393e5]
[ID: a200000000000002]
[TYPE: mc]
[OBJECTIVE: synthetic:counter-reason]
[PAIR: a2-counter]
A) The rule doubles the starting value.
B) The rule adds two to the starting value once.
C) The rule keeps the starting value unchanged.
D) The rule adds four to the starting value once.
CORRECT: B
WHY BEST: The stated rule is addition, not multiplication.
KEY DISCRIMINATOR: Identify the stated operation.
SECOND-BEST: D. Adding four would fit two applications of the stated rule.
DISTRACTOR ANALYSIS:
- A) Doubling would be correct for a rule that multiplies by two.
- B) Correct: the rule adds two once.
- C) No change would be correct for an identity rule.
- D) Adding four would be correct if the rule were applied twice.
TRAP: An operation can be familiar without being the stated one.
CONFIDENCE: high

Q3. Complete both blanks: the fictional flag is {{color}} and has {{count}} stripes.
[HASH: sha256:22f26525ae0a86d6]
[ID: a200000000000003]
[TYPE: fill]
[OBJECTIVE: synthetic:flag]
[FIELDS: [{"id":"color","label":"Flag color","kind":"text","accepted":["blue"],"case_sensitive":false,"whitespace":"trim"},{"id":"count","label":"Stripe count","kind":"numeric","answer":"2.5"}]]
WHY BEST: The invented flag is blue with two and a half stripes.
KEY DISCRIMINATOR: Each blank has its own stable field ID.
TRAP: Do not interchange fields.
CONFIDENCE: high

Q4. Select the statements that support the fictional rule, not the starting value.
[HASH: sha256:3be17ea619c11d63]
[ID: a200000000000004]
[TYPE: multi]
[OBJECTIVE: synthetic:evidence]
[SELECT: 2]
A) Rule sentence: add two once.
B) Initial-state sentence: the counter starts at three.
C) Operation sentence: use addition rather than doubling.
CORRECT: A, C
WHY BEST: The rule and operation sentences describe the transformation.
KEY DISCRIMINATOR: Select rule evidence rather than initial state.
DISTRACTOR ANALYSIS:
- A) Correct: this sentence supplies the rule.
- B) The initial-state sentence would be correct when asked for evidence of the starting value.
- C) Correct: this sentence identifies the operation.
TRAP: Relevant context is not always evidence for the requested claim.
CONFIDENCE: high
