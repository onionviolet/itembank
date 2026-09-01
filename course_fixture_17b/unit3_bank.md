# Unit 3 bank: Peat Hydrology and the Lantern Moss Cycle (synthetic)

Synthetic assessment content for the 17B tracer (Aldrasse fen ecology,
invented). Every station, figure, and species is fictional, and nothing
here derives from any real course, exam, or textbook. The teaching text
lives in `unit3_lesson.md` through the `[LESSON-SRC:]` directive below.
Scenario stems not present in the sources are authored synthesis and say
so in their rationale.

[LESSON-SRC: unit3_lesson.md]

## SOURCES

fen-notes | sources/fen_hydrology_field_notes.md
moss-survey | sources/lantern_moss_survey.md

## TERMS

minerotrophic | Fed by mineral-rich groundwater arriving laterally, rather than by rainfall alone | mineral-fed
acrotelm | The upper, loosely decomposed peat layer with high hydraulic conductivity, where storm water moves and exits
catotelm | The dense, deep peat layer that conducts water poorly and dries only slowly from the top
lagg | The transitional zone where ridge seepage first enters a fen, wetter and more mineral-rich than the interior
vitality score | The survey's four-point condition rating of a lantern moss cushion, averaged per station

## ACTIVITIES

4dc7c93e7a4c4f18 | prediction | commit to a forecast before the mechanism is taught | afe:unit3.layers | The storm question posed in the lesson's Two Layers, Two Clocks section | mc | none | after_commitment | activity_trace | A labelled radio group in document order, answerable by keyboard alone | Write your prediction down, then read the section and compare it with what you wrote.
dc4b3fe5b0f64b2b | practice | sequence the cycle from memory after the diagram | afe:unit3.cycle | The annual cycle diagram and its static description | build | unlimited | after_commitment | scored_by_runtime | The steps are a keyboard-orderable list with labelled move controls | Write the four phases in order on paper, then check against the diagram's static description.
a42004eabf0343b9 | explanation | connect the two sources' thresholds in prose | afe:unit3.instrument | Both threshold statements, kept in view | short | none | withheld_until_submit | pending_human_mark | A labelled text area reachable in document order, with no time limit | Write the explanation in full sentences, then compare it with the model answer when it is released.
56178d0782344bc4 | transfer | apply the calibrated convention in an unfamiliar basin | afe:unit3.instrument | An invented basin the sources never surveyed | mc | none | after_commitment | scored_by_runtime | A labelled radio group in document order, answerable by keyboard alone | Answer on paper, then read the rationale for the boundary the convention does not cross.

## MEDIA

moss-cycle | media/lantern_moss_cycle.svg | Diagram drawn for this unit, synthetic | Four phases in a clockwise circle: spring green-up, then early-summer investment, then the late-summer lantern phase, then the autumn wager. The arrow into early-summer investment is marked as the hinge, because the water position then decides whether a shoot initiates fertile stems or banks the season as vegetative growth. | granted | Drawn from the Annual cycle section of lantern_moss_survey.md; synthesis, no tracing of any published figure. | present | sha256:b3d2467be2859a588fd41cb37ddde52b66a79ecf44dca842edb1d43790fe42b0

Q1. Your prediction from the lesson: after a heavy storm on the Aldrasse fen, what does the water table do?   (difficulty: application)
[ID: 4dc7c93e7a4c4f18]
[HASH: sha256:602b307b93eaf821]
[OBJECTIVE: afe:unit3.layers]
[LESSON-REF: Two Layers, Two Clocks]
[SRC: fen-notes #water-table-dynamics]

A) It stays high for several weeks while the catotelm drains
B) It rises slowly over the following month as recharge arrives
C) It spikes sharply, then decays back over three to five days
D) It does not respond, because storms bypass a minerotrophic fen

CORRECT: C

WHY BEST: Storm water moves laterally through the high-conductivity acrotelm and exits at the flark margin, so the spike decays within days.

