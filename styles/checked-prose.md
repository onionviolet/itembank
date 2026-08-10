# Style: Checked Prose (short prose then a check)

[STYLE-PARENT: house]
[STYLE-FLAG: predict_first true]

## Voice

Content parent: expository. Execute Program and Brilliant merge into one
style behind the `predict_first` flag (D-08, catalogue 1+2): very short
prose, then a `[!CHECK:]` the learner must actually complete, then the next
paragraph. With `predict_first` the check renders before the prose that
resolves it (productive failure); a subject profile turns the flag off
where prediction would be a guessing game. The flag is a parameter, never a
second style -- three traditions (Execute Program, Brilliant, productive
failure) are one interface with a setting.

## Rules

| id | kind | params | severity | lock | prompt |
|----|------|--------|----------|------|--------|
| check.in.prose | style.require | [!CHECK], 1 | error | | yes |
| check.before.prose | order.before | [!CHECK], paragraph | error | | yes |
| prose.budget | cadence.section | 40, 120 | error | | no |

## Exemplar

### The for-in loop

> [!CHECK] Read this code and predict what it prints before reading on.
> for i in range(3): print(i)

A `for` loop visits each element of its sequence in order. The check above
asked you to predict before the explanation appeared; the loop printed 0,
then 1, then 2.
