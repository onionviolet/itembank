# Course graph

This file is the durable cross-object course graph for this course. It is
plain Markdown on purpose: it stays readable and diffable by hand, and it
never becomes the only understandable copy of anything it records. Edges
that relate two independently identified objects are written here.

| field | value |
|---|---|
| graph_schema_version | 1 |
| course_object_id | 0d0d18c491584a92 |
| title | Meridian Field Response |

## Structure

| id | label | parent | order | title |
|---|---|---|---|---|
| b5e6ba5f69b340d7 | module |  | 1 | Scene Size Up |
| 35c5959094a04fd2 | module |  | 2 | Primary Assessment |

## Objectives

| id | container | order | statement | origin | import_version | overlays |
|---|---|---|---|---|---|---|
| 93abf6bff28e4d22 | b5e6ba5f69b340d7 | 1 | Identify scene hazards on arrival | local |  |  |
| 7be9835a22544b9c | 35c5959094a04fd2 | 2 | Choose a body substance isolation level | local |  |  |
| f65f81718cab4146 | b5e6ba5f69b340d7 | 3 | State the number of patients before approaching | local |  |  |
| 13253b84cd1d42e5 | 35c5959094a04fd2 | 4 | Form a general impression in one sentence | local |  |  |
| 543ab4f1695645f6 | b5e6ba5f69b340d7 | 5 | Rank the three findings that change transport priority | local |  |  |
| 3574f6646ac64e3f | 35c5959094a04fd2 | 6 | Hand off using a fixed report order | local |  |  |

## Sources

| source_object_id | title | note |
|---|---|---|
| 86ead446d33843f8 | Field response unit one, working notes | rights are recorded on the source object, never here |

## Edges

| source | edge_type | target | authority | rationale | confidence | override |
|---|---|---|---|---|---|---|
| 93abf6bff28e4d22 | prerequisite-of | 7be9835a22544b9c | authored | the first is read before the second | medium | advisory |
| 7be9835a22544b9c | prerequisite-of | f65f81718cab4146 | authored | the first is read before the second | medium | advisory |
| 13253b84cd1d42e5 | prerequisite-of | 543ab4f1695645f6 | authored | the first is read before the second | medium | advisory |
| 3574f6646ac64e3f | covers-objective | 13253b84cd1d42e5 | authored |  | unknown | advisory |

## Bindings

| binding_kind | objective | source_object_id | treatment_kind | locator | state | confidence | rights_snapshot |
|---|---|---|---|---|---|---|---|

## Migrations

| migration_id | kind | from | to | rationale | state | actor | timestamp |
|---|---|---|---|---|---|---|---|

## Log

| timestamp | note |
|---|---|
