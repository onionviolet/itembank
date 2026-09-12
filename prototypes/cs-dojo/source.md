# CS Dojo: array boundaries and function contracts

Original synthetic teaching unit. Source identity: SYN-CS-UNIT-01.
Revision: 2026-09-12. All prose, examples, and worked explanations here are
public practice material. This is a study-usable static fallback, not a bank.

The rich prototype uses three activities with the same objectives and teaching
points below. Write predictions and reflections in your own notes when using
this document. There are no scores or mastery claims. The JavaScript browser
runner is optional. Do not execute code from an unreviewed downloaded draft.

## Indices

Objective SYN-CS-01: trace array indices and explain an exclusive upper bound.

For an array of length n, the occupied indices run from 0 through n - 1.
Reading an absent array element produces undefined. The condition
`i < values.length` stops before the first absent position.

Predict every line printed by this original example:

```javascript
const readings = [3, 7, 4];

for (let i = 0; i <= readings.length; i++) {
  console.log(i, readings[i]);
}
```

Write your prediction before checking the worked trace. Which condition would
visit exactly the three stored readings, and why?

### Worked trace

| i | Condition i <= 3 | Value | Printed line |
| --- | --- | --- | --- |
| 0 | true | 3 | 0 3 |
| 1 | true | 7 | 1 7 |
| 2 | true | 4 | 2 4 |
| 3 | true | undefined | 3 undefined |
| 4 | false | not read | nothing |

Changing the condition to `i < readings.length` visits only indices 0, 1, and
2. Length is the count of elements, not the last occupied index.

## Accumulators

Objective SYN-CS-02: use an observed failure and an empty case to repair a loop.

Start a sum at 0, the additive identity. Add only occupied elements. Adding
undefined to a number produces NaN, which then propagates through later
additions. For an empty array, the loop should execute zero times and return
its initial total.

Repair this function so it adds each provided finite number exactly once:

```javascript
function sum(readings) {
  let total = 0;
  for (let i = 0; i <= readings.length; i++) {
    total += readings[i];
  }
  return total;
}
```

Compare its behavior for these declared examples:

| Example | Input | Expected result |
| --- | --- | --- |
| three readings | [3, 7, 4] | 14 |
| empty input | [] | 0 |
| negative value | [-2, 5] | 3 |

The rich runner provides `report(label, actual, expected)` to display these
values side by side. It does not grade them. Add an example testing a different
boundary. Explain the cause of NaN and why your repair addresses it.

### Worked repair

Use `i < readings.length`. The original loop adds the absent element at
`readings[readings.length]`. The repaired empty loop executes zero times.
A one-element array is a useful extra boundary example.

## Contracts

Objective SYN-CS-03: implement a function across a declared module boundary and
design examples.

The arithmetic mean is the sum divided by the count. An empty array has no
arithmetic mean, so this exercise explicitly returns null. Inputs contain only
finite numbers. Examples should probe ordinary inputs and boundaries. Selected
examples do not prove that a program is correct.

Implement `mean(readings)` in `stats.js`:

```javascript
function mean(readings) {
  // Return null when there are no readings.
  // Otherwise calculate the sum and divide by the count.
  return null;
}

module.exports = { mean };
```

In the provided `examples.js`, add one example containing a negative number and
another containing a single value:

```javascript
const { mean } = require("./stats.js");

report("two readings", mean([2, 6]), 4);
report("empty input", mean([]), null);
```

This is an explicitly declared CommonJS-style local-file teaching harness.
`module.exports` shares the function and `require("./stats.js")` obtains it.
There is no Node.js environment, filesystem, package loading, or native
ES-module support in this prototype.

Explain your empty-input choice. What could remain wrong if these examples
look right? Keep code, behavioral observations, and explanations separate.

### Worked approach

Return null when `readings.length === 0`. Otherwise accumulate the sum and
return `total / readings.length`. Extra examples include `[-2, 6]` with expected
mean 2 and `[5]` with expected mean 5. Review readability and reasoning
separately from behavior.

## Recovery and review

The browser draft includes all three activities, code files, predictions,
observations, and reflections. Activity and file changes retain these values
inside the same tab. Reloading starts again. Export a plain Markdown draft to
keep your work. Reset affects one activity after confirmation.

Execution errors and timeouts are execution outcomes, not incorrect answers.
Code is limited to 30,000 characters per provided file. Runs stop after two
seconds or bounded output. The worker has no DOM or host filesystem API.
The browser cannot provide a hard per-worker memory quota here. This remains
a disposable prototype on its own loopback origin, not production assessment
execution or an accepted hostile-code sandbox.
