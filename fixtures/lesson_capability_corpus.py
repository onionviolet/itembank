#!/usr/bin/env python3
"""The Phase 16A stress-corpus generator (plan 16A-02 Task 1).

Every string in this file is fictional. Nothing here is a real course, a real
exam, a real syllabus, a real learner note, or a real question bank, and
nothing here is derived from or paraphrased out of any such material. The tide
table, the station name, the objective key, and every option and rationale
were invented to exercise the lesson grammar, and their only relationship to
real teaching material is their shape.

Standard library only and directly importable, following
`fixtures/grandchild_spawner.py`'s module shape: module-level functions, no
class, nothing that runs on import.

Determinism here is a literal rather than a seed. `THIN_SLICE_BANK` is a
module-level constant string, so two builds into two directories produce two
byte-identical files without a random module being involved at all, and a
diff of this file is a diff of the corpus.
"""
import os


THIN_SLICE_BANK = """# Reading a tide table (synthetic)

Fully invented teaching content for exercising the Phase 16A semantic and
capability grammar. It is not derived from any real course, exam, textbook, or
tide publication, and no real question bank belongs in this repository.

[SEMANTIC-PROFILE: 1]
[LESSON-LANG: en]
[LESSON-DIR: ltr]

## LESSON

### Reading A Tide Table

> [!PREREQUISITE]
> You can read a two column table and add whole numbers.

A tide table is a list of times paired with heights. Each row names a moment
when the water reaches a turning point, and the height beside it says how far
above or below the chart datum the water sits at that moment. Nothing in the
table describes the water between two rows, which is the most common thing a
first reader assumes it does.

> [!EXAMPLE]
> At the fictional station Kestrel Point, the table lists a high water at
> 04:12 and the next low water at 10:38. Those two rows say nothing about
> 07:00; they say only where the turning points fall.

Because the rows are turning points, the useful question is almost never what
the table says at a listed time. It is which pair of rows a moment falls
between, and which direction the water is moving across that interval.

Q1. A tide table for Kestrel Point lists a high water at 04:12 and a low water at 10:38. What does the table tell you about the water at 07:00?   (difficulty: application)
[LESSON-REF: Reading A Tide Table]
[OBJECTIVE: nav:tides]

A) The exact height of the water at 07:00
B) That the water is falling between two listed turning points
C) That the water is at its lowest point of the day
D) That no reading was taken at 07:00

CORRECT: B

WHY BEST: 07:00 falls between a listed high water and the next listed low
water, so the only thing the table establishes is the direction of travel
across that interval.

KEY DISCRIMINATOR: The answer must describe what two turning points imply
about the interval between them, not what happens at a listed row.

SECOND-BEST: A. The table does fix heights at its own rows, and this would be
correct if the question asked about 04:12 rather than about 07:00.

DISTRACTOR ANALYSIS:
- A) The table gives heights only at its listed turning points; this would be correct if the question named a listed time.
- B) Correct: 07:00 sits between a high water and the following low water, so the water is falling.
- C) The lowest listed point is 10:38, not 07:00; this would be correct if the question asked which row is the low water.
- D) A gap between rows is not a missing observation; this would be correct if the table were a log of readings rather than a table of turning points.

TRAP: Reading a table of turning points as though it were a continuous record,
and expecting a height for every clock time.

CONFIDENCE: high
"""

THIN_SLICE_FILENAME = "capability_thin_slice_bank.md"


def build_thin_slice(dest_dir):
    """Write the one thin-slice bank into `dest_dir` and return its absolute
    path. Writing it twice into the same directory, or into two directories,
    produces byte-identical content."""
    os.makedirs(dest_dir, exist_ok=True)
    path = os.path.join(os.path.abspath(dest_dir), THIN_SLICE_FILENAME)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(THIN_SLICE_BANK)
    return path


