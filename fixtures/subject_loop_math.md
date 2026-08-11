# Subject-loop Math fixture (synthetic, Phase 9)

Fully invented teaching content for the subject-invariant loop roundtrip. It
is not derived from any real course, exam, or textbook.

## LESSON

### Linear Growth

Context before the action: a quantity that changes by a fixed amount each
step grows linearly. Its value after $n$ steps is the starting value plus
$n$ times the step size.

The same idea in display form:

$$
v_n = v_0 + n \cdot d
$$

A prediction check follows the context: decide which statement is true
before reading the key. The step size is the constant that separates one
value from the next.

Q1. Which statement is true for linear growth?   (difficulty: application)
[LESSON-REF: Linear Growth]
[OBJECTIVE: math:sequences.linear]

A) The difference between consecutive values is constant
B) The ratio between consecutive values is constant
C) Each value doubles the previous one
D) Values approach a fixed ceiling

CORRECT: A

WHY BEST: Linear growth adds the same step size each time, so consecutive
differences are equal; a constant ratio is exponential, not linear.

KEY DISCRIMINATOR: The learner must name the additive invariant, not the
multiplicative one.

DISTRACTOR ANALYSIS:
- A) Correct: equal consecutive differences are the signature of linear growth.
- B) A constant ratio is geometric growth; it would be correct if the question asked about doubling sequences.
- C) Doubling is one geometric case; it would be correct if the question asked about exponential growth.
- D) A fixed ceiling is bounded growth; it would be correct if the question asked about a limiting process.

TRAP: Confusing the additive step with the multiplicative ratio.

CONFIDENCE: high
