# Boundary workshop (synthetic)

Original synthetic teaching and questions for a coding-learning integration
fixture. No real course, assessment, or proprietary platform lesson is used.
Prerequisites: Python functions, lists, for loops, if statements and return.
This is a draft practice treatment, not a certification or mastery claim.

## LESSON

### Ask the boundary question

An ordinary value rarely exposes a boundary bug. Pick three examples: just
below the cutoff, exactly equal to it, and just above it. Decide which belong
before writing a comparison. This works because equality is the only case
where an inclusive comparison and its strict counterpart disagree.

```python
value = 4
if value < 4:
    print("smaller")
else:
    print("not smaller")
```

Here the else branch runs. It includes equality as well as larger values.
See Python's [if and for statements](https://docs.python.org/3/tutorial/controlflow.html#if-statements)
for the language reference. This explanation and all exercises are original
synthesis, not copied lessons.

Start with the prediction, then implement, repair and transfer. Each coding
submission runs authored cases through Itembank's runtime. In practice, a
failed attempt stays on its question so you can compare the feedback and
repair it. Saved attempts describe what happened; they do not prove lasting
independent skill.

### Count values that qualify

Use a small table in your scratch work:

| Value relative to cutoff | Should it count? |
| --- | --- |
| Below | Decide from the requirement |
| Equal | Decide explicitly |
| Above | Decide from the requirement |

Then start a count at zero, inspect every value, and increment only when its
condition holds. Try your own equal-value example before submitting. Empty
input has no qualifying values. Repeated qualifying values are separate
observations, so each counts.

### Repair one boundary

For the debugging task, read the failed input, expected value and your actual
value. Which category in the table explains the difference? Change the rule
that caused it, then submit again. Do not special-case a visible input just to
make that one test pass. Extra hints are optional and released by the runtime.

### Transfer without a worked answer

The final question changes the setting and combines two boundaries. Read its
new contract before reusing an earlier condition. Explain your choice in your
own notes; the runtime records code outcomes and leaves prose review separate.
The transfer task contains no worked implementation in this lesson.

### Take it into a small project

After the unit, write a local command-line tool that reads fictional event
windows from a file and reports how many are active at a chosen time. Keep the
selection function separate from file loading. Add examples for empty input,
both boundaries and overlapping windows. Show the tool's input format and one
terminal run in a README. This is an optional learner-owned project brief,
not an automatically graded activity or permission to run arbitrary files.
Larger IDE, dependency, server and database projects need their own adapter.

Q1. Predict the printed value before executing this code.

```python
matches = 0
for value in [8, 9, 10]:
    if value >= 9:
        matches += 1
print(matches)
```
(difficulty: recall)
[ID: 6a0487c1915d42e3]
[HASH: sha256:7f9604dc5c08c810]
[OBJECTIVE: cs:boundary-filtering]
[LESSON-REF: Ask the boundary question]
[PAIR: boundary-workshop]

A) 1
B) 2
C) 3
D) 9

CORRECT: B
WHY BEST: Both 9 and 10 meet the inclusive lower boundary, so two values count.
KEY DISCRIMINATOR: The value exactly equal to 9 is included.
SECOND-BEST: A. It counts only values strictly above the cutoff.
DISTRACTOR ANALYSIS:
- A) This would be correct for a strict greater-than condition that excludes 9.
- B) Correct: 9 and 10 each increment the counter once.
- C) This would be correct if every value met the condition.
- D) This would be correct if the program printed the cutoff instead of the count.
TRAP: Ignoring the equals sign in an inclusive comparison.
CONFIDENCE: high


Q2. Implement count_over(values, limit). Return the number of integers strictly greater than limit. Count repeated values separately. An empty list returns zero.   (difficulty: application)
[ID: 11f7f38c5c304883]
[HASH: sha256:c004e5a5c47bc362]
[TYPE: check]
[OBJECTIVE: cs:boundary-filtering]
[LESSON-REF: Count values that qualify]
[PAIR: boundary-workshop]
[LANG: python]
[HARNESS: count_over]
CASE) count_over([2, 3, 4], 3) :: 1
CASE) count_over([3, 3], 3) :: 0
CASE) count_over([], 7) :: 0
CASE) count_over([-4, -2, 0], -2) :: 1
CASE) count_over([8, 8, 1], 3) :: 2
STARTER:
def count_over(values, limit):
    # Write your implementation here.
    return 0

