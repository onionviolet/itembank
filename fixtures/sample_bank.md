# Sample bank (synthetic)

Fully invented content for a fictional municipal water-treatment operator
certification. It exists to exercise all five item types and to give `lint`
something that passes cleanly. It is not derived from any real course, exam, or
textbook, and no real question bank belongs in this repository.

Q1. An operator notices the chlorine residual at the far end of the distribution network has fallen below the regulatory floor, while the reading at the plant outlet is normal. What is the most likely explanation?   (difficulty: application)
[OBJECTIVE: Distribution / residual maintenance]

A) The plant is underdosing chlorine
B) Chlorine demand in the network is consuming the residual before it reaches the far end
C) The far-end sampling tap is contaminated
D) The regulatory floor was recently raised

CORRECT: B

WHY BEST: A normal outlet reading rules out underdosing at the source, so the loss is happening in transit. Chlorine demand from biofilm, sediment, and long residence time consumes residual as water travels.

KEY DISCRIMINATOR: The outlet reading is normal. That single fact separates a dosing problem from a transit problem.

SECOND-BEST: C. A contaminated tap would also produce a low reading, and it is worth ruling out, but it explains one sample rather than a systemic pattern at the network edge.

DISTRACTOR ANALYSIS:
- A) Underdosing would depress the plant outlet reading too; this would be correct if the outlet reading were also low.
- B) Correct: demand in transit consumes the residual.
- C) A dirty tap is a real cause of a single bad sample, and this would be right if only one tap out of several at the same location read low.
- D) A changed standard alters the threshold, not the measurement; this would be correct if the question asked why a previously compliant reading is now a violation.

TRAP: Reading a low number as a dosing failure without checking where in the system it was measured.

CONFIDENCE: high

Q2. Which conditions require an immediate boil-water notice?   (difficulty: application)
[TYPE: multi]
[SELECT: 2]
[OBJECTIVE: Public notification]

A) Loss of positive pressure across the distribution system
B) A single customer complaint about taste
C) Confirmed detection of E. coli in a routine sample
D) A scheduled hydrant flushing program
E) A turbidity reading slightly below the action level

CORRECT: A, C

WHY BEST: Both indicate a credible pathway for pathogens to reach customers. Loss of pressure allows intrusion; a confirmed indicator organism means contamination is already present.

KEY DISCRIMINATOR: Is there a plausible route for pathogens to reach a customer right now?

SECOND-BEST: Not applicable; the remaining options describe aesthetic, planned, or in-compliance conditions.

DISTRACTOR ANALYSIS:
- A) Correct: pressure loss permits intrusion.
- B) Taste is aesthetic; this would be correct if the question asked what triggers a secondary-standard investigation.
- C) Correct: a confirmed indicator organism.
- D) Planned flushing is routine; it would be right if the question asked what causes temporary discoloration complaints.
- E) Below the action level means in compliance, and it would be correct if the reading were above it.

TRAP: Treating any abnormal reading as a notification trigger. Notification follows a pathogen pathway, not an inconvenience.

CONFIDENCE: high

Q3. Classify each task as ROUTINE or EMERGENCY response.   (difficulty: recall)
[TYPE: table]
[CATEGORIES: Routine | Emergency]
[OBJECTIVE: Operations]

ROW) Monthly calibration of a turbidimeter :: Routine
ROW) Responding to a confirmed main break flooding a street :: Emergency
ROW) Quarterly lead and copper sampling :: Routine
ROW) Isolating a section after a chemical spill enters a storm drain :: Emergency

WHY BEST: Scheduled, calendar-driven work is routine. Unplanned events that threaten water quality or public safety are emergencies.

KEY DISCRIMINATOR: Was this on the calendar before today?

DISTRACTOR ANALYSIS:
- The two routine rows are both calendar-driven, despite covering different equipment and regulations, which is the point: the subject matter does not determine the category.
- The main break is the row most often misfiled as routine, because breaks are common. Frequency is not the same as scheduling.

TRAP: Sorting by how familiar the task feels rather than by whether it was planned.

CONFIDENCE: high

Q4. Put the conventional surface-water treatment train in order.   (difficulty: recall)
[TYPE: build]
[OBJECTIVE: Treatment processes]

STEP) Coagulation
STEP) Flocculation
STEP) Sedimentation
STEP) Filtration
STEP) Disinfection

WHY BEST: Coagulant destabilises particles, gentle mixing grows them into settleable floc, gravity removes the bulk, filtration removes what remains, and disinfection treats the clarified water.

KEY DISCRIMINATOR: Each step conditions the water for the next, so the order is causal rather than conventional.

DISTRACTOR ANALYSIS:
- Swapping coagulation and flocculation is the common error: they are often spoken of as one step, but destabilising must precede aggregating.
- Placing disinfection first looks defensible if you think of it as killing pathogens early; disinfection is placed last because organic load and turbidity consume disinfectant and shield organisms.

TRAP: Treating the train as an arbitrary sequence to memorise rather than a chain where each step depends on the previous one.

CONFIDENCE: high

Q5. Sort each parameter into PRIMARY or SECONDARY drinking-water standard.   (difficulty: recall)
[TYPE: dnd]
[CATEGORIES: Primary | Secondary]
[OBJECTIVE: Regulatory framework]

ITEM) Total coliform :: Primary
ITEM) Lead :: Primary
ITEM) Iron staining laundry :: Secondary
ITEM) Odour :: Secondary

WHY BEST: Primary standards are enforceable and protect health. Secondary standards are guidelines covering aesthetics: taste, odour, colour, staining.

KEY DISCRIMINATOR: Does exceeding it make someone sick, or make them dislike the water?

DISTRACTOR ANALYSIS:
- Iron is the row that catches people, because a visible problem feels more serious than an invisible one. Visibility and health risk are unrelated.
- Coliform and lead are both invisible and both primary, which is the same lesson from the other direction.

TRAP: Ranking by how obvious the problem is to a customer rather than by health effect.

CONFIDENCE: high