# The all-roles bank (plan 16A-03 Task 1): one document exercising every one
# of CAP-01's fourteen semantic teaching roles, so the catalog's completeness
# claim is checked against a render rather than against prose. Eleven callout
# kinds, a `## TERMS` registry with a `[[term]]` reference, a `[!CHECK:]` slot
# resolving to a real item, an item carrying the full authored hint ladder,
# and one `visual` item carrying an interaction contract.
ALL_ROLES_BANK = """# Reading a lock schedule (synthetic)

Fully invented teaching content for exercising every Phase 16A semantic
teaching role in one document. It is not derived from any real course, exam,
textbook, or navigation publication, and no real question bank belongs in
this repository.

[SEMANTIC-PROFILE: 1]
[LESSON-LANG: en]
[LESSON-DIR: ltr]

## TERMS

Lock chamber | The invented enclosed basin a vessel waits in while the water level is changed | Chamber
Lift | The invented height difference the chamber moves a vessel through

## LESSON

### Reading A Lock Schedule

> [!PREREQUISITE]
> You can read a clock time and subtract two clock times.

> [!EXAMPLE]
> The fictional Marrow Cut lock publishes a lift at 09:00 and the next at
> 09:40. A vessel arriving at 09:05 waits for the 09:40 lift.

A lock schedule lists the moments the [[lock chamber]] is committed to moving
water, not the moments a vessel may arrive. Every published time is a
departure of the chamber, and a vessel that misses one waits for the next.

> [!KEY] A schedule row is a chamber departure
> Each row names when the chamber moves, never when a vessel may arrive.

> [!NOTE]
> The published interval is nominal. Traffic and weather stretch it, and the
> posted list is not a promise.

> [!WARNING]
> A vessel that enters a chamber after the gates begin to close is in the one
> place on the cut where there is no room to turn around.

> [!MISCONCEPTION]
> Readers often treat the interval between two rows as a queue length. It is
> not: it is the time the chamber needs to fill, empty, and reset.

### Working A Lift Interval

> [!TIP]
> Subtract your arrival from the next published row before you do anything
> else. That one number decides every other choice on the approach.

> [!COUNTEREXAMPLE]
> A schedule listing 09:00 and 09:40 does not mean a vessel arriving at 09:20
> waits twenty minutes. It waits until 09:40, which is twenty minutes, only
> because the arrival happened to fall midway.

> [!EXCERPT]
> From the invented Marrow Cut standing orders, section 4: "The chamber
> departs on the published time or on the master's signal, whichever is
> later."

> [!UNCERTAINTY]
> The invented cut's operators disagree about whether a signalled departure
> resets the published interval or displaces one row. This fixture does not
> settle it.

> [!SUMMARY]
> Rows are chamber departures. Your wait is the gap between your arrival and
> the next row, and nothing else on the sheet changes that.

> [!CHECK: q1]

Q1. A lock schedule lists lifts at 09:00 and 09:40. A vessel arrives at 09:05. What does the schedule establish about its wait?   (difficulty: application)
[LESSON-REF: Reading A Lock Schedule]
[OBJECTIVE: nav:locks]

A) The chamber will depart at 09:05
B) The vessel waits until the 09:40 lift
C) The vessel is fifth in a queue of arrivals
D) No lift is scheduled after 09:05

CORRECT: B

WHY BEST: The published rows are chamber departures, so an arrival at 09:05
missed the 09:00 row and is held for the next published row at 09:40.

KEY DISCRIMINATOR: The answer must count from the arrival to the next
published row, not from the arrival to a queue position.

SECOND-BEST: A. The chamber does depart on a published time, and this would
be correct if 09:05 were itself a published row.

DISTRACTOR ANALYSIS:
- A) The rows are fixed departures rather than responses to arrivals; this would be correct if 09:05 appeared on the sheet.
- B) Correct: 09:05 falls after the 09:00 row, so the next committed departure is 09:40.
- C) A schedule records departures and not arrivals, so it cannot establish a queue position; this would be correct if the sheet were an arrivals log.
- D) The 09:40 row is later than 09:05; this would be correct if 09:00 were the final row of the day.

TRAP: Reading a departure schedule as an arrivals queue, and counting places
in line instead of counting to the next row.

CONFIDENCE: high

Q2. Two published lifts are 09:00 and 09:40. What is the nominal interval?   (difficulty: recall)
[LESSON-REF: Working A Lift Interval]
[OBJECTIVE: nav:locks.interval]

A) Twenty minutes
B) Forty minutes
C) Ninety minutes
D) It cannot be read from two rows

CORRECT: B

WHY BEST: The nominal interval is the difference between two consecutive
published rows, and 09:40 minus 09:00 is forty minutes.

KEY DISCRIMINATOR: The interval is the gap between rows, not the gap between
an arrival and a row.

SECOND-BEST: A. Twenty minutes is a real number on this sheet, and this would
be correct if the question asked for the wait of a vessel arriving at 09:20.

DISTRACTOR ANALYSIS:
- A) Twenty minutes is a possible wait rather than the interval; this would be correct if the question named an arrival at 09:20.
- B) Correct: consecutive rows forty minutes apart give a forty minute nominal interval.
- C) Ninety minutes appears nowhere on this sheet; this would be correct if the rows were 09:00 and 10:30.
- D) Two consecutive rows are exactly what an interval is read from; this would be correct if only one row were published.

TRAP: Reporting a particular vessel's wait as though it were the schedule's
interval.

CONFIDENCE: high

Q3. Mark the 09:40 lift on the timeline of the invented Marrow Cut morning.   (difficulty: application)
[OBJECTIVE: nav:locks.timeline]
[TYPE: visual]
[INTERACTION: numberline]
[VISUAL: {"version":1,"axis":{"min":"9","max":"11","step":"1/3"},"initial":{"points":[],"interval":null},"actions":["select_numberline_point"],"accessibility":{"description":"A number line of the invented morning from 9 to 11 marked in twenty minute steps, with one selectable point. Select the point at 9 and two thirds, which is 09:40."}}]
[SCORING: {"kind":"numberline_point","accepted":[{"value":"29/3"}],"tolerance":{"value":"0"},"partial_credit":false}]

WHY BEST: 09:40 is two thirds of the way from 9 to 10, the second twenty
minute tick after the start of the invented morning.

KEY DISCRIMINATOR: The tick two thirds past 9, not the tick one third past 9
and not the tick at 10.

SECOND-BEST: The tick at 10 is a published hour; it would be correct if the
prompt named the 10:00 lift.

DISTRACTOR ANALYSIS:
- The tick one third past 9 is 09:20; this would be correct if the item asked for a 09:20 lift.
- The tick at 10 is 10:00; this would be correct if the item asked for the 10:00 lift.

TRAP: Counting twenty minute ticks as half hours and landing on 09:30.

CONFIDENCE: high
"""

ALL_ROLES_FILENAME = "capability_all_roles_bank.md"


def build_all_roles(dest_dir):
    """Write the one all-roles bank into `dest_dir` and return its absolute
    path. Deterministic for `build_thin_slice`'s reason: the content is a
    module-level literal, so two builds produce byte-identical files."""
    os.makedirs(dest_dir, exist_ok=True)
    path = os.path.join(os.path.abspath(dest_dir), ALL_ROLES_FILENAME)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(ALL_ROLES_BANK)
    return path