KEY DISCRIMINATOR: The acrotelm's conductivity is what turns a storm into a short spike rather than a lasting rise.

SECOND-BEST: B. Slow rise is the seasonal recharge clock; this would be correct if the question asked about autumn ridge seepage rather than a storm event.

DISTRACTOR ANALYSIS:
- A) This would be correct if the table sat in the catotelm, which holds water and dries slowly; a storm spike lives in the acrotelm instead.
- B) This would be correct for seasonal recharge, the slow clock; a storm is the fast clock.
- C) Correct: sharp spike, three to five day decay, per the dipwell records.
- D) This would be correct for no known wetland; minerotrophic describes where water comes from, not indifference to rain.

TRAP: Confusing the two clocks: the storm response with the seasonal recharge response.

CONFIDENCE: high

Q2. The Aldrasse fen carries a sedge and brown moss community instead of a Sphagnum lawn. What sets that community?   (difficulty: application)
[ID: 1c51d625bcc84d55]
[HASH: sha256:7a39f8cb0e30fe01]
[OBJECTIVE: afe:unit3.minerotrophy]
[LESSON-REF: Why The Fen Is Minerotrophic]
[SRC: fen-notes #basin-overview]

A) Cold air pooling in the glacial trough
B) Lateral mineral inflow buffering the porewater near pH 6.2 to 6.8
C) The forty meter spacing of the monitoring transect
D) Rainfall chemistry, since fens are fed from above

CORRECT: B

WHY BEST: The dissolved calcium and magnesium arriving with lateral seepage buffer the porewater, and that buffered chemistry feeds the sedge and brown moss community.

KEY DISCRIMINATOR: The causal chain runs from lateral inflow through porewater chemistry to the plant community.

SECOND-BEST: D. Water source is the right axis; this would be correct for a rain-fed bog, which is exactly what the fen is not.

DISTRACTOR ANALYSIS:
- A) This would be correct if the question asked about frost hollows; temperature is not the notes' causal chain.
- B) Correct: mineral inflow, buffered pH, sedge and brown moss.
- C) This would be correct for nothing biological; the transect measures the fen and does not make it.
- D) This would be correct for an ombrotrophic bog, where rainfall is the only input.

TRAP: Reading "fen" as "bog" and reaching for rainfall.

CONFIDENCE: high

Q3. Which two roles do the field notes give the lagg zone?   (difficulty: application)
[ID: 6c4d32df2dce4a80]
[HASH: sha256:d1a10179d7d01510]
[TYPE: multi]
[SELECT: 2]
[OBJECTIVE: afe:unit3.lagg]
[LESSON-REF: Read The Source: The Lagg Boundary]
[SRC: fen-notes #mineral-inflow-and-the-lagg-boundary]

A) The fen's chemical gatekeeper, where delivered calcium is taken up before water reaches the interior
B) The fen's main carbon bank, where the deepest peat accumulates
C) The habitat of the densest Sphagnum growth in the basin
D) The early-warning line, where disturbance shows in porewater chemistry seasons before the interior shifts
E) The zone of lowest specific conductance on the transect

CORRECT: A, D

WHY BEST: The notes name exactly two reasons the lagg matters: chemical gatekeeper and early-warning line.

KEY DISCRIMINATOR: Both roles are about the lagg intercepting what enters the fen, chemically and diagnostically.

SECOND-BEST: E. Conductance is the right instrument; this would be correct inverted, since the lagg runs mineral-rich and the interior runs leaner.

DISTRACTOR ANALYSIS:
- A) Correct: calcium precipitates or is taken up in the lagg, so the central flark runs leaner than station A1.
- B) This would be correct for the central flark, where three meters of profile sit; the lagg is the edge, not the bank.
- C) This would be correct in a rain-fed system; the mineral-rich lagg is exactly where Sphagnum loses to brown mosses.
- D) Correct: ditching, salting, and runoff appear in lagg porewater seasons early.
- E) This would be correct for the interior; the lagg is where conductance runs highest, which is why station A1 is read first.

