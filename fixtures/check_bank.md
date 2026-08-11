# Check-item sample bank (synthetic)

Fully invented content for an imaginary "CS Foundations" course (cs:). It
exists to exercise the `check` item type end to end -- parse, run, score,
record -- and to give `lint` something that passes cleanly. It is not derived
from any real course, exam, or textbook, and no real question bank belongs in
this repository.

Q1. Write a program that reads two integers from standard input and prints their sum.   (difficulty: recall)
[ID: 1000000000000001]
[HASH: sha256:61dd03f6c9d399e1]
[TYPE: check]
[OBJECTIVE: cs:io.sum]
[LANG: python]
[MATCH: trimmed]
CASE) 5 7 :: 12
CASE) 3 4 :: 7
STARTER:
import sys

nums = [int(x) for x in sys.stdin.read().split()]
print(sum(nums))

TRAP: Reading only the first number instead of the whole line.
CONFIDENCE: high

Q2. Write a program that reads integers from standard input, one per line, and prints the total.   (difficulty: application)
[ID: 1000000000000002]
[HASH: sha256:b122caba635b0098]
[TYPE: check]
[OBJECTIVE: cs:io.anycount]
CASE) 5 7 :: 12
CASE) 3 4 :: 7
CASE) 0 :: 0
STARTER:
import sys

total = 0
for line in sys.stdin:
    total += int(line)
print(total)

TRAP: Hard-coding a two-number input instead of looping over all lines.
CONFIDENCE: high

Q3. Write a program that reads a number and prints it twice.   (difficulty: recall)
[ID: 1000000000000003]
[HASH: sha256:90639558f5e58415]
[TYPE: check]
[OBJECTIVE: cs:io.duplicate]
CASE) 7 :: 7
CASE) 3 :: 3
STARTER:
import sys

value = sys.stdin.read().strip()
while True:
    pass

TRAP: Writing a loop that never terminates.
CONFIDENCE: high

Q4. Write a program that reads a number and counts upward from it.   (difficulty: recall)
[ID: 1000000000000004]
[HASH: sha256:053aabb43070acd3]
[TYPE: check]
[OBJECTIVE: cs:io.countup]
CASE) 1 :: 1
CASE) 1 :: 1
STARTER:
import sys

value = int(sys.stdin.read().strip())
n = value
while True:
    print(n)
    n += 1

TRAP: Forgetting a stopping condition.
CONFIDENCE: high

Q5. Write a program that prints exactly one positive integer.   (difficulty: application)
[ID: 1000000000000005]
[HASH: sha256:7a75998c49522057]
[TYPE: check]
[OBJECTIVE: cs:io.single_int]
[MATCH: regex]
CASE) 42 :: [0-9]+
CASE) 7 :: [0-9]+
STARTER:
import sys

sys.stdout.write(sys.stdin.read().strip())

TRAP: Printing extra text alongside the number.
CONFIDENCE: high

Q6. Complete the function so it returns the sum of its two arguments.   (difficulty: recall)
[ID: 1000000000000006]
[HASH: sha256:99c8ae7072591b5a]
[TYPE: check]
[OBJECTIVE: cs:functions.add]
[HARNESS: add]
[TOLERANCE: 0.01]
CASE) add(1, 2) :: 3
CASE) add(2, 3) :: 5
CASE) add(0.1, 0.2) :: 0.3
STARTER:
def add(a, b):
    return a + b

TRAP: Returning the first argument instead of the sum.
CONFIDENCE: high