# The unknown-semantics bank (plan 16A-03 Task 3): exactly one unknown
# OPTIONAL semantic and exactly one unknown REQUIRED semantic, plus one
# registered callout so the file reads as a realistic lesson rather than as a
# pathology. Both degradation paths must keep the author's own words.
UNKNOWN_SEMANTICS_BANK = """# Reading a fictional ferry board (synthetic)

Fully invented teaching content for exercising the Phase 16A
unknown-semantic contract. It is not derived from any real course, exam,
textbook, or transport publication, and no real question bank belongs in this
repository.

[SEMANTIC-PROFILE: 1]

## LESSON

### Reading A Ferry Board

> [!NOTE]
> The board lists sailings, not arrivals. A sailing that is called is not the
> same as a sailing that has left.

> [!WHATEVER]
> This block names a semantic role no reader knows about, and it is not
> marked required, so it degrades to an ordinary paragraph and says so in
> lint.

A ferry board is a promise about departures and nothing else. Reading it as a
statement about the boat currently at the ramp is the mistake that makes a
passenger miss the sailing they were watching.

> [!ALSOUNKNOWN!]
> This block names a semantic role no reader knows about and is marked
> required, so the reader refuses it out loud and prints this text unchanged.

Q1. A ferry board lists a sailing at 14:10. What does that row establish?   (difficulty: recall)
[LESSON-REF: Reading A Ferry Board]
[OBJECTIVE: nav:ferry]

A) The boat now at the ramp leaves at 14:10
B) A sailing is scheduled to depart at 14:10
C) A boat arrives at 14:10
D) Boarding closes at 14:10

CORRECT: B

WHY BEST: A board row is a scheduled departure, so the only thing the row
establishes is that a sailing is scheduled for that time.

KEY DISCRIMINATOR: The answer must describe a scheduled departure rather than
the state of any particular vessel.

SECOND-BEST: A. A boat at the ramp often is the 14:10 sailing, and this would
be correct if the board named vessels rather than sailings.

DISTRACTOR ANALYSIS:
- A) The board names sailings and not vessels; this would be correct if each row carried a boat name.
- B) Correct: a row is a scheduled departure time and nothing more.
- C) Arrivals are a different board; this would be correct if the question named the arrivals board.
- D) Boarding times are not published on this invented board; this would be correct if a boarding column existed.

TRAP: Treating the boat visible at the ramp as the boat named by the next
row.

CONFIDENCE: high
"""

UNKNOWN_SEMANTICS_FILENAME = "capability_unknown_semantics_bank.md"


def build_unknown_semantics(dest_dir):
    """Write the one unknown-semantics bank into `dest_dir` and return its
    absolute path. Deterministic for `build_thin_slice`'s reason."""
    os.makedirs(dest_dir, exist_ok=True)
    path = os.path.join(os.path.abspath(dest_dir), UNKNOWN_SEMANTICS_FILENAME)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(UNKNOWN_SEMANTICS_BANK)
    return path


# The example-order bank (plan 16A-03 Task 3). Two headings: the first places
# a [!KEY] definition before its worked example and is the offending one; the
# second places its example first and must produce no finding, which is what
# makes the check per-heading rather than per-lesson.
_DEFINITION_FIRST_HEAD = """# Reading a fictional bridge lift board (synthetic)

Fully invented teaching content for exercising the Phase 16A
worked-example-first default. It is not derived from any real course, exam,
textbook, or navigation publication, and no real question bank belongs in
this repository.

[SEMANTIC-PROFILE: 1]
"""

_DEFINITION_FIRST_BODY = """
## LESSON

### Defining The Lift Window

> [!KEY] A lift window is a committed opening
> The bridge is committed to opening at the published time and is committed
> to nothing else.

> [!EXAMPLE]
> The invented Harrow Bridge publishes lifts at 07:00 and 07:30. A vessel
> arriving at 07:05 waits for 07:30.

### Showing The Lift Window

> [!EXAMPLE]
> The same invented board at 11:00 and 11:30 holds a vessel arriving at 11:05
> until 11:30, for exactly the same reason.

> [!KEY] The window is read from two rows
> Two consecutive published rows are what a window is measured between.

Q1. A bridge board publishes lifts at 07:00 and 07:30. A vessel arrives at 07:05. When does it pass?   (difficulty: application)
[LESSON-REF: Defining The Lift Window]
[OBJECTIVE: nav:bridges]

A) 07:05
B) 07:30
C) 08:00
D) It cannot be determined

CORRECT: B

WHY BEST: The published rows are committed openings, so an arrival at 07:05
is held until the next committed opening at 07:30.

KEY DISCRIMINATOR: The answer must be a published row later than the arrival.

SECOND-BEST: A. The vessel is present at 07:05, and this would be correct if
07:05 were itself a published row.

DISTRACTOR ANALYSIS:
- A) The bridge opens on published times and not on arrivals; this would be correct if 07:05 appeared on the board.
- B) Correct: 07:30 is the first published row after the arrival.
- C) 08:00 appears nowhere on this board; this would be correct if the rows were hourly from 08:00.
- D) Two published rows are enough to answer; this would be correct if no row followed the arrival.

TRAP: Reading a committed opening board as though the bridge responds to
arrivals.

CONFIDENCE: high

Q2. What are two consecutive published rows used to measure?   (difficulty: recall)
[LESSON-REF: Showing The Lift Window]
[OBJECTIVE: nav:bridges.window]

A) The lift window
B) The number of waiting vessels
C) The height of the bridge
D) The time a vessel arrived

CORRECT: A

WHY BEST: The window is the interval between two consecutive committed
openings, which is exactly what two rows give.

KEY DISCRIMINATOR: The measurement is between two rows, not between a row and
anything a vessel does.

SECOND-BEST: D. Arrival time is what a window is compared against, and this
would be correct if the question asked what the window is used to decide.

DISTRACTOR ANALYSIS:
- A) Correct: two consecutive rows are the endpoints of one window.
- B) The board records openings and not vessels; this would be correct if it were a traffic log.
- C) Height is a chart datum figure; this would be correct if the question named the air draft table.
- D) An arrival is not published on the board; this would be correct if the question asked what a window is compared against.

TRAP: Reading the board as a record of traffic rather than of openings.

CONFIDENCE: high
"""

_EXAMPLE_ORDER_DIRECTIVES = {
    None: "",
    "with_reason": ("[EXAMPLE-ORDER: definition-first because the formal "
                    "definition is the invented course's own wording]\n"),
    "no_reason": "[EXAMPLE-ORDER: definition-first]\n",
}

