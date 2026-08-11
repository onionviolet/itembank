# Visual assessment bank (synthetic)

Fully invented content for the interactive visual protocol tracer. It exists to
exercise the declarative `visual` item grammar (`[INTERACTION:]` +
`[VISUAL:]` scene + private `[SCORING:]` envelope) across the three protocol-1
response kinds: a plot point on an integer grid, a number-line point on a
half-step grid, and a number-line interval. It is not derived from any real
course, exam, or textbook, and no real question bank belongs in this
repository. `[SCORING:]` is the private scoring envelope: it never appears in
any served/public payload.

Q1. Place a point at (2, 3) on the coordinate grid.   (difficulty: application)
[OBJECTIVE: math:coordinates.plotting]
[TYPE: visual]
[INTERACTION: plot]
[VISUAL: {"version":1,"axes":{"x":{"min":"-5","max":"5","step":"1"},"y":{"min":"-5","max":"5","step":"1"}},"initial":{"points":[]},"actions":["place_point","move_point"],"accessibility":{"description":"A coordinate grid from -5 to 5 on both axes, with one movable point. Place the point at (2, 3)."}}]
[SCORING: {"kind":"point","accepted":[{"x":"2","y":"3"}],"tolerance":{"x":"0","y":"0"},"partial_credit":false}]

WHY BEST: (2, 3) is two units right of the origin on the x-axis and three units up on the y-axis, the only grid cell the prompt names.

KEY DISCRIMINATOR: The x-coordinate is horizontal distance and the y-coordinate is vertical distance; a correct answer preserves which number belongs on which axis.

SECOND-BEST: (3, 2) swaps the coordinates; it would be correct if the prompt asked for three right and two up.

DISTRACTOR ANALYSIS:
- (3, 2) reverses the coordinates; this would be correct if the item asked for the point three right and two up.
- (2, -3) keeps x correct but mirrors y; this would be correct for a point two right and three down.

TRAP: Reading "2, 3" and placing the point at (3, 2) because the numbers feel interchangeable.

CONFIDENCE: high

Q2. Select the point at 1/2 on the number line.   (difficulty: recall)
[OBJECTIVE: math:numberline.rationals]
[TYPE: visual]
[INTERACTION: numberline]
[VISUAL: {"version":1,"axis":{"min":"-2","max":"2","step":"1/2"},"initial":{"points":[],"interval":null},"actions":["select_numberline_point"],"accessibility":{"description":"A number line from -2 to 2 marked in half steps, with one selectable point. Select the point at 1/2."}}]
[SCORING: {"kind":"numberline_point","accepted":[{"value":"1/2"}],"tolerance":{"value":"0"},"partial_credit":false}]

WHY BEST: 1/2 is halfway between 0 and 1, the first half-step tick to the right of zero.

KEY DISCRIMINATOR: The tick halfway between 0 and 1, not the tick at 1 or the tick at 0.

SECOND-BEST: 1 sits a full step right of 0; it would be correct if the prompt asked for one whole unit.

DISTRACTOR ANALYSIS:
- 1 is a full step right of 0; this would be correct if the item asked for the point at 1.
- 0 is the origin; this would be correct if the item asked for the point at zero.

TRAP: Counting the half-step tick at 1/2 as a whole unit and landing on 1.

CONFIDENCE: high

Q3. Select the interval from -1 to 3/2, including -1 but excluding 3/2.   (difficulty: analysis)
[OBJECTIVE: math:numberline.intervals]
[TYPE: visual]
[INTERACTION: numberline]
[VISUAL: {"version":1,"axis":{"min":"-2","max":"2","step":"1/2"},"initial":{"points":[],"interval":null},"actions":["set_interval"],"accessibility":{"description":"A number line from -2 to 2 marked in half steps, with one adjustable interval. Set the interval from -1 to 3/2, closed at -1 and open at 3/2."}}]
[SCORING: {"kind":"interval","accepted":[{"start":"-1","end":"3/2","start_closed":true,"end_closed":false}],"tolerance":{"start":"0","end":"0"},"partial_credit":false}]

WHY BEST: The interval spans two and a half half-steps, closed at -1 and open at 3/2, exactly matching the prompt's endpoints and boundary inclusivity.

KEY DISCRIMINATOR: The endpoint at 3/2 is excluded while -1 is included; swapping the closures changes which boundary values belong to the interval.

SECOND-BEST: Closing both ends would include 3/2; it would be correct if the prompt asked for a closed interval.

DISTRACTOR ANALYSIS:
- Closing both endpoints would include 3/2; this would be correct if the prompt asked for a closed interval.
- Reversing the direction (3/2 to -1) names the same set but must be normalized by the runtime, never rejected.

TRAP: Including the open endpoint 3/2 because the interval "reaches" it visually.

CONFIDENCE: high

Q4. Select a point within half a unit of 1 on the number line.   (difficulty: application)
[OBJECTIVE: math:numberline.tolerance]
[TYPE: visual]
[INTERACTION: numberline]
[VISUAL: {"version":1,"axis":{"min":"-2","max":"2","step":"1/2"},"initial":{"points":[],"interval":null},"actions":["select_numberline_point"],"accessibility":{"description":"A number line from -2 to 2 marked in half steps, with one selectable point. Select a point at least half a unit away from 1."}}]
[SCORING: {"kind":"numberline_point","accepted":[{"value":"1"}],"tolerance":{"value":"1/2"},"partial_credit":false}]

WHY BEST: The tolerated region is [1/2, 3/2]: every tick at least half a unit from 1 — including the boundaries 1/2 and 3/2 — is accepted.

KEY DISCRIMINATOR: Tolerance is inclusive of both boundaries; 0 and 2 sit exactly one step away and fail, while 1/2 and 3/2 sit exactly on the boundary and pass.

SECOND-BEST: 0 is a full unit from 1; it would be correct only under a stricter tolerance than 1/2.

DISTRACTOR ANALYSIS:
- 0 is a full unit left of 1; this would be correct if the tolerance were larger than one.
- 2 is a full unit right of 1; this would be correct if the tolerance were larger than one.

TRAP: Treating the tolerance as exclusive so that 1/2 and 3/2 fail when they should pass.

CONFIDENCE: high