TRAP: Placing the fen's superlatives (deepest peat, most Sphagnum) at its most visible edge.

CONFIDENCE: high

Q4. Put the four phases of the lantern moss survey year in order, starting in spring.   (difficulty: application)
[ID: dc4b3fe5b0f64b2b]
[HASH: sha256:63a35a57c1c0198c]
[TYPE: build]
[OBJECTIVE: afe:unit3.cycle]
[LESSON-REF: The Annual Cycle Of Lantern Moss]
[SRC: moss-survey #annual-cycle]

STEP) Green-up and extension growth at the annual water table high
STEP) Investment: shoots near the capillary fringe initiate fertile stems
STEP) Lantern phase: capsules swell, blanch, and release spores
STEP) Wager: stored sugars go to rhizoid growth against ice heave

CORRECT: A, B, C, D

WHY BEST: The survey year runs spring green-up, early-summer investment, late-summer lantern, autumn wager, in that order.

KEY DISCRIMINATOR: Investment precedes the lantern phase: fertile stems are initiated in early summer and the capsules ripen in late summer.

SECOND-BEST: Swapping the lantern and wager phases; that would be correct if spore release happened after the autumn commitment, but the northerly winds of September come first.

DISTRACTOR ANALYSIS:
- The trap ordering places the wager before the lantern phase; it would be correct if the cushion committed reserves before releasing spores, but the autumn wager is the year's last act.
- Placing investment after the lantern phase would be correct only if capsules appeared without initiation; the fertile stems must be initiated a phase earlier.
- Starting the year at the lantern phase would be correct for a calendar beginning in September; the survey year starts at ice-out.

TRAP: Treating "wager" as the early-summer decision; the survey names autumn the wager phase, while early summer is the investment that the wager language describes.

CONFIDENCE: high

Q5. Under the monitoring protocol, which observation marks a drought state at a dipwell station?   (difficulty: recall)
[ID: 3010fee339a94556]
[HASH: sha256:4a60ceb12bbcd2b0]
[OBJECTIVE: afe:unit3.threshold]
[LESSON-REF: The Drought Threshold]
[SRC: fen-notes #water-table-dynamics]

A) Any summer drawdown below the peat surface
B) A water table eighteen centimeters below the surface
C) A crest-stage tube reading above the peat surface
D) A water table more than twenty five centimeters below the surface

CORRECT: D

WHY BEST: The notes set the drought line at more than twenty five centimeters below the surface, with the vegetation registering an excursion within a fortnight.

KEY DISCRIMINATOR: Eighteen centimeters is the ordinary summer extreme; twenty five is the threshold.

SECOND-BEST: B. Eighteen centimeters is a number from the same paragraph; it would be correct if the question asked how far ordinary summer drawdown reaches.

DISTRACTOR ANALYSIS:
- A) This would be correct if any drawdown were abnormal; summer drawdown to eighteen centimeters is routine.
- B) This would be correct for the typical summer maximum drawdown, not the drought line.
- C) This would be correct for flood recording; a crest-stage tube marks high water, not drought.
- D) Correct: past twenty five centimeters is the drought state.

TRAP: Grabbing the first number in the paragraph instead of the threshold.

CONFIDENCE: high

Q6. A neighboring profile accumulates peat at half a millimeter per year. About how old is the peat at two meters depth, using the unit's method?   (difficulty: application)
[ID: 9dd7c46e5e704669]
[HASH: sha256:f6843a91736fe7cb]
[OBJECTIVE: afe:unit3.peat]
[LESSON-REF: Banking Peat]
[SRC: fen-notes #peat-accumulation-and-decay]

A) About four thousand years
B) About one thousand years
C) About four hundred years
D) It cannot be estimated without a productivity record

CORRECT: A