DEFINITION_FIRST_FILENAMES = {
    None: "capability_definition_first_bank.md",
    "with_reason": "capability_definition_first_reason_bank.md",
    "no_reason": "capability_definition_first_no_reason_bank.md",
}


def build_definition_first(dest_dir, override=None):
    """Write the example-order bank into `dest_dir` and return its absolute
    path.

    `override` selects the `[EXAMPLE-ORDER:]` directive: `None` writes none,
    `"with_reason"` writes a reasoned override, and `"no_reason"` writes the
    override CAP-01 refuses to honor. Each value writes its own filename, so
    all three can live in one directory and be linted independently.
    """
    if override not in _EXAMPLE_ORDER_DIRECTIVES:
        raise ValueError("unknown override %r; expected one of %s"
                         % (override,
                            ", ".join(repr(k) for k
                                      in _EXAMPLE_ORDER_DIRECTIVES)))
    os.makedirs(dest_dir, exist_ok=True)
    path = os.path.join(os.path.abspath(dest_dir),
                        DEFINITION_FIRST_FILENAMES[override])
    text = (_DEFINITION_FIRST_HEAD + _EXAMPLE_ORDER_DIRECTIVES[override]
            + _DEFINITION_FIRST_BODY)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    return path


# The unavailable-capability bank (plan 16A-04 Task 3): one lesson carrying a
# `[!CHECK:]` slot resolving to a real item in the same bank, so a gate-less
# render exercises CAP-02's static instructional path against real shipped
# code rather than against a stub.
UNAVAILABLE_CAPABILITY_BANK = """# Reading a fictional siding diagram (synthetic)

Fully invented teaching content for exercising CAP-02's static instructional
path. It is not derived from any real course, exam, textbook, or railway
publication, and no real question bank belongs in this repository.

[SEMANTIC-PROFILE: 1]

## LESSON

### Reading A Siding Diagram

> [!EXAMPLE]
> The invented Harrow Loop diagram draws the siding as a stub off the running
> line, with the points shown lying for the running line.

A siding diagram draws where a vehicle may be put, never where one is. The
points symbol says which way the blades lie in the drawing, and a drawing is
not a report about this morning.

> [!NOTE]
> The diagram is a plan of the layout. It is not a live indication and it
> never was.

> [!CHECK: q1]

Q1. A siding diagram shows the points lying for the running line. What does that establish about the layout right now?   (difficulty: application)
[LESSON-REF: Reading A Siding Diagram]
[OBJECTIVE: rail:siding.diagram]

A) The points are lying for the running line right now
B) The diagram records the normal position of the points
C) A vehicle is standing in the siding
D) The siding is out of use

CORRECT: B

WHY BEST: A diagram records the layout and the normal position of its points,
so the only thing it establishes is what normal means here.

KEY DISCRIMINATOR: The answer must describe the drawing's record of a normal
position rather than a live state.

SECOND-BEST: A. The points often do lie as drawn, and this would be correct
if the diagram were a live indication panel.

DISTRACTOR ANALYSIS:
- A) A plan is not an indication; this would be correct if the question named a live panel.
- B) Correct: a diagram records the layout and the normal position of its points.
- C) Vehicles are not drawn on a layout plan; this would be correct if the drawing were an occupancy chart.
- D) Out of use is a separate notice; this would be correct if the diagram carried a possession marking.

TRAP: Reading a layout plan as a live indication of where the blades are
lying this minute.

CONFIDENCE: high
"""

UNAVAILABLE_CAPABILITY_FILENAME = "capability_unavailable_bank.md"


def build_unavailable_capability(dest_dir):
    """Write the one unavailable-capability bank into `dest_dir` and return
    its absolute path. Deterministic for `build_thin_slice`'s reason."""
    os.makedirs(dest_dir, exist_ok=True)
    path = os.path.join(os.path.abspath(dest_dir),
                        UNAVAILABLE_CAPABILITY_FILENAME)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(UNAVAILABLE_CAPABILITY_BANK)
    return path


# A lesson with no callout of any kind (plan 16A-04 Task 3 step 5). CAP-02's
# no-decorative-block clause is only checkable against a document that uses
# none: a style system that required a decorative block would fire here.
NO_CALLOUTS_BANK = """# Reading a fictional gauge board (synthetic)

Fully invented teaching content carrying no callout of any kind, so CAP-02's
no-decorative-block clause is checkable rather than aspirational. It is not
derived from any real course, exam, textbook, or engineering publication, and
no real question bank belongs in this repository.

## LESSON

### Reading A Gauge Board

A gauge board pairs a reading with the moment it was taken. Neither number
means anything without the other, and a board that has lost its timestamps is
a list of numbers rather than a record.

The reading is what the instrument said. It is not what the quantity was, and
the difference between those two is the whole of instrument work.

Q1. A gauge board pairs a reading with a time. What does one pair establish?   (difficulty: recall)
[LESSON-REF: Reading A Gauge Board]
[OBJECTIVE: eng:gauge.pairs]

A) What the instrument said at that moment
B) What the quantity was at that moment
C) What the quantity will be next
D) Whether the instrument is accurate

CORRECT: A

WHY BEST: A pair records an instrument reading and the moment it was taken,
which is a statement about the instrument and not about the quantity.

KEY DISCRIMINATOR: The answer must stay with what the instrument said rather
than with what was true.

SECOND-BEST: B. A calibrated instrument reading is usually close to the
quantity, and this would be correct if the board recorded corrected values.

DISTRACTOR ANALYSIS:
- A) Correct: a pair is a reading and the moment it was taken.
- B) The quantity and the reading differ by the instrument's error; this would be correct if the board recorded corrected values.
- C) A board is a record and not a forecast; this would be correct if the question named a trend line.
- D) Accuracy is established by calibration and not by a single pair; this would be correct if the question named a calibration certificate.

TRAP: Treating a raw reading as the quantity itself and dropping the
instrument from the account.

CONFIDENCE: high
"""

