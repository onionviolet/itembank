# Visual authoring golden fixture (synthetic)

Fully invented content for the plan 06.1-02 authoring contract. The first two
items are valid (one plot, one number-line point); every later item isolates
exactly one invalid family so `itembank lint` can prove each named
`item.visual_*` code fires with the offending field. No real question bank
content is used, and `[SCORING:]` never appears in any served payload.

Q1. Place a point at (2, 3) on the coordinate grid.   (difficulty: application)
[OBJECTIVE: math:coordinates.plotting]
[TYPE: visual]
[INTERACTION: plot]
[VISUAL: {"version":1,"axes":{"x":{"min":"-5","max":"5","step":"1"},"y":{"min":"-5","max":"5","step":"1"}},"initial":{"points":[]},"actions":["place_point","move_point"],"accessibility":{"description":"A coordinate grid from -5 to 5 on both axes. Place the point at (2, 3)."}}]
[SCORING: {"kind":"point","accepted":[{"x":"2","y":"3"}],"tolerance":{"x":"0","y":"0"},"partial_credit":false}]

WHY BEST: (2, 3) is two units right of the origin and three units up, the only grid cell the prompt names.

KEY DISCRIMINATOR: The x-coordinate is horizontal distance and the y-coordinate vertical distance.

SECOND-BEST: (3, 2) swaps the coordinates; it would be correct if the prompt asked for three right and two up.

DISTRACTOR ANALYSIS:
- (3, 2) reverses the coordinates; this would be correct for the point three right and two up.

TRAP: Swapping the coordinates.

CONFIDENCE: high

Q2. Select the point at 1/2 on the number line.   (difficulty: recall)
[OBJECTIVE: math:numberline.rationals]
[TYPE: visual]
[INTERACTION: numberline]
[VISUAL: {"version":1,"axis":{"min":"-2","max":"2","step":"1/2"},"initial":{"points":[],"interval":null},"actions":["select_numberline_point"],"accessibility":{"description":"A number line from -2 to 2 in half steps. Select the point at 1/2."}}]
[SCORING: {"kind":"numberline_point","accepted":[{"value":"1/2"}],"tolerance":{"value":"0"},"partial_credit":false}]

WHY BEST: 1/2 is the half-step tick between 0 and 1.

KEY DISCRIMINATOR: The tick halfway between 0 and 1.

SECOND-BEST: 1 is a full step right of 0; it would be correct if the prompt asked for one whole unit.

DISTRACTOR ANALYSIS:
- 1 is a full step right of 0; this would be correct for the point at 1.

TRAP: Counting the half-step tick as a whole unit.

CONFIDENCE: high

