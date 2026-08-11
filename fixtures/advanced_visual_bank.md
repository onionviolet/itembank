# Advanced visual assessment bank (synthetic)

Fully invented content for the phase 999.1 protocol extension tracer. It
exercises the declarative `visual` item grammar across the four advanced
families -- `hotspot`, `timeline`, `diagram`, `trace` -- on top of the 06.1
plot/number-line items, which are carried over verbatim to prove the additive
extension keeps them byte-compatible. It is not derived from any real course,
exam, or textbook, and no real question bank belongs in this repository.
`[SCORING:]` is the private scoring envelope: it never appears in any
served/public payload.

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

Q5. Select the heart on the organ diagram.   (difficulty: recall)
[OBJECTIVE: anatomy:organs.locate]
[TYPE: visual]
[INTERACTION: hotspot]
[VISUAL: {"version":1,"plane":{"width":"10","height":"6"},"regions":[{"id":"heart","label":"Heart","shape":"circle","coords":["2","3","1.5"]},{"id":"liver","label":"Liver","shape":"rect","coords":["6","2","3","2"]},{"id":"lungs","label":"Lungs","shape":"polygon","coords":[["1","5"],["4","5"],["2.5","3.5"]]}],"initial":{"region":null},"actions":["select_hotspot"],"accessibility":{"description":"A diagram of three organs: a heart, a liver and the lungs. Select the heart."}}]
[SCORING: {"kind":"hotspot","accepted":[{"region":"heart"}],"tolerance":{},"partial_credit":false}]

WHY BEST: The heart is the only circular organ among the three regions, drawn as a circle on the left side of the diagram.

KEY DISCRIMINATOR: The correct region is identified by its label and shape, not by position alone — the lungs also sit on the left but are drawn as a polygon.

SECOND-BEST: The lungs are the leftmost region; they would be correct if the prompt asked for the organ that fills the upper left.

DISTRACTOR ANALYSIS:
- The lungs form the polygon at the top left; this would be correct if the item asked for the upper-left organ.
- The liver is the rectangle on the right; this would be correct if the item asked for the organ on the right side.

TRAP: Picking the leftmost region without reading the label, so the lungs win over the heart.

CONFIDENCE: high

Q6. Select the region showing the state of Montana.   (difficulty: application)
[OBJECTIVE: geography:us.states]
[TYPE: visual]
[INTERACTION: hotspot]
[VISUAL: {"version":1,"plane":{"width":"12","height":"8"},"regions":[{"id":"montana","label":"Montana","shape":"rect","coords":["1","1","4","3"]},{"id":"texas","label":"Texas","shape":"rect","coords":["6","4","5","3"]},{"id":"florida","label":"Florida","shape":"polygon","coords":[["8","1"],["11","1"],["11","2.5"],["8","3"]]}],"initial":{"region":null},"actions":["select_hotspot"],"accessibility":{"description":"A schematic map with three rectangular or polygonal regions labelled Montana, Texas and Florida. Select the region showing Montana."}}]
[SCORING: {"kind":"hotspot","accepted":[{"region":"montana"}],"tolerance":{},"partial_credit":false}]

WHY BEST: Montana is the northern rectangle spanning the top-left of the schematic map.

KEY DISCRIMINATOR: Montana is the top-left rectangle; Texas is the bottom-left rectangle and Florida the bottom-right polygon.

SECOND-BEST: Texas is also a rectangle; it would be correct if the prompt asked for the southern rectangle.

DISTRACTOR ANALYSIS:
- Texas is the lower rectangle; this would be correct if the item asked for the southern state.
- Florida is the polygon on the right; this would be correct if the item asked for the southeastern state.

TRAP: Choosing any rectangle without checking its position, so Texas looks as plausible as Montana.

CONFIDENCE: high

Q7. Select the region that contains the number 4 on this target.   (difficulty: analysis)
[OBJECTIVE: logic:classification.regions]
[TYPE: visual]
[INTERACTION: hotspot]
[VISUAL: {"version":1,"plane":{"width":"8","height":"8"},"regions":[{"id":"ring","label":"Ring band","shape":"circle","coords":["4","4","3"]},{"id":"center","label":"Center bullseye","shape":"circle","coords":["4","4","1"]},{"id":"corner","label":"Corner square","shape":"rect","coords":["0","0","2","2"]}],"initial":{"region":null},"actions":["select_hotspot"],"accessibility":{"description":"A circular target with a ring band, a center bullseye and a corner square. Select the region that contains the number 4."}}]
[SCORING: {"kind":"hotspot","accepted":[{"region":"ring"}],"tolerance":{},"partial_credit":false}]