NO_CALLOUTS_FILENAME = "capability_no_callouts_bank.md"


def build_no_callouts(dest_dir):
    """Write the one callout-free bank into `dest_dir` and return its
    absolute path. Deterministic for `build_thin_slice`'s reason."""
    os.makedirs(dest_dir, exist_ok=True)
    path = os.path.join(os.path.abspath(dest_dir), NO_CALLOUTS_FILENAME)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(NO_CALLOUTS_BANK)
    return path


# The media lesson (plan 16A-05 Task 3): one bank exercising all four states
# `_media_figure_html` handles, plus the two lint findings the states cannot
# produce on their own.
#
# The placeholder asset is a synthetic 67-byte one-pixel greyscale PNG written
# from the literal byte string below. It is not a photograph, not a diagram,
# and not derived from anything: it exists so the `present` state has real
# bytes on disk to point at without a real image entering this repository.
PLACEHOLDER_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00"
    b"\x00\x01\x08\x00\x00\x00\x00:~\x9bU\x00\x00\x00\nIDATx\x9cch"
    b"\x00\x00\x00\x82\x00\x81w\xcdr\xb6\x00\x00\x00\x00IEND\xaeB`\x82")

PLACEHOLDER_PNG_FILENAME = "capability_tide_chart_placeholder.png"

MEDIA_BANK = """# Reading a fictional tide chart (synthetic)

Fully invented teaching content for exercising the Phase 16A media grammar.
Every asset row below is fictional: the station, the photographer, the host,
and the derivation are invented, and nothing here is derived from any real
course, exam, textbook, photograph, or chart.

[SEMANTIC-PROFILE: 1]

## MEDIA

tide-chart | capability_tide_chart_placeholder.png | Chart by the invented Kestrel Point survey, fictional | A one pixel placeholder standing in for a tide chart whose curve rises from a low water at 04:12 to a high water at 10:38. | granted | Redrawn from the invented survey's own plotted figures, no tracing. | present | sha256:0000000000000000000000000000000000000000000000000000000000000000
harbour-photo | capability_harbour_photo.jpg | Photograph by the invented Ilse Marrow, fictional | A harbour wall at low water with the tide gauge board visible, its lowest painted mark standing clear of the water. | unknown | Original photograph, no derivation. | missing | sha256:1111111111111111111111111111111111111111111111111111111111111111
remote-diagram | https://example.invalid/fictional/lock-diagram.svg | Diagram by the invented Harrow Cut trust, fictional | A schematic of a lock chamber with its upper and lower gates and the sluice paths between them. | denied | Traced from the invented trust's published schematic. | remote | sha256:2222222222222222222222222222222222222222222222222222222222222222
no-alt-asset | capability_no_alt.png |  |  | granted | Invented placeholder with no alternative on purpose. | present | sha256:3333333333333333333333333333333333333333333333333333333333333333

## LESSON

### Reading A Tide Chart

A tide chart draws the curve a table only samples. The turning points are the
same in both; what the chart adds is the shape between them.

[MEDIA: tide-chart]

The gauge board on the wall is the same measurement taken by eye, and a photo
of one is a reading rather than a record.

[MEDIA: harbour-photo]

### Reading A Lock Diagram

A lock diagram is a schematic, so it draws relationships and not distances.
The gates and the sluice paths are what it is for.

[MEDIA: remote-diagram]

[MEDIA: no-alt-asset]

[MEDIA: ghost]

Q1. A tide chart draws a curve between two turning points. What does the curve between them establish?   (difficulty: application)
[LESSON-REF: Reading A Tide Chart]
[OBJECTIVE: nav:tides.chart]

A) The exact height at every clock time
B) The shape of the water's travel between two turning points
C) The times of the turning points only
D) Nothing that a table does not already say

CORRECT: B

WHY BEST: The turning points are the same in a chart and a table; the curve
between them is the one thing the chart adds.

KEY DISCRIMINATOR: The answer must name what the curve adds over the table
rather than what both already carry.

SECOND-BEST: A. The curve does give a height for any time, and this would be
correct if the chart were an exact record rather than a drawn interpolation.

DISTRACTOR ANALYSIS:
- A) A drawn curve is an interpolation and not an exact record; this would be correct if the chart plotted measured readings at every minute.
- B) Correct: the shape between the turning points is what a chart adds to a table.
- C) Turning point times are what a table already gives; this would be correct if the question asked what the two share.
- D) The curve is more than the table carries; this would be correct if the chart plotted only the turning points.

TRAP: Reading a drawn interpolation as a measured record.

CONFIDENCE: high
"""

MEDIA_FILENAME = "capability_media_bank.md"


def build_media_lesson(dest_dir):
    """Write the media bank plus its one synthetic placeholder asset into
    `dest_dir` and return the bank's absolute path.

    Two files, not one: the `present` state needs real bytes on disk to point
    at, and pointing at a file that is not there would make `present` and
    `missing` render the same thing and prove nothing.
    """
    os.makedirs(dest_dir, exist_ok=True)
    root = os.path.abspath(dest_dir)
    with open(os.path.join(root, PLACEHOLDER_PNG_FILENAME), "wb") as fh:
        fh.write(PLACEHOLDER_PNG)
    path = os.path.join(root, MEDIA_FILENAME)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(MEDIA_BANK)
    return path


# The ten-purpose activity set (plan 16A-06 Task 3). Eleven items, eleven
# declarations: ten covering the ten ACTIVITY_PURPOSES exactly once, each
# paired with a response form research stream 03 section 4.1 names as suitable
# for that purpose, and an eleventh declaring a form outside RESPONSE_FORMS so
# ACTIVITY-01's Degraded clause has something real to fall back from.
#
# All eight shipped response forms appear. That is the demonstration
# ACTIVITY-01 asks for: ten purposes served by the forms that already exist,
# with no ninth type minted for any of them.
ACTIVITY_SET_ORDER = ("q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9",
                      "q10", "q11")

