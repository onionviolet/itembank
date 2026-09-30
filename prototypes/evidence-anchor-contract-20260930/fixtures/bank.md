# Fictional fixed evidence spans

Synthetic fixtures only. A fictional counter follows this passage:

Café 🧭: Add two. Start at three. Add two.

The repeated rule sentences are distinct occurrences. Select both rule
occurrences, not the initial state. Offsets count Unicode code points within
the passage, starting at zero; the end is excluded.

| Option | Anchor ID | Range | Quote |
| --- | --- | --- | --- |
| A | rule-first | 8:16 | Add two. |
| B | start | 17:32 | Start at three. |
| C | rule-second | 33:41 | Add two. |

Q1. Select both occurrences that state the fictional rule.
[HASH: sha256:9df6e6f844b18a74]
[ID: ea00000000000001]
[TYPE: multi]
[OBJECTIVE: synthetic:fixed-evidence]
[SELECT: 2]
A) Rule sentence, first occurrence (8:16): Add two.
B) Initial state (17:32): Start at three.
C) Rule sentence, second occurrence (33:41): Add two.
CORRECT: A, C
WHY BEST: Both occurrences describe the rule rather than the initial state.
KEY DISCRIMINATOR: Quote text alone cannot distinguish repeated occurrences.
DISTRACTOR ANALYSIS:
- A) Correct: the first occurrence states the rule.
- B) This would be correct when selecting evidence of the initial state.
- C) Correct: the second occurrence states the rule.
TRAP: Do not collapse equal quote text into one occurrence.
CONFIDENCE: high

Q2. Recheck both rule occurrences in the same fictional passage.
[HASH: sha256:26d4e14ee7e99912]
[ID: ea00000000000002]
[TYPE: multi]
[OBJECTIVE: synthetic:fixed-evidence-recheck]
[SELECT: 2]
A) Rule sentence, first occurrence (8:16): Add two.
B) Initial state (17:32): Start at three.
C) Rule sentence, second occurrence (33:41): Add two.
CORRECT: A, C
WHY BEST: Both rule occurrences support the same fictional claim.
KEY DISCRIMINATOR: Each occurrence retains its own stable identity.
DISTRACTOR ANALYSIS:
- A) Correct: the first occurrence is rule evidence.
- B) This would be correct when asked for the starting value.
- C) Correct: the second occurrence is rule evidence.
TRAP: Relevant context need not be evidence of the requested claim.
CONFIDENCE: high