WHY BEST: The number 4 sits between the bullseye radius 1 and the ring radius 3, so it lies in the ring band, not the bullseye.

KEY DISCRIMINATOR: The ring band excludes both the center disk and the corner square; the number 4 falls strictly in the band.

SECOND-BEST: The center bullseye is the innermost region; it would be correct if the number sat within radius 1.

DISTRACTOR ANALYSIS:
- The center bullseye covers only radius 1; this would be correct if the number 4 were within one unit of the center.
- The corner square overlaps nothing; this would be correct if the number 4 were drawn in the top-left corner.

TRAP: Picking the visually central region (bullseye) because "center" feels like the default answer.

CONFIDENCE: high

Q8. Place the fall of Rome at year 5 on the timeline.   (difficulty: recall)
[OBJECTIVE: history:world.timeline]
[TYPE: visual]
[INTERACTION: timeline]
[VISUAL: {"version":1,"axis":{"min":"0","max":"10","step":"1"},"events":[{"id":"fall","label":"Fall of Rome"},{"id":"printing","label":"Printing press"}],"initial":{"placements":[]},"actions":["place_timeline_event","move_timeline_event"],"accessibility":{"description":"A timeline from year 0 to year 10 marked in whole years. Place the fall of Rome at year 5."}}]
[SCORING: {"kind":"timeline_event","accepted":[{"event":"fall","value":"5"}],"tolerance":{"value":"0"},"partial_credit":false}]

WHY BEST: 476 CE is conventionally dated to the fall of Rome; on this 0-10 timeline it is the midpoint, year 5.

KEY DISCRIMINATOR: The event id and the year must both match — placing the printing press at 5 is as wrong as placing Rome at 8.

SECOND-BEST: The printing press is the other event; it would be correct if the prompt asked for the later invention.

DISTRACTOR ANALYSIS:
- Placing the printing press at 5 mixes the right year with the wrong event; this would be correct if the prompt asked for the printing press at year 5.
- Placing the fall of Rome at 8 is a plausible guess at a "late" date; it would be correct only if the prompt said year 8.

TRAP: Finding the right year and forgetting which event label goes with it.

CONFIDENCE: high

Q9. Place the industrial revolution within one year of year 7 on the timeline.   (difficulty: application)
[OBJECTIVE: history:world.timeline.tolerance]
[TYPE: visual]
[INTERACTION: timeline]
[VISUAL: {"version":1,"axis":{"min":"0","max":"10","step":"1"},"events":[{"id":"industrial","label":"Industrial revolution"},{"id":"reformation","label":"Reformation"}],"initial":{"placements":[]},"actions":["place_timeline_event","move_timeline_event"],"accessibility":{"description":"A timeline from year 0 to year 10. Place the industrial revolution within one year of year 7."}}]
[SCORING: {"kind":"timeline_event","accepted":[{"event":"industrial","value":"7"}],"tolerance":{"value":"1"},"partial_credit":false}]

WHY BEST: The tolerated window is [6, 8]: years 6, 7 and 8 all sit within one year of 7 and are accepted.

KEY DISCRIMINATOR: Tolerance is inclusive — 6 and 8 pass exactly on the boundaries while 5 and 9 fail.

SECOND-BEST: Year 5 is two years from 7; it would be correct only under a tolerance larger than one.

DISTRACTOR ANALYSIS:
- Year 5 is two years before 7; this would be correct if the tolerance were two or more.
- Year 9 is two years after 7; this would be correct if the tolerance were two or more.

TRAP: Treating the tolerance as exclusive so that 6 and 8 fail when they should pass.

CONFIDENCE: high

Q10. Connect premise A to the conclusion in this argument diagram.   (difficulty: analysis)
[OBJECTIVE: logic:argument.structure]
[TYPE: visual]
[INTERACTION: diagram]
[VISUAL: {"version":1,"plane":{"width":"8","height":"6"},"nodes":[{"id":"a","label":"Premise A","x":"2","y":"4"},{"id":"b","label":"Premise B","x":"6","y":"4"},{"id":"c","label":"Conclusion","x":"4","y":"1"}],"initial":{"connections":[]},"actions":["connect_diagram"],"accessibility":{"description":"An argument diagram with two premises at the top and a conclusion at the bottom. Connect premise A to the conclusion."}}]
[SCORING: {"kind":"diagram_connection","accepted":[{"from":"a","to":"c"}],"tolerance":{},"partial_credit":false}]