UNSUPPORTED_ACTIVITY_ITEM = "q11"
UNSUPPORTED_ACTIVITY_FORM = "oral_explanation"
UNSUPPORTED_ACTIVITY_FALLBACK = (
    "Say your answer out loud, then compare it to the worked explanation "
    "below.")

ACTIVITY_SET_BANK = '# The invented Kestrel Point pilotage course (synthetic)\n\nFully invented teaching content for exercising the Phase 16A activity\ndeclaration grammar. Every item, objective, station, and rule below is\ninvented, and nothing here is derived from any real course, exam, textbook, or\npilotage publication.\n\n[SEMANTIC-PROFILE: 1]\n\n## ACTIVITIES\n\nq1 | prediction | anticipate what the chart will show before reading it | nav:tides.predict | The invented Kestrel Point tide table for a single morning | mc | none | after_commitment | activity_trace | The prediction is a labelled radio group in document order with a visible legend, answerable by keyboard alone. | Write down which way you think the water is moving at 07:00, then read the table and compare.\nq2 | noticing | discriminate one marked feature from its neighbours | nav:charts.notice | An invented number line of the morning marked in twenty minute steps | visual | unlimited | immediate | activity_trace | The scene carries a required text description naming every tick and the task, so the item is answerable without seeing or dragging anything. | Read the description of the marked line and name the tick the question asks for.\nq3 | retrieval | recall a stated definition without the source in view | nav:tides.recall | No stimulus; the learner works from memory | short | none | after_commitment | pending_human_mark | The response is a labelled text area reachable in document order, with no time limit and no pointer requirement. | Say the definition out loud from memory, then check it against the glossary entry.\nq4 | explanation | justify why one reading follows from another | nav:tides.explain | The same invented morning table, still in view | short | none | after_commitment | pending_human_mark | The response is a labelled text area reachable in document order; the stimulus stays on the page beside it. | Write out the reason in full sentences, then compare it to the worked explanation.\nq5 | comparison | weigh two records against a stated criterion | nav:records.compare | Two invented record types, a table and a chart | table | unlimited | immediate | scored_by_runtime | Each row is a labelled control in a real table with row and column headers, operable by keyboard. | Sort the listed statements into the two record types on paper, then check the key.\nq6 | diagnosis | locate the fault in a failing routine | cs:debug.locate | An invented four line routine that misreads its input | check | until_correct | immediate | scored_by_runtime | The editor is a labelled text area; every case result is announced as text and never by color alone. | Read the routine line by line and write down which line is wrong before running anything.\nq7 | practice | apply a stated procedure end to end | nav:locks.practice | An invented lock approach with four published steps | build | unlimited | staged | scored_by_runtime | The steps are a labelled list, reorderable by keyboard with a visible current position. | Write the four steps in order on paper, then compare with the key below.\nq8 | transfer | select the right model in a changed context | nav:models.transfer | Three invented situations the learner has not met in this order | dnd | unlimited | after_commitment | scored_by_runtime | Every item and every bucket is a labelled control with a keyboard path; no drag is required. | Decide which model each situation needs, write the pairs down, then check them.\nq9 | reflection | monitor and name your own uncertainty | study:reflection | The learner\'s own work so far, nothing else | short | unlimited | non_evaluative | not_recorded | The response is a labelled text area reachable in document order; nothing is scored and nothing is announced as right or wrong. | Write one sentence naming the part you are least sure of and why.\nq10 | formal_assessment | whatever the sourced construct requires | nav:tides.assess | The invented blueprint\'s own stem set | multi | none | withheld_until_submit | scored_by_runtime | Every option is a labelled checkbox in document order with the required count stated in text. | Answer the printed version of the item set under the same conditions.\nq11 | explanation | explain a reading out loud to another person | nav:tides.oral | The same invented morning table | oral_explanation | unlimited | non_evaluative | not_recorded | The prompt is plain text in document order and the fallback needs no audio device. | Say your answer out loud, then compare it to the worked explanation below.\n\n## LESSON\n\n### Working The Invented Morning\n\nThe invented Kestrel Point table lists a high water at 04:12 and a low water\nat 10:38. Every activity in this bank works from that one morning.\n\n> [!CHECK: q11]\n\nQ1. Before reading the table, which way do you expect the water to be moving at 07:00?   (difficulty: application)\n[LESSON-REF: Working The Invented Morning]\n[OBJECTIVE: nav:tides.predict]\n\nA) Rising toward a high water\nB) Falling toward a low water\nC) Standing still\nD) Not enough is known to expect either\n\nCORRECT: B\n\nWHY BEST: The listed high water is at 04:12 and the next listed low water is at 10:38, so 07:00 sits on the falling side of that pair.\n\nKEY DISCRIMINATOR: The expectation must follow from which two turning points the time falls between.\n\nSECOND-BEST: A. The water does rise toward a high water, and this would be correct if 07:00 fell before 04:12 rather than after it.\n\nDISTRACTOR ANALYSIS:\n- A) Rising is the travel before a high water; this would be correct if the time fell before 04:12.\n- B) Correct: 07:00 falls between a high water and the following low water.\n- C) Standing water happens only at a turning point; this would be correct if the question named 04:12 or 10:38.\n- D) Two published turning points are enough to expect a direction; this would be correct if only one row were published.\n\nTRAP: Treating a prediction as unanswerable because the table gives no height for 07:00.\n\nCONFIDENCE: high\n\nQ2. Select the point at 9 and two thirds on the invented morning line.   (difficulty: recall)\n[OBJECTIVE: nav:charts.notice]\n[TYPE: visual]\n[INTERACTION: numberline]\n[VISUAL: {"version":1,"axis":{"min":"9","max":"11","step":"1/3"},"initial":{"points":[],"interval":null},"actions":["select_numberline_point"],"accessibility":{"description":"A number line of the invented morning from 9 to 11 marked in twenty minute steps, with one selectable point. Select the point at 9 and two thirds."}}]\n[SCORING: {"kind":"numberline_point","accepted":[{"value":"29/3"}],"tolerance":{"value":"0"},"partial_credit":false}]\n\nWHY BEST: Nine and two thirds is the second twenty minute tick after the start of the invented morning.\n\nKEY DISCRIMINATOR: The tick two thirds past 9, not the tick one third past 9 and not the tick at 10.\n\nSECOND-BEST: The tick at 10 is a whole hour; it would be correct if the prompt named 10 rather than 9 and two thirds.\n\nDISTRACTOR ANALYSIS:\n- The tick one third past 9 is the first twenty minute tick; this would be correct if the item asked for 9 and one third.\n- The tick at 10 is a whole hour; this would be correct if the item asked for 10.\n\nTRAP: Counting twenty minute ticks as half hours and landing halfway.\n\nCONFIDENCE: high\n\nQ3. From memory, state what a turning point on a tide table is.   (difficulty: recall)\n[OBJECTIVE: nav:tides.recall]\n[TYPE: short]\nMODEL: A turning point is a listed moment when the water stops rising or stops falling and reverses, which is why a row fixes a height only at that instant.\nRUBRIC:\n- names the reversal of direction\n- states that the row fixes a height at that moment only\n\nTRAP: Describing a turning point as the highest point of the day, which is true of only one of them.\n\nCONFIDENCE: high\n\nQ4. Explain why the table says nothing about the water at 07:00.   (difficulty: analysis)\n[LESSON-REF: Working The Invented Morning]\n[OBJECTIVE: nav:tides.explain]\n[TYPE: short]\nMODEL: The rows are turning points rather than samples, so the table fixes heights only at 04:12 and 10:38 and leaves the interval between them undescribed.\nRUBRIC:\n- states that the rows are turning points and not samples\n- states that the interval between two rows carries no listed height\n\nTRAP: Explaining the answer by saying the reading was not taken, which treats the table as a log.\n\nCONFIDENCE: high\n\nQ5. Sort each statement into the record type it describes.   (difficulty: application)\n[OBJECTIVE: nav:records.compare]\n[TYPE: table]\n[CATEGORIES: Table | Chart]\nROW) Lists a height only at its own listed moments :: Table\nROW) Draws a continuous curve between turning points :: Chart\nROW) Cannot be read at an unlisted clock time :: Table\nROW) Gives an interpolated height at any clock time :: Chart\n\nWHY BEST: A table fixes heights at its own listed moments and a chart draws through the times between them, so continuity belongs to the chart and unlisted times belong to the table.\n\nKEY DISCRIMINATOR: Whether the statement is about listed moments or about the span between them.\n\nDISTRACTOR ANALYSIS:\n- A chart is an interpolation and a table is a set of samples; a statement about continuity belongs to the chart.\n- A statement about what cannot be read at an unlisted time belongs to the table, because the chart draws through those times.\n\nTRAP: Treating a drawn curve as though it were measured, and sorting continuity into the table.\n\nCONFIDENCE: high\n\nQ6. Fix the routine so it totals every number on the input line rather than only the first.   (difficulty: application)\n[OBJECTIVE: cs:debug.locate]\n[TYPE: check]\n[LANG: python]\n[MATCH: trimmed]\nCASE) 5 7 :: 12\nCASE) 3 4 9 :: 16\nSTARTER:\nimport sys\n\nnums = [int(x) for x in sys.stdin.read().split()]\nprint(sum(nums))\n\nTRAP: Reading only the first token and reporting it as the total.\n\nCONFIDENCE: high\n\nQ7. Put the four published steps of the invented lock approach in order.   (difficulty: application)\n[OBJECTIVE: nav:locks.practice]\n[TYPE: build]\nSTEP) Read the next published lift from the board\nSTEP) Compute the wait from your own arrival\nSTEP) Call the lock keeper on the published channel\nSTEP) Enter the chamber when the gates are signalled open\n\nWHY BEST: Each step supplies what the next one needs: the board gives the lift, the lift gives the wait, the wait decides the call, and only the signal opens the chamber.\n\nKEY DISCRIMINATOR: Entry follows the signal rather than the published time.\n\nDISTRACTOR ANALYSIS:\n- The wait cannot be computed before the next published lift is read, so reading the board comes first.\n- The call is made once the wait is known, and entering follows the signal rather than the clock.\n\nTRAP: Entering on the published time rather than on the signal.\n\nCONFIDENCE: high\n\nQ8. Sort each unfamiliar situation into the model it needs.   (difficulty: analysis)\n[OBJECTIVE: nav:models.transfer]\n[TYPE: dnd]\n[CATEGORIES: Turning point model | Interval model]\nITEM) A vessel asking what the water is doing right now :: Interval model\nITEM) A vessel asking when the water next reverses :: Turning point model\nITEM) A vessel asking how long it must wait :: Interval model\n\nWHY BEST: A question about a reversal is answered by a listed row, and a question about now or about a wait is answered by the span between two rows.\n\nKEY DISCRIMINATOR: Whether the question asks about a listed moment or about the span between two of them.\n\nDISTRACTOR ANALYSIS:\n- A question about a reversal is answered by a listed turning point, not by the interval between two of them.\n- A question about right now or about a wait is answered by the interval, because both are about the span between rows.\n\nTRAP: Reaching for a listed row whenever a clock time appears in the question.\n\nCONFIDENCE: high\n\nQ9. Name the part of this morning\'s work you are least sure of, and why.   (difficulty: recall)\n[OBJECTIVE: study:reflection]\n[TYPE: short]\nMODEL: Any honest, specific statement naming one part of the work and one reason for the uncertainty. There is no correct content here.\nRUBRIC:\n- names one specific part of the work rather than the whole\n- gives a reason rather than a feeling alone\n\nTRAP: Naming the whole topic instead of one part, which gives the learner nothing to act on.\n\nCONFIDENCE: high\n\nQ10. Select the three statements the invented blueprint treats as established by a two row table.   (difficulty: analysis)\n[OBJECTIVE: nav:tides.assess]\n[TYPE: multi]\n[SELECT: 3]\n\nA) The moments of two turning points\nB) The direction of travel between them\nC) The height at each listed moment\nD) The height at every clock time\nE) The number of vessels waiting\nF) The time the next vessel arrives\n\nCORRECT: A, B, C\n\nWHY BEST: Two rows fix their own moments and their own heights, and two consecutive turning points fix the direction of travel between them; nothing else on the list follows from a two row table.\n\nKEY DISCRIMINATOR: Each keyed statement must follow from the two rows alone, with no interpolation and no traffic information.\n\nSECOND-BEST: D. A chart does give a height at every clock time, and this would be correct if the stimulus were a chart rather than a table.\n\nDISTRACTOR ANALYSIS:\n- A) Correct: the rows are turning points and their moments are listed.\n- B) Correct: two consecutive turning points fix the direction of travel between them.\n- C) Correct: each row fixes a height at its own moment.\n- D) A table gives no height between rows; this would be correct if the stimulus were a chart.\n- E) Vessels are not on a tide table; this would be correct if the stimulus were a traffic log.\n- F) Arrivals are not on a tide table; this would be correct if the stimulus were an arrivals board.\n\nTRAP: Reading a two row table as though it established a height at every clock time.\n\nCONFIDENCE: high\n\nQ11. Explain the morning\'s tide to another person out loud, then write what you said.   (difficulty: analysis)\n[LESSON-REF: Working The Invented Morning]\n[OBJECTIVE: nav:tides.oral]\n[TYPE: short]\nMODEL: Any spoken account that names the two turning points, states the direction between them, and says the table fixes no height in between.\nRUBRIC:\n- names both turning points\n- states what the table does not establish between them\n\nTRAP: Describing the shape of the water without saying what the table itself establishes.\n\nCONFIDENCE: high\n'

