# Unit 3 lesson: Peat Hydrology and the Lantern Moss Cycle

Synthetic teaching content for the 17B tracer (Aldrasse fen ecology,
invented). This file is the durable authored lesson: it must read
coherently in a plain Markdown reader on its own, and it is served
richly through `unit3_bank.md`, whose `[LESSON-SRC:]` directive points
here. Source-derived claims cite the two synthetic sources by section;
paragraphs marked as synthesis combine both sources and are labeled.

[SEMANTIC-PROFILE: 1]
[LESSON-LANG: en]

## SOURCES

fen-notes | fen_hydrology_field_notes.md
moss-survey | lantern_moss_survey.md

The `## TERMS` and `## MEDIA` registries for this lesson live in
`unit3_bank.md`, the file the linter reads them from; the definitions
below are also written into the prose, so this file stays coherent on
its own.

## LESSON

### Why The Fen Is Minerotrophic

The Aldrasse fen sits in a shallow glacial trough, and the fact that
organizes everything else about it is where its water comes from. The
fen is [[minerotrophic]]: water arrives laterally, seeping from the
ridge aquifers, and carries dissolved calcium and magnesium picked up
from the till [SRC: fen-notes #basin-overview].

Follow the causal chain, because the items in this unit test the chain
and not the label. Lateral inflow brings minerals; the minerals buffer
the porewater near a pH of 6.2 to 6.8; the buffered chemistry feeds a
sedge and brown moss community rather than a Sphagnum lawn. Remove the
lateral inflow and every link downstream changes, which is why the notes
call the mineral supply the single most consequential fact about the
system [SRC: fen-notes #basin-overview].

### Two Layers, Two Clocks

Before reading further, make a prediction and write it down: after a
heavy storm, does the fen's water table stay high for weeks, or fall
back within days? Commit to one answer now; the first practice item
records your prediction as participation, not as a grade.

The water table behaves like a damped oscillator driven by two inputs on
different clocks: slow seasonal recharge from ridge seepage, and sharp
storm spikes that decay over three to five days
[SRC: fen-notes #water-table-dynamics].

The damping lives in the peat's two-layer structure. The [[acrotelm]]
conducts water two to three orders of magnitude better than the
[[catotelm]] below it, so storm water moves laterally through the upper
layer and exits at the flark margin before it can pressurize the deep
profile. The same structure explains the asymmetry you predicted above:
a table sitting in the acrotelm sheds water quickly and stays wet, while
a table that drops into the catotelm holds what it has and dries slowly
from the top [SRC: fen-notes #water-table-dynamics].

### The Drought Threshold

> [!KEY] The Aldrasse drought threshold
> [ID: 76f829119a7142fd]
> [HASH: sha256:5ea8c1ba1b8ac63f]
> A water table more than twenty five centimeters below the peat surface
> is a drought state, and the vegetation registers an excursion past it
> within a fortnight [SRC: fen-notes #water-table-dynamics].

Summer drawdown rarely lowers the table more than eighteen centimeters,
so the threshold is not a routine season; it is the line the monitoring
protocol watches [SRC: fen-notes #water-table-dynamics].

### Banking Peat

> [!EXAMPLE]
> The dated ash layer at station A5 gives an accumulation rate just
> under one millimeter per year. Three meters of profile under the
> central flark, at one millimeter per year, represents roughly three
> thousand years of banked carbon: divide the depth by the rate, and
> keep the units honest (3000 mm divided by 1 mm per year)
> [SRC: fen-notes #peat-accumulation-and-decay].

The race that forms peat is decided by oxygen, not by growth. Above the
water table, aerobic decay consumes fresh litter within a few seasons;
below it, decay runs at perhaps one hundredth that rate. So accumulation
tracks the position of the water table, not the productivity of the
surface: a wet year with modest growth banks more peat than a lush dry
year, because the decay term moves more than the production term
[SRC: fen-notes #peat-accumulation-and-decay].

### Read The Source: The Lagg Boundary

This objective's treatment is direct source reading. Read the section
"Mineral inflow and the lagg boundary" in the field notes
[SRC: fen-notes #mineral-inflow-and-the-lagg-boundary]; it is narrative,
ordered, and self-contained, and this lesson does not paraphrase it. As
you read, hold two questions: what are the [[lagg]] zone's two roles,
and what condition at station A1 triggers a full transect resample?

### The Annual Cycle Of Lantern Moss

The survey year divides into four observable phases: spring green-up,
early-summer investment, the late-summer lantern phase, and the autumn
wager [SRC: moss-survey #annual-cycle].

[MEDIA: moss-cycle]

The hinge is the early-summer water position. A shoot within two
centimeters of the capillary fringe initiates fertile stems; a drier
shoot skips reproduction and banks the season as vegetative growth. A
cushion that misreads the hinge loses both the capsules and the deferred
growth, and the plot records show such double losses take two full
seasons to recover [SRC: moss-survey #annual-cycle].

> [!MISCONCEPTION]
> The lantern phase is not the wager. The capsules blanch and release
> spores in late summer; the wager is the autumn commitment of stored
> sugars to rhizoid growth against winter ice heave. The bet was placed
> earlier, in early summer, when the shoot chose reproduction over
> growth [SRC: moss-survey #annual-cycle].

### Moss As Instrument

This section is synthesis: it combines the two sources' thresholds, and
the connection is the survey's own claim from nine seasons of plot data
[SRC: moss-survey #hydrological-sensitivity]
[SRC: fen-notes #water-table-dynamics].

Cushion vitality tracks the mean summer water table with a lag of about
one month, and the response is asymmetric: brief flooding costs nothing,
but four weeks with the table more than twenty five centimeters down
browns a cushion from the crown outward. That is the same twenty five
centimeter line as the hydrology notes' drought threshold, which is what
makes the moss usable as an instrument: a station mean
[[vitality score]] below 2.5 is treated as equivalent to a recorded
drought excursion where no dipwell is installed
[SRC: moss-survey #hydrological-sensitivity].

> [!TIP]
> Field crews read the moss before the dipwell. Browning starts at the
> cushion crown, so scan crowns on the walk in; a station whose crowns
> are browning in a wet-looking fen is the cue to pull the dipwell
> record early rather than at the scheduled visit.

> [!UNCERTAINTY]
> The equivalence between a station mean below 2.5 and a dipwell drought
> excursion rests on nine seasons at one fen. Treat it as a monitoring
> convention supported by the survey's own data, not as a law that
> transfers to other basins unmeasured.

> [!SUMMARY]
> Lateral mineral inflow makes the fen what it is; the acrotelm and
> catotelm put the water table on two clocks; twenty five centimeters
> down for too long is drought; peat follows the water table, not the
> weather; the lagg is gatekeeper and early-warning line; the moss's
> year turns on the early-summer water position; and a moss cushion,
> read carefully, is a hydrological instrument.
