# Visual GIFT fixture (synthetic)

A mixed synthetic bank: one ordinary expressible multiple-choice item plus
plot and number-line visual items. It exists to prove plan 06.1-03's GIFT
boundary: default and `--strict` exports render the expressible item and
refuse every visual item by its original item number with
`gift.type_unsupported`, with no lossy approximation and no private scoring or
scene material leaking into the partial document. No real question bank
content is used.

Q1. Which unit is used to measure electrical potential difference?   (difficulty: recall)
[OBJECTIVE: physics:units.voltage]
[ID: 6f18f22c8f1b4a01]
[HASH: sha256:2c8f9c4a1b6d3e5f]

A) Volt
B) Ampere
C) Ohm
D) Watt

CORRECT: A

WHY BEST: The volt is the SI unit of electrical potential difference, matching the measure the question names.

KEY DISCRIMINATOR: Potential difference is measured in volts; current in amperes, resistance in ohms, power in watts.

SECOND-BEST: B. The ampere measures current; it would be correct if the question asked for the unit of current flow.

DISTRACTOR ANALYSIS:
- A) Correct: the volt measures potential difference.
- B) The ampere measures current; this would be correct for the unit of current.
- C) The ohm measures resistance; this would be correct for the unit of resistance.
- D) The watt measures power; this would be correct for the unit of power.

TRAP: Confusing potential difference (volts) with current (amperes).

CONFIDENCE: high

Q2. Place a point at (2, 3) on the coordinate grid.   (difficulty: application)
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

Q3. Select the point at 1/2 on the number line.   (difficulty: recall)
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

Q4. Select the heart on the organ diagram.   (difficulty: recall)
[OBJECTIVE: anatomy:organs.locate]
[TYPE: visual]
[INTERACTION: hotspot]
[VISUAL: {"version":1,"plane":{"width":"10","height":"6"},"regions":[{"id":"heart","label":"Heart","shape":"circle","coords":["2","3","1.5"]},{"id":"liver","label":"Liver","shape":"rect","coords":["6","2","3","2"]}],"initial":{"region":null},"actions":["select_hotspot"],"accessibility":{"description":"A diagram with a heart and a liver. Select the heart."}}]
[SCORING: {"kind":"hotspot","accepted":[{"region":"heart"}],"tolerance":{},"partial_credit":false}]

WHY BEST: The heart is the circular region on the left of the diagram.

KEY DISCRIMINATOR: The correct region is identified by label and shape, not position alone.

SECOND-BEST: The liver is the rectangle on the right; it would be correct if the prompt asked for the right-side organ.

DISTRACTOR ANALYSIS:
- The liver is the rectangle on the right; this would be correct if the item asked for the right-side organ.

TRAP: Picking the leftmost region without reading the label.

CONFIDENCE: high

Q5. Place the fall of Rome at year 5 on the timeline.   (difficulty: recall)
[OBJECTIVE: history:world.timeline]
[TYPE: visual]
[INTERACTION: timeline]
[VISUAL: {"version":1,"axis":{"min":"0","max":"10","step":"1"},"events":[{"id":"fall","label":"Fall of Rome"},{"id":"printing","label":"Printing press"}],"initial":{"placements":[]},"actions":["place_timeline_event"],"accessibility":{"description":"A timeline from 0 to 10. Place the fall of Rome at year 5."}}]
[SCORING: {"kind":"timeline_event","accepted":[{"event":"fall","value":"5"}],"tolerance":{"value":"0"},"partial_credit":false}]

WHY BEST: The fall of Rome is conventionally dated 476 CE, the midpoint of this 0-10 timeline.

KEY DISCRIMINATOR: Event id and year must both match.

SECOND-BEST: The printing press is the other event; it would be correct if the prompt asked for the later invention.

DISTRACTOR ANALYSIS:
- Placing the printing press at 5 mixes the right year with the wrong event.

TRAP: Finding the right year and forgetting which event label goes with it.

CONFIDENCE: high