WHY BEST: Count each value that meets the stated strict comparison, including duplicates.
KEY DISCRIMINATOR: Decide what happens below, at and above the boundary before choosing the comparison.
TRAP: A value exactly on a boundary is not automatically included. Match the requirement.
CONFIDENCE: high

Q3. Repair count_at_most(values, ceiling). The intended function counts every integer less than or equal to ceiling. The starter incorrectly excludes equality. Change the rule rather than special-casing the examples.   (difficulty: application)
[ID: 2093f3dcf6084875]
[HASH: sha256:fc51bf66c7794f17]
[TYPE: check]
[OBJECTIVE: cs:boundary-filtering]
[LESSON-REF: Repair one boundary]
[PAIR: boundary-workshop]
[LANG: python]
[HARNESS: count_at_most]
CASE) count_at_most([2, 3, 4], 3) :: 2
CASE) count_at_most([5, 5], 5) :: 2
CASE) count_at_most([], 5) :: 0
CASE) count_at_most([-4, -2, 0], -2) :: 2
CASE) count_at_most([9, 10], 3) :: 0
STARTER:
def count_at_most(values, ceiling):
    count = 0
    for value in values:
        if value < ceiling:
            count += 1
    return count

WHY BEST: The contract includes equality, so values on the ceiling count too.
KEY DISCRIMINATOR: Use the equality case to locate the faulty comparison.
TRAP: Passing an ordinary below-boundary example does not test equality.
CONFIDENCE: high

Q4. Fresh transfer: count_active(windows, moment) counts fictional event windows active at moment. Each window is a two-integer list [start, stop] with start less than stop. It is active from its start inclusive until its stop exclusive. Count overlapping windows separately; an empty list returns zero. Return an integer.   (difficulty: synthesis)
[ID: d2b8fd7b7e8b4f12]
[HASH: sha256:454ee388d98f08f8]
[TYPE: check]
[OBJECTIVE: cs:boundary-filtering]
[PAIR: boundary-workshop]
[LANG: python]
[HARNESS: count_active]
CASE) count_active([[2, 5], [5, 8]], 5) :: 1
CASE) count_active([[2, 5], [3, 7]], 4) :: 2
CASE) count_active([[2, 5]], 2) :: 1
CASE) count_active([[2, 5]], 5) :: 0
CASE) count_active([], 4) :: 0
CASE) count_active([[-4, -1], [-1, 2]], -1) :: 1
CASE) count_active([[2, 5], [2, 5]], 4) :: 2
STARTER:
def count_active(windows, moment):
    # Solve from the new contract, without a worked implementation.
    return 0

WHY BEST: Count a window only when both its inclusive start and exclusive stop conditions hold.
KEY DISCRIMINATOR: Test the start and stop boundaries separately, then combine them.
TRAP: Reusing one comparison from the counting tasks misses the second boundary.
CONFIDENCE: high

Q5. Explain an unfamiliar boundary rule in your own words. A fictional storage reservation includes its opening minute and excludes its closing minute. Write a short proof or Python function, explain both boundary choices, and give an example that distinguishes this rule from including both ends. Explain how overlapping reservations are counted. This is a separate reflection after the coding unit, with rubric review rather than automatic grading.   (difficulty: synthesis)
[ID: b6fd89d6ab8b4fd2]
[HASH: sha256:682ad8151c67df5f]
[TYPE: short]
[OBJECTIVE: cs:boundary-filtering]
[LESSON-REF: Take it into a small project]

MODEL: A reservation is active when its opening minute is at most the current minute and its closing minute is greater than the current minute. Equality at opening counts; equality at closing does not. Each qualifying reservation contributes separately, including overlaps.
RUBRIC:
- States and justifies the inclusive opening boundary.
- States and justifies the exclusive closing boundary.
- Gives an equality example that distinguishes the two boundary rules.
- Explains separate counting of overlapping reservations.

TRAP: Treating a successful code run as review of the explanation.
CONFIDENCE: high
