# Subject-loop CS fixture (synthetic, Phase 9)

Fully invented teaching content for the subject-invariant loop roundtrip. It
is not derived from any real course, exam, or textbook.

## LESSON

### Sum of Two Numbers

Context before the action: a program that reads two integers and prints
their sum is the smallest complete input/output program. Reading uses
`input().split()`, converting each piece with `int`, and summing with
`sum`. The example below is safe to run: it reads until end of input.

```python
print(sum(int(x) for x in input().split()))
```

The prediction check is the item below: write the program that prints the
sum of two integers, then run it against the hidden cases. A wrong run
unlocks one targeted hint; a corrected program can be re-submitted.

Q1. Write a program that prints the sum of two integers.
[LESSON-REF: Sum of Two Numbers]
[OBJECTIVE: cs:io.sum]
[TYPE: check]
[LANG: python]
[MATCH: trimmed]
CASE) 5 7 :: 12
CASE) 1 2 :: 3
TRAP: Reading fewer than the authored values, or printing a label before
the number.
CONFIDENCE: high