WHY BEST: Depth divided by rate: 2000 millimeters at 0.5 millimeters per year is about four thousand years. The numbers are changed from the source's worked example; the method is the source's.

KEY DISCRIMINATOR: Keep the units honest: meters to millimeters before dividing.

SECOND-BEST: B. This would be correct at the Aldrasse rate of one millimeter per year; the stem halves the rate.

DISTRACTOR ANALYSIS:
- A) Correct: 2000 divided by 0.5 is 4000.
- B) This would be correct if the rate were one millimeter per year, the A5 figure carried over unread.
- C) This would be correct if the division ran the wrong way (2000 times 0.5 read as 400 through a dropped digit); it punishes inverting the rate.
- D) This would be correct if accumulation tracked productivity, which the notes explicitly deny; the water table, not growth, decides the rate.

TRAP: Importing the source's rate instead of the stem's, or inverting the division.

CONFIDENCE: high

Q7. A station in the lagg arc has no dipwell. Explain how the survey protocol still detects a drought excursion there, and why that inference is trusted.   (difficulty: analysis)
[ID: a42004eabf0343b9]
[HASH: sha256:b121bb8b44a04f7b]
[TYPE: short]
[OBJECTIVE: afe:unit3.instrument]
[LESSON-REF: Moss As Instrument]
[SRC: moss-survey #hydrological-sensitivity]

MODEL: Lantern moss vitality is scored on five cushions per station; a station mean below 2.5 is treated as equivalent to a recorded drought excursion, because nine seasons of plot data show browning past the same twenty five centimeter, four week line the hydrology notes define as drought. The moss integrates water position with about a one month lag, so it stands in for the missing instrument.

RUBRIC:
- Names the station-mean vitality threshold (below 2.5) as the drought-equivalent signal
- Connects it to the dipwell drought definition (more than twenty five centimeters down, sustained about four weeks)
- States the evidential basis or its limit (nine seasons of plot data at this one fen, roughly one month lag)

TRAP: A confident answer that treats the moss score as a direct water table measurement rather than a lagged, calibrated stand-in.

CONFIDENCE: high

Q8. In the Virsk fen, a basin the sources never surveyed, a crew finds a station with a lantern moss mean vitality of 2.2 held for five weeks and no dipwell. Under the Aldrasse conventions, what is the defensible reading?   (difficulty: analysis)
[ID: 56178d0782344bc4]
[HASH: sha256:ce442696796788a9]
[OBJECTIVE: afe:unit3.instrument]
[LESSON-REF: Moss As Instrument]
[SRC: moss-survey #hydrological-sensitivity]

A) The station is flooded, since cushions tolerate flooding without cost
B) Nothing can be concluded, because vitality scores are not hydrological data
C) Treat it as a drought-equivalent signal, flagged as an out-of-basin extrapolation of a nine season, single fen calibration
D) Declare a certified drought excursion identical to a dipwell record

CORRECT: C

WHY BEST: A mean below 2.5 is the drought-equivalent convention, and the lesson's uncertainty note requires flagging that the calibration comes from one basin. This scenario is authored synthesis: the Virsk fen appears in no source.

KEY DISCRIMINATOR: The convention transfers as a flagged inference, not as a certified measurement.

SECOND-BEST: D. The threshold reading is right; this would be correct if the calibration were established for the Virsk fen rather than borrowed from the Aldrasse plots.

DISTRACTOR ANALYSIS:
- A) This would be correct if vitality dropped under flooding, but the response is asymmetric: flooding is tolerated and drought browns the crown.
- B) This would be correct if the survey had never calibrated vitality against the water table; nine seasons of plot data are exactly that calibration.
- C) Correct: apply the convention, state the extrapolation.
- D) This would be correct inside the calibrated basin under the monitoring convention; uncalibrated transfer overstates it.

TRAP: Either refusing a usable calibrated signal or promoting it to a certainty it does not have.

CONFIDENCE: high
