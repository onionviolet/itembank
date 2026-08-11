# Broken check-item sample bank (synthetic)

Four deliberately invalid items, each tripping one of the new lint codes
introduced with the `check` item type (plan 05-01): a language absent from the
allowlist, a single-case item, a harness item with a float expected value but
no [TOLERANCE:], and a `short` item -- deliberately NOT registered in the
normalizer registry -- so an author of a bank that mixes code items with an
unregistered type is told it will land pending.

Q1. Write a program that greets the user by name.   (difficulty: recall)
[TYPE: check]
[OBJECTIVE: cs:io.greet]
[LANG: ruby]
CASE) Ada :: Hello, Ada!
CASE) Lin :: Hello, Lin!
TRAP: Printing without a trailing newline.
CONFIDENCE: high

Q2. Write a program that prints the number 7.   (difficulty: recall)
[TYPE: check]
[OBJECTIVE: cs:io.seven]
CASE) 1 :: 7
TRAP: Reading stdin instead of printing a constant.
CONFIDENCE: high

Q3. Complete the function so it returns half of its argument.   (difficulty: application)
[TYPE: check]
[OBJECTIVE: cs:functions.half]
[HARNESS: half]
CASE) half(10) :: 5
CASE) half(1) :: 0.5
TRAP: Returning the argument unchanged.
CONFIDENCE: high

Q4. Explain in your own words what a variable is.   (difficulty: recall)
[TYPE: short]
[OBJECTIVE: cs:concepts.variable]
MODEL: A named container for a value.
RUBRIC:
- Names that it holds a value
- Says it can change
TRAP: Confusing the name with the value.
CONFIDENCE: high
