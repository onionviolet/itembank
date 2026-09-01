# Course graph

This file is the durable cross-object course graph for this course. It is
plain Markdown on purpose: it stays readable and diffable by hand, and it
never becomes the only understandable copy of anything it records. Edges
that relate two independently identified objects are written here.

| field | value |
|---|---|
| graph_schema_version | 1 |
| course_object_id | ba070378d35d44e7 |
| title | Aldrasse Fen Ecology 101 |

## Structure

| id | label | parent | order | title |
|---|---|---|---|---|
| a1af12281f2a4e65 | unit |  | 1 | Unit 3: Peat Hydrology and the Lantern Moss Cycle |

## Objectives

| id | container | order | statement | origin | import_version | overlays |
|---|---|---|---|---|---|---|
| 67b9a4f0cfab4cb8 | a1af12281f2a4e65 | 1 | O3.1 Explain why the Aldrasse fen is minerotrophic and how lateral mineral inflow sets its porewater chemistry and plant community | local |  |  |
| 98b0c52691954d27 | a1af12281f2a4e65 | 2 | O3.2 Describe the acrotelm and catotelm structure and predict water table response to a storm versus seasonal recharge | local |  |  |
| 2589f5292d234a4d | a1af12281f2a4e65 | 3 | O3.3 State the drought threshold (water table more than 25 cm below surface) and how vegetation registers an excursion | local |  |  |
| a46a877388f54575 | a1af12281f2a4e65 | 4 | O3.4 Explain why peat accumulation tracks water table position and estimate profile age from an accumulation rate | local |  |  |
| 4f3456e288a44412 | a1af12281f2a4e65 | 5 | O3.5 Describe the lagg zone's two roles and the station A1 conductance condition that triggers a resample | local |  |  |
| 1db0edbda647453a | a1af12281f2a4e65 | 6 | O3.6 Sequence the four phases of the lantern moss annual cycle and the early-summer hinge | local |  |  |
| ae08d09cd3714164 | a1af12281f2a4e65 | 7 | O3.7 Use lantern moss vitality scores as a hydrological instrument tied to the dipwell threshold | local |  |  |

## Sources

| source_object_id | title | note |
|---|---|---|
| 8bd25c20ceaa4e20 | sources/fen_hydrology_field_notes.md |  |
| 5c5bc6b17baa44c6 | sources/lantern_moss_survey.md |  |

## Edges

| source | edge_type | target | authority | rationale | confidence | override |
|---|---|---|---|---|---|---|

## Bindings

| binding_kind | objective | source_object_id | treatment_kind | locator | state | confidence | rights_snapshot |
|---|---|---|---|---|---|---|---|
| source | 67b9a4f0cfab4cb8 | 8bd25c20ceaa4e20 |  | sources/fen_hydrology_field_notes.md#basin-overview | covered | high | granted |
| source | 98b0c52691954d27 | 8bd25c20ceaa4e20 |  | sources/fen_hydrology_field_notes.md#water-table-dynamics | covered | high | granted |
| source | 2589f5292d234a4d | 8bd25c20ceaa4e20 |  | sources/fen_hydrology_field_notes.md#water-table-dynamics | covered | high | granted |
| source | a46a877388f54575 | 8bd25c20ceaa4e20 |  | sources/fen_hydrology_field_notes.md#peat-accumulation-and-decay | covered | high | granted |
| source | 4f3456e288a44412 | 8bd25c20ceaa4e20 |  | sources/fen_hydrology_field_notes.md#mineral-inflow-and-the-lagg-boundary | covered | high | granted |
| source | 1db0edbda647453a | 5c5bc6b17baa44c6 |  | sources/lantern_moss_survey.md#annual-cycle | covered | high | granted |
| source | ae08d09cd3714164 | 5c5bc6b17baa44c6 |  | sources/lantern_moss_survey.md#hydrological-sensitivity | covered | high | granted |
| treatment | 67b9a4f0cfab4cb8 | 8bd25c20ceaa4e20 | guided-lesson | sources/fen_hydrology_field_notes.md#basin-overview | covered | high | granted |
| treatment | 67b9a4f0cfab4cb8 | 8bd25c20ceaa4e20 | practice | sources/fen_hydrology_field_notes.md#basin-overview | covered | high | granted |
| treatment | 98b0c52691954d27 | 8bd25c20ceaa4e20 | guided-lesson | sources/fen_hydrology_field_notes.md#water-table-dynamics | covered | high | granted |
| treatment | 98b0c52691954d27 | 8bd25c20ceaa4e20 | practice | sources/fen_hydrology_field_notes.md#water-table-dynamics | covered | high | granted |
| treatment | 2589f5292d234a4d | 8bd25c20ceaa4e20 | notes-or-terms | sources/fen_hydrology_field_notes.md#water-table-dynamics | covered | high | granted |
| treatment | 2589f5292d234a4d | 8bd25c20ceaa4e20 | practice | sources/fen_hydrology_field_notes.md#water-table-dynamics | covered | high | granted |
| treatment | a46a877388f54575 | 8bd25c20ceaa4e20 | worked-example | sources/fen_hydrology_field_notes.md#peat-accumulation-and-decay | covered | high | granted |
| treatment | a46a877388f54575 | 8bd25c20ceaa4e20 | practice | sources/fen_hydrology_field_notes.md#peat-accumulation-and-decay | covered | high | granted |
| treatment | 4f3456e288a44412 | 8bd25c20ceaa4e20 | direct-reading | sources/fen_hydrology_field_notes.md#mineral-inflow-and-the-lagg-boundary | covered | high | granted |
| treatment | 4f3456e288a44412 | 8bd25c20ceaa4e20 | practice | sources/fen_hydrology_field_notes.md#mineral-inflow-and-the-lagg-boundary | covered | high | granted |
| treatment | 1db0edbda647453a | 5c5bc6b17baa44c6 | guided-lesson | sources/lantern_moss_survey.md#annual-cycle | covered | high | granted |
| treatment | 1db0edbda647453a | 5c5bc6b17baa44c6 | visual-or-demonstration | sources/lantern_moss_survey.md#annual-cycle | covered | high | granted |
| treatment | 1db0edbda647453a | 5c5bc6b17baa44c6 | practice | sources/lantern_moss_survey.md#annual-cycle | covered | high | granted |
| treatment | ae08d09cd3714164 | 5c5bc6b17baa44c6 | guided-lesson | sources/lantern_moss_survey.md#hydrological-sensitivity | covered | high | granted |
| treatment | ae08d09cd3714164 | 5c5bc6b17baa44c6 | practice | sources/lantern_moss_survey.md#hydrological-sensitivity | covered | high | granted |

## Migrations

| migration_id | kind | from | to | rationale | state | actor | timestamp | reviewer | rationale_review |
|---|---|---|---|---|---|---|---|---|---|

## Log

| timestamp | note |
|---|---|