Q3. Malformed VISUAL JSON.   (difficulty: recall)
[OBJECTIVE: math:invalid.json]
[TYPE: visual]
[INTERACTION: plot]
[VISUAL: {"version":1,"axes":{"x":{"min":"-5","max":"5","step":"1"},"y":{"min":"-5","max":"5","step":"1"}}, broken]
[SCORING: {"kind":"point","accepted":[{"x":"2","y":"3"}],"tolerance":{"x":"0","y":"0"},"partial_credit":false}]

WHY BEST: This item exists only to exercise the malformed-JSON lint code.

KEY DISCRIMINATOR: None — invalid fixture.

SECOND-BEST: None — invalid fixture.

DISTRACTOR ANALYSIS:
- N/A — invalid fixture.

TRAP: None — invalid fixture.

CONFIDENCE: low

Q4. Malformed SCORING JSON.   (difficulty: recall)
[OBJECTIVE: math:invalid.json]
[TYPE: visual]
[INTERACTION: plot]
[VISUAL: {"version":1,"axes":{"x":{"min":"-5","max":"5","step":"1"},"y":{"min":"-5","max":"5","step":"1"}},"initial":{"points":[]},"actions":["place_point","move_point"],"accessibility":{"description":"A coordinate grid. Place a point."}}]
[SCORING: {"kind":"point","accepted":[{"x":"2","y":"3"}],"tolerance":]

WHY BEST: This item exists only to exercise the malformed-SCORING lint code.

KEY DISCRIMINATOR: None — invalid fixture.

SECOND-BEST: None — invalid fixture.

DISTRACTOR ANALYSIS:
- N/A — invalid fixture.

TRAP: None — invalid fixture.

CONFIDENCE: low

Q5. Unknown interaction kind.   (difficulty: recall)
[OBJECTIVE: math:invalid.interaction]
[TYPE: visual]
[INTERACTION: histogram]
[VISUAL: {"version":1,"axes":{"x":{"min":"-5","max":"5","step":"1"},"y":{"min":"-5","max":"5","step":"1"}},"initial":{"points":[]},"actions":["place_point","move_point"],"accessibility":{"description":"A coordinate grid. Place a point."}}]
[SCORING: {"kind":"point","accepted":[{"x":"2","y":"3"}],"tolerance":{"x":"0","y":"0"},"partial_credit":false}]

WHY BEST: This item exists only to exercise the unknown-interaction lint code.

KEY DISCRIMINATOR: None — invalid fixture.

SECOND-BEST: None — invalid fixture.

DISTRACTOR ANALYSIS:
- N/A — invalid fixture.

TRAP: None — invalid fixture.

CONFIDENCE: low

Q6. Unknown action kind.   (difficulty: recall)
[OBJECTIVE: math:invalid.action]
[TYPE: visual]
[INTERACTION: plot]
[VISUAL: {"version":1,"axes":{"x":{"min":"-5","max":"5","step":"1"},"y":{"min":"-5","max":"5","step":"1"}},"initial":{"points":[]},"actions":["place_point","drag_fire"],"accessibility":{"description":"A coordinate grid. Place a point."}}]
[SCORING: {"kind":"point","accepted":[{"x":"2","y":"3"}],"tolerance":{"x":"0","y":"0"},"partial_credit":false}]

WHY BEST: This item exists only to exercise the unknown-action lint code.

KEY DISCRIMINATOR: None — invalid fixture.

SECOND-BEST: None — invalid fixture.

DISTRACTOR ANALYSIS:
- N/A — invalid fixture.

TRAP: None — invalid fixture.

CONFIDENCE: low

Q7. Unknown scoring kind.   (difficulty: recall)
[OBJECTIVE: math:invalid.kind]
[TYPE: visual]
[INTERACTION: plot]
[VISUAL: {"version":1,"axes":{"x":{"min":"-5","max":"5","step":"1"},"y":{"min":"-5","max":"5","step":"1"}},"initial":{"points":[]},"actions":["place_point","move_point"],"accessibility":{"description":"A coordinate grid. Place a point."}}]
[SCORING: {"kind":"region","accepted":[{"x":"2","y":"3"}],"tolerance":{"x":"0","y":"0"},"partial_credit":false}]

WHY BEST: This item exists only to exercise the unknown-scoring-kind lint code.

KEY DISCRIMINATOR: None — invalid fixture.

SECOND-BEST: None — invalid fixture.

DISTRACTOR ANALYSIS:
- N/A — invalid fixture.

TRAP: None — invalid fixture.

CONFIDENCE: low

Q8. Unknown VISUAL member.   (difficulty: recall)
[OBJECTIVE: math:invalid.member]
[TYPE: visual]
[INTERACTION: plot]
[VISUAL: {"version":1,"axes":{"x":{"min":"-5","max":"5","step":"1"},"y":{"min":"-5","max":"5","step":"1"}},"initial":{"points":[]},"actions":["place_point","move_point"],"accessibility":{"description":"A coordinate grid. Place a point."},"onclick":"alert(1)"}]
[SCORING: {"kind":"point","accepted":[{"x":"2","y":"3"}],"tolerance":{"x":"0","y":"0"},"partial_credit":false}]

WHY BEST: This item exists only to exercise the unknown-VISUAL-member lint code.

KEY DISCRIMINATOR: None — invalid fixture.

SECOND-BEST: None — invalid fixture.

DISTRACTOR ANALYSIS:
- N/A — invalid fixture.

TRAP: None — invalid fixture.

CONFIDENCE: low

Q9. Unknown SCORING member.   (difficulty: recall)
[OBJECTIVE: math:invalid.member]
[TYPE: visual]
[INTERACTION: plot]
[VISUAL: {"version":1,"axes":{"x":{"min":"-5","max":"5","step":"1"},"y":{"min":"-5","max":"5","step":"1"}},"initial":{"points":[]},"actions":["place_point","move_point"],"accessibility":{"description":"A coordinate grid. Place a point."}}]
[SCORING: {"kind":"point","accepted":[{"x":"2","y":"3"}],"tolerance":{"x":"0","y":"0"},"partial_credit":false,"answer_key":"B"}]

WHY BEST: This item exists only to exercise the unknown-SCORING-member lint code.

KEY DISCRIMINATOR: None — invalid fixture.

SECOND-BEST: None — invalid fixture.

DISTRACTOR ANALYSIS:
- N/A — invalid fixture.

TRAP: None — invalid fixture.

CONFIDENCE: low

Q10. Invalid axis geometry.   (difficulty: recall)
[OBJECTIVE: math:invalid.axis]
[TYPE: visual]
[INTERACTION: plot]
[VISUAL: {"version":1,"axes":{"x":{"min":"-5","max":"5","step":"0"},"y":{"min":"-5","max":"5","step":"1"}},"initial":{"points":[]},"actions":["place_point","move_point"],"accessibility":{"description":"A coordinate grid. Place a point."}}]
[SCORING: {"kind":"point","accepted":[{"x":"2","y":"3"}],"tolerance":{"x":"0","y":"0"},"partial_credit":false}]

WHY BEST: This item exists only to exercise the invalid-axis lint code.

KEY DISCRIMINATOR: None — invalid fixture.

SECOND-BEST: None — invalid fixture.

DISTRACTOR ANALYSIS:
- N/A — invalid fixture.

TRAP: None — invalid fixture.

CONFIDENCE: low

Q11. Excessive scalar precision.   (difficulty: recall)
[OBJECTIVE: math:invalid.precision]
[TYPE: visual]
[INTERACTION: plot]
[VISUAL: {"version":1,"axes":{"x":{"min":"-5","max":"5","step":"1.0000000"},"y":{"min":"-5","max":"5","step":"1"}},"initial":{"points":[]},"actions":["place_point","move_point"],"accessibility":{"description":"A coordinate grid. Place a point."}}]
[SCORING: {"kind":"point","accepted":[{"x":"2","y":"3"}],"tolerance":{"x":"0","y":"0"},"partial_credit":false}]

WHY BEST: This item exists only to exercise the invalid-scalar lint code.

KEY DISCRIMINATOR: None — invalid fixture.

SECOND-BEST: None — invalid fixture.

DISTRACTOR ANALYSIS:
- N/A — invalid fixture.

TRAP: None — invalid fixture.

CONFIDENCE: low

Q12. Negative tolerance.   (difficulty: recall)
[OBJECTIVE: math:invalid.tolerance]
[TYPE: visual]
[INTERACTION: numberline]
[VISUAL: {"version":1,"axis":{"min":"-2","max":"2","step":"1/2"},"initial":{"points":[],"interval":null},"actions":["select_numberline_point"],"accessibility":{"description":"A number line from -2 to 2. Select a point."}}]
[SCORING: {"kind":"numberline_point","accepted":[{"value":"1/2"}],"tolerance":{"value":"-1/4"},"partial_credit":false}]

WHY BEST: This item exists only to exercise the invalid-tolerance lint code.

KEY DISCRIMINATOR: None — invalid fixture.

SECOND-BEST: None — invalid fixture.

DISTRACTOR ANALYSIS:
- N/A — invalid fixture.

TRAP: None — invalid fixture.

CONFIDENCE: low

Q13. Empty accessible description.   (difficulty: recall)
[OBJECTIVE: math:invalid.accessibility]
[TYPE: visual]
[INTERACTION: plot]
[VISUAL: {"version":1,"axes":{"x":{"min":"-5","max":"5","step":"1"},"y":{"min":"-5","max":"5","step":"1"}},"initial":{"points":[]},"actions":["place_point","move_point"],"accessibility":{"description":"  "}}]
[SCORING: {"kind":"point","accepted":[{"x":"2","y":"3"}],"tolerance":{"x":"0","y":"0"},"partial_credit":false}]

WHY BEST: This item exists only to exercise the empty-accessibility lint code.

KEY DISCRIMINATOR: None — invalid fixture.

SECOND-BEST: None — invalid fixture.

DISTRACTOR ANALYSIS:
- N/A — invalid fixture.

TRAP: None — invalid fixture.

CONFIDENCE: low

Q14. Duplicate scene point ids.   (difficulty: recall)
[OBJECTIVE: math:invalid.ids]
[TYPE: visual]
[INTERACTION: plot]
[VISUAL: {"version":1,"axes":{"x":{"min":"-5","max":"5","step":"1"},"y":{"min":"-5","max":"5","step":"1"}},"initial":{"points":[{"id":"p1","x":"0","y":"0"},{"id":"p1","x":"1","y":"1"}]},"actions":["place_point","move_point"],"accessibility":{"description":"A coordinate grid. Place a point."}}]
[SCORING: {"kind":"point","accepted":[{"x":"2","y":"3"}],"tolerance":{"x":"0","y":"0"},"partial_credit":false}]

WHY BEST: This item exists only to exercise the duplicate-scene-id lint code.

KEY DISCRIMINATOR: None — invalid fixture.

SECOND-BEST: None — invalid fixture.

DISTRACTOR ANALYSIS:
- N/A — invalid fixture.

TRAP: None — invalid fixture.

CONFIDENCE: low

Q15. Executable/script-bearing member.   (difficulty: recall)
[OBJECTIVE: math:invalid.exec]
[TYPE: visual]
[INTERACTION: plot]
[VISUAL: {"version":1,"axes":{"x":{"min":"-5","max":"5","step":"1"},"y":{"min":"-5","max":"5","step":"1"}},"initial":{"points":[{"id":"p1","x":"0","y":"0","onload":"alert(1)"}]},"actions":["place_point","move_point"],"accessibility":{"description":"A coordinate grid. Place a point."}}]
[SCORING: {"kind":"point","accepted":[{"x":"2","y":"3"}],"tolerance":{"x":"0","y":"0"},"partial_credit":false}]

WHY BEST: This item exists only to exercise the executable-member lint code.

KEY DISCRIMINATOR: None — invalid fixture.

SECOND-BEST: None — invalid fixture.

DISTRACTOR ANALYSIS:
- N/A — invalid fixture.

TRAP: None — invalid fixture.

CONFIDENCE: low