ACTIVITY_SET_FILENAME = "capability_activity_set_bank.md"


def build_activity_set(dest_dir):
    """Write the one activity-set bank into `dest_dir` and return its
    absolute path. Deterministic for `build_thin_slice`'s reason."""
    os.makedirs(dest_dir, exist_ok=True)
    path = os.path.join(os.path.abspath(dest_dir), ACTIVITY_SET_FILENAME)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(ACTIVITY_SET_BANK)
    return path


# The output-mode lesson (plan 16A-07 Task 2): four registered terms and
# three headings, every one a distinct fictional string, so the derivation
# assertion in `scenario_output_modes` has something to find rather than
# matching by accident on a common word.
OUTPUT_MODE_BANK = '# The invented Marrow Cut signalling primer (synthetic)\n\nFully invented teaching content for exercising the Phase 16A output-mode\ncomposers. Every term, station, and rule below is invented, and nothing here\nis derived from any real course, exam, textbook, or signalling publication.\n\n[SEMANTIC-PROFILE: 1]\n\n## TERMS\n\nAbsolute block | The invented rule that only one vessel occupies a marked reach of the cut at a time | Block\nFixed distant | The invented board that repeats what the next board will say, and never says anything itself\nOccupation key | The invented brass token a master carries while their vessel holds a reach\nRunning release | The invented signal that a reach has been given up without the token being returned\n\n## LESSON\n\n### The Absolute Block Rule\n\nThe invented Marrow Cut works on an [[absolute block]]: a reach belongs to one\nvessel from the moment it is entered until the moment it is given up. Nothing\nabout the rule depends on how fast a vessel moves, only on whether a reach is\nheld.\n\n### Reading The Fixed Distant\n\nA [[fixed distant]] board is a repeater. It carries no authority of its own,\nwhich is the single most misread thing on the cut, and a master who treats it\nas an instruction has read a copy as though it were the original.\n\n### Holding And Giving Up A Reach\n\nAn [[occupation key]] is the physical record that a reach is held. A\n[[running release]] gives the reach up without the key coming back, which is\nthe one case where the physical record and the state of the cut disagree.\n\nQ1. A fixed distant board on the invented cut shows a caution. What does that establish?   (difficulty: application)\n[LESSON-REF: Reading The Fixed Distant]\n[OBJECTIVE: rail:signals.distant]\n\nA) The next board will show a caution or worse\nB) The vessel must stop at this board\nC) The reach ahead is occupied by two vessels\nD) The board has failed and shows its default\n\nCORRECT: A\n\nWHY BEST: A fixed distant repeats what the next board will say and carries no\nauthority of its own, so a caution on it is a statement about the next board.\n\nKEY DISCRIMINATOR: The answer must be about the next board rather than about\nthis one.\n\nSECOND-BEST: B. A caution does require slowing, and this would be correct if\nthe board carried authority of its own rather than repeating.\n\nDISTRACTOR ANALYSIS:\n- A) Correct: the distant repeats the next board and says nothing itself.\n- B) A distant never commands a stop; this would be correct if it were the next board rather than its repeater.\n- C) The number of vessels in a reach is not on any board; this would be correct if the cut published occupancy counts.\n- D) A caution is a real indication and not a failure default; this would be correct if the board were dark.\n\nTRAP: Reading a repeater as an instruction, which turns a copy into an\noriginal.\n\nCONFIDENCE: high\n'

OUTPUT_MODE_FILENAME = "capability_output_mode_bank.md"


def build_output_mode_lesson(dest_dir):
    """Write the one output-mode bank into `dest_dir` and return its absolute
    path. Deterministic for `build_thin_slice`'s reason."""
    os.makedirs(dest_dir, exist_ok=True)
    path = os.path.join(os.path.abspath(dest_dir), OUTPUT_MODE_FILENAME)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(OUTPUT_MODE_BANK)
    return path
