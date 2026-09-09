# Rainfall, side by side

Prototype teaching artifact. Synthetic source only. Not accepted learner content.

Objective RAIN-COMPARE: compare two rainfall depths and explain why the time intervals must match.

## Source RAIN-01, paragraph 1

[Read the unchanged source](../rainfall.txt).

> A rain gauge measures rainfall depth in millimeters. Compare readings over equal time intervals. Gauge A collected 12 mm in 24 hours and gauge B collected 18 mm in 24 hours. B received 6 mm more.

Source identity: the existing synthetic competition fixture `rainfall.txt`.
Rights: synthetic agent-authored trial text with no third-party course content.
Revision: see the SHA-256 in `baseline.json` for `prototypes/competition/rainfall.txt`.

## What to notice

**Depth is the quantity.** Millimeters describe rainfall depth here.
**Time is held equal.** Both source measurements cover 24 hours.
These notes paraphrase RAIN-01.

## Explanation and hypothetical comparison

AI-authored synthesis from RAIN-01, not additional observations:

Holding the time interval equal lets this comparison focus on rainfall depth over the same duration. A larger depth over a longer interval would mix two changing quantities.

Subtract A from B. At the source values, **18 - 12 = 6 mm**, so B is higher by 6 mm.

The interactive version holds A at 12 mm and lets you vary B from 0 to 24 mm. Both intervals remain 24 hours. Every B value except 18 mm is hypothetical.

| B depth | B - A | Meaning | Origin |
| --- | --- | --- | --- |
| 6 mm | -6 mm | B is 6 mm lower | Hypothetical |
| 12 mm | 0 mm | Equal depths | Hypothetical |
| 18 mm | +6 mm | B is 6 mm higher | RAIN-01 |

**Takeaway:** compare depths over equal time intervals. Subtract A from B to see the size and direction of the difference.

No response is requested or graded. Interaction is temporary presentation state. Reset and reopen restore source values. Nothing creates a score, mastery claim, accepted revision, or learner evidence.
