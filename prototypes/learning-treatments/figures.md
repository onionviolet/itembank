# Figure and table question treatment

**Status:** prototype only. Review required. This is original synthetic source
material and a proposed authoring treatment. It is not a bank, a score, a
source binding, or an accepted revision.

## Exact source locator

`figures.md#source-figure-2`, Figure 2, and `figures.md#source-table-1`,
Table 1, rows 1 through 4.

**Source identity:** original synthetic specimen created for this prototype.
There is no book source, external URL, source binding, or rights grant to
infer.

<a id="source-figure-2"></a>

## Original source figure

**Figure 2. Water moving through a local landscape**

```text
             [Condensation]
                   cloud
                     |
                     | [Precipitation]
     [Evaporation]   v
 lake  ^              hill ---- [Runoff] ----> stream ----> lake
       |
```

The figure names four movements of water in the illustrated watershed:
evaporation rises from the lake, condensation names cloud formation,
precipitation falls from the cloud, and runoff moves across land toward the
stream and lake.

<a id="source-table-1"></a>

## Original source table

**Table 1. Synthetic rainfall measurements**

| Day | Gauge A | Gauge B | Collection interval |
| --- | ---: | ---: | --- |
| Monday | 12 mm | 18 mm | 24 hours |
| Tuesday | 5 mm | 5 mm | 24 hours |
| Wednesday | 0 mm | 7 mm | 24 hours |
| Thursday | 9 mm | 4 mm | 24 hours |

## Author interpretation, pending review

The figure can support identifying a named process from its visual context and
locating a label at its intended arrow. The table can support a comparison when
collection intervals match. Those are proposed constructs, not accepted
objectives or proof that any response format is appropriate.

## Current studio workflow, revised 2026-09-11

Choose the figure or rainfall table. Select source labels or cells to replace
in the preview. Write an instruction and purpose, then try the resulting text
fields or label placements. Review draft shows that exact selection and wording
as a treatment sketch. For diagram placement, Create bank draft turns that
selection into an existing `dnd` item for author review and download.

The downloaded Markdown keeps all four supplied labels. Selected locations
retain their source numbers. Extra labels go in an explicit Not used
destination. The proposed key comes from the synthetic source, never from
trial answers. The file includes the original source specimen, exact locator,
static practice description, and exact author text in JSON metadata. Ordinary
instruction line breaks become spaces in the question with a visible notice.
Structural question or field markup in instructions produces a visible error.
The per-download file remains a draft until checked through the runtime.

The diagram now starts in drag-and-drop mode. Its word bank stays visible.
Each label can occupy one selected location, and moving it clears the previous
location. Click selection and dropdowns provide the same placement choices.
Typed diagram answers have an optional word bank. Table blanks have an optional
value bank. Each source retains its bank preference and typed responses when
the bank is hidden or shown. Banks start visible and list options independently
of their source order.

Each source retains its instruction, purpose, selection, and trial responses in
page memory. Text responses and placement responses remain separate. The
original-source dialog preserves the active draft and returns keyboard focus on
close. Raw Markdown opens separately. Reload or Reset discards the edits.

### Static preview of the default selection

**Instruction:** Name the water processes at the marked locations.

```text
             [Condensation]
                   cloud
                     |
                     | [3]
          [1]        v
 lake  ^              hill ---- [Runoff] ----> stream ----> lake
       |
```

1. Arrow rising from the lake: ____________________
3. Arrow falling from cloud to land: ____________________

For the placement version, choose a process label for each numbered location.
The labels are Evaporation, Condensation, Precipitation, and Runoff. These are
ungraded preview responses. The original source remains above for inspection.

The default table selection replaces Monday's Gauge B value with a blank and
retains Monday, Gauge A = 12 mm, and the 24-hour interval. The response is text
in millimeters. This treatment tests recall of a selected value, not an inferred
calculation. A different construct requires different author wording and review.

## First-pass treatment proposals, retained for comparison

### Figure fill blank

**Candidate composition:** visual context with a fill blank or short response
discussion. Existing types remain under review.

**Prompt:** With Figure 2 visible, label the upward movement from the lake:
“Water warmed by the sun rises from the lake through ________.”

**Static alternative:** show Figure 2 with all labels, then present the
sentence as text. No keyed response or grading rule is supplied here.

### Figure placement

**Candidate composition:** existing `visual` plus `dnd` discussion. A keyboard
alternative selects a source label, then a named target.

| Named target | Visible source context |
| --- | --- |
| Target A, lake arrow | Arrow rising from the lake |
| Target B, cloud | Cloud formation area |
| Target C, rain arrow | Arrow from cloud to land |

**Static alternative:** show a named target list and ask the reader to state
which label belongs at each target. No placement acceptance, key, partial
credit, or scorer behavior is proposed.

### Rainfall table prompt

**Synthetic export:** existing `short` for a prose comparison. The separate
value-retrieval treatment retains its blanks and optional value bank.

**Prompt:** Using Monday’s equal collection intervals, describe the difference
between Gauge A and Gauge B.

The source values stay visible. The exported `short` item has a proposed model
answer and rubric pending human review. No accepted answer exists.

## Limits

Source reproduction and presentation are user choices. Human touch,
screen-reader, zoom, visual approval, real-course comparison, and format
acceptance are deferred under the 2026-09-11 direction. They do not block
continued synthetic work. The current direction and revisit triggers are in
[the prototype owner](README.md#current-direction-2026-09-11).

Separate runtime candidates now exist for label-to-location matching in
`runtime-candidate/water-process-placement.txt` and for explaining the rainfall
comparison in `runtime-candidate/rainfall-comparison.txt`. The latter is
learning practice using `short`, with prose left pending. These are hand-authored
format experiments. The studio exports placement and Monday comparison drafts on request.
Choose Rainfall observations, then Explain Monday comparison. Edit the
instruction and purpose, try an ungraded prose response, and use Review draft,
Create bank draft, then Download bank draft. The file embeds Monday, Gauge A
12 mm, Gauge B 18 mm, their equal 24-hour interval, and the exact source locator.
Both author fields require one plain-text line. Unsafe structural text is
visibly refused instead of silently rewritten. Changes clear old exports.
Trial responses never enter the proposed model answer or rubric.
Typed labels and table retrieval retain their existing ungraded preview. A value bank with visible table cells can
allow elimination, so the blank exercise is source-value recognition or recall.
It does not establish rainfall reasoning or examination fidelity.

- The HTML page uses adjacent CSS and JavaScript files and works offline.
- Choices, target pairing, and draft edits stay in page memory unless the user
  downloads a separate placement or comparison bank draft.
- Downloaded bank drafts include a proposed source-derived key or rubric for
  author review. The studio has no scorer, mastery result, evidence record, source
  binding, accepted write, localStorage, fetch, or submitted learner response.
- `visual`, `table`, `dnd`, and `build` remain candidates for future format and
  accessibility review. This prototype makes no durable type.