WHY BEST: Premise A is the left-hand premise and the conclusion is the bottom node; the argument runs from premise to conclusion.

KEY DISCRIMINATOR: The connection is ordered — premise A to the conclusion, not the conclusion to premise A, and not premise B.

SECOND-BEST: Premise B is the right-hand premise; it would be correct if the prompt asked for the second premise.

DISTRACTOR ANALYSIS:
- Premise B to the conclusion swaps the premise; this would be correct if the prompt named premise B.
- Reversing the direction (conclusion to premise A) changes what the edge means; this would be correct only in a conclusion-to-premise diagram.

TRAP: Connecting any premise to the conclusion without checking which premise the prompt names.

CONFIDENCE: high

Q11. Trace the V-shaped path by placing three points exactly on it.   (difficulty: application)
[OBJECTIVE: geometry:paths.trace]
[TYPE: visual]
[INTERACTION: trace]
[VISUAL: {"version":1,"axes":{"x":{"min":"0","max":"4","step":"1"},"y":{"min":"0","max":"4","step":"1"}},"point_count":3,"initial":{"points":[{"x":"0","y":"0"},{"x":"2","y":"2"},{"x":"4","y":"0"}]},"actions":["place_trace_point","move_trace_point"],"accessibility":{"description":"A grid from 0 to 4 on both axes with a V-shaped reference path. Place three points exactly on the path."}}]
[SCORING: {"kind":"trace_path","accepted":[{"points":[{"x":"0","y":"0"},{"x":"2","y":"2"},{"x":"4","y":"0"}]}],"tolerance":{"x":"0","y":"0"},"partial_credit":false}]

WHY BEST: The V dips at (2, 2) between the two endpoints; the three points (0, 0), (2, 2) and (4, 0) reproduce it exactly.

KEY DISCRIMINATOR: The order matters — (0, 0) then (2, 2) then (4, 0) — and every point must land exactly on a grid cell.

SECOND-BEST: (2, 0) sits on the baseline; it would be correct if the path were a straight horizontal line.

DISTRACTOR ANALYSIS:
- (2, 0) is the midpoint of the baseline, not the V's dip; this would be correct if the path were flat.
- Reordering the points (endpoint first) breaks the element-wise comparison; this would be correct if order did not matter.

TRAP: Placing the middle point on the baseline because the V's dip is easy to miss at a glance.

CONFIDENCE: high

Q12. Trace the valley by placing three points within half a unit of it.   (difficulty: analysis)
[OBJECTIVE: geometry:paths.trace.tolerance]
[TYPE: visual]
[INTERACTION: trace]
[VISUAL: {"version":1,"axes":{"x":{"min":"0","max":"4","step":"1/2"},"y":{"min":"0","max":"4","step":"1/2"}},"point_count":3,"initial":{"points":[{"x":"0","y":"2"},{"x":"2","y":"0"},{"x":"4","y":"2"}]},"actions":["place_trace_point","move_trace_point"],"accessibility":{"description":"A grid marked in half steps with a valley-shaped reference path. Place three points within half a unit of the path."}}]
[SCORING: {"kind":"trace_path","accepted":[{"points":[{"x":"0","y":"2"},{"x":"2","y":"0"},{"x":"4","y":"2"}]}],"tolerance":{"x":"1/2","y":"1/2"},"partial_credit":false}]

WHY BEST: Each accepted point tolerates a half-unit shift in x and y, so (1/2, 3/2) is still within range of the valley's left arm at (0, 2).

KEY DISCRIMINATOR: The tolerance is inclusive — a point exactly half a unit away passes, a full unit away fails, and every point is compared element-wise in order.

SECOND-BEST: (1, 1) is a full unit from the left arm; it would be correct only under a tolerance of one.

DISTRACTOR ANALYSIS:
- (1, 1) sits a full unit from (0, 2) in x; this would be correct if the tolerance were one.
- Reordering the points fails the element-wise comparison; this would be correct if order did not matter.

TRAP: Shifting a point by a whole unit and assuming the half-unit tolerance still covers it.

CONFIDENCE: high
