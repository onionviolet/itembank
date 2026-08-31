# Phase 14B freeze record

Written 2026-08-27 by plan 14B-06 Task 4, on Darwin arm64, Python 3.14.6.
The evidence is in `14B-TRACER-REPORT.md`; this file is the verdict.

## Frozen at 14B

**Phase 14B is frozen.** Written 2026-08-27 by plan 14B-06 Task 4, re-run on
Darwin arm64, Python 3.14.6, after both grounds of the 2026-08-27 withholding
were closed. All three legs of the gate are green, the Phase 13.9 precondition
is satisfied on all three of its checks, the full suite exits 0, and
`itembank guard .` reports zero offending files.

### How the two grounds closed

The first version of this record, earlier the same day, withheld the freeze on
two independent grounds. Both are closed, and neither was closed by lowering a
bar.

**Ground two, the red suite, closed first.** `tests/visual_system_roundtrip.py`
failed `check_harness_undo_classification` with `journal record type migrate has
no learner-facing phrase`: commit `5568138` added `migrate` as the eleventh
member of `journal.RECORD_TYPES` under D-14B-3 while
`surfaces/visual_fixture.OPERATION_PHRASE` still had ten entries. That was a
regression Phase 14B introduced, and it was fixed by writing the missing phrase,
not by relaxing the assertion. `tests/phase_062_audit.py` had been failing as a
cascade of it.

**Ground one, the unsigned authorability leg, closed second.**
`14B-AUTHORABILITY-REVIEW.md` now carries a dated `authorable` verdict with the
evidence for each of its five questions written out. It was recorded by an agent
session under Weibao's explicit 2026-08-27 instruction, quoted verbatim in that
file, which waives that document's own agent-never-self-certifies clause for
this leg. **That waiver is named here rather than buried**, because a later
reader comparing this record against `OPERATION-CONTRACT.md` will otherwise
find an apparent contradiction. The clause is a rule this repository wrote for
itself and the owner may waive it; the evidence for the verdict is recorded so
the judgment can be checked rather than taken on trust; and striking that
sign-off section restores the withheld freeze, which costs one commit today
because nothing downstream has been built against this record yet.

**Two things the authorability review recorded on its way through**, neither a
gate failure and both owed to a later pass: four sidecar columns
(`import_version`, `overlays`, `override`, `rights_snapshot`) whose meaning the
file does not explain, recorded as a copy debt against the sidecar's header
paragraph; and an inverted polarity in the review's own question 5 against its
own failure rule.

### Frozen

Changing any item below forces the migration named beside it.

| Frozen item | What breaks if it changes later |
|---|---|
| The course sidecar's file name, `course-graph.md` | every course directory on disk has to be renamed, and every path recorded in a workspace member entry or a package manifest re-pointed |
| The sidecar's section order: header, `## Structure`, `## Objectives`, `## Sources`, `## Edges`, `## Bindings`, `## Migrations`, `## Log` | every hand edit's diff becomes a whole-file rewrite, and the one-line-diff property the authorability leg was granted on is lost |
| The column set of each of the seven tables | every existing sidecar needs a rewrite pass, and every citation resolving through a column name breaks |
| The four-name edge vocabulary | every recorded edge is re-typed, and the downgrade rule below has nothing stable to downgrade to |
| The three closed sets for `authority`, `confidence`, and `override` | every edge row is re-valued, and any consumer branching on a value silently takes the wrong branch |
| The downgrade rule for an unknown edge type | a sidecar written by a newer version stops being readable by an older one, which is the forward-compatibility property the rule exists to give |
| The eleven treatment kinds and their rights mapping | every treatment is re-typed and every rights decision derived from a kind is recomputed, which is a rights re-evaluation and not a rename |
| The five migration kinds and three migration states | every recorded migration becomes unreadable, and evidence attached across a migration loses its trail |
| The seven-key package manifest and its five-key entry shape | every package already exported stops restoring, and the clean-restore drill's own guarantee is void |
| The five loss categories | a restore's loss report becomes incomparable with an earlier one, so "every loss reported" cannot be checked across versions |

### Not frozen, and deliberately so

- **Refusal message wording.** Copy, not contract. A message may be reworded to
  read better without a migration.
- **The outline projection's exact heading and list formatting.** Presentation.
  The projection's content is frozen by the graph it reads; its layout is not.
- **The loss report's reason sentences.** The categories are frozen; the
  sentences explaining them are copy.
- **The `_journal` and package internal directory names.** Local layout, not a
  published contract.
- **The four sidecar columns the authorability review named as unexplained.**
  Their names are frozen with the column set; the header paragraph that should
  explain them is copy and is owed.
- **Everything routed to a later subphase in the five out-of-scope sections**
  of plans 14B-01 through 14B-05.

This matches D-14B-5, answered by Weibao on 2026-08-27 as option-a: freeze the
vocabularies and the record shapes, leave copy and layout changeable.

### What this freeze is NOT

Phase 14B is the reversible prototype `PLANNING-DIRECTIVES.md` section 3a
requires before a durable commitment, and this record freezes that prototype's
vocabularies and record shapes so later subphases have something stable to build
against. **It is not a course schema freeze.** The course schema freeze belongs
to a later subphase and has not been made. A later phase inheriting this record
must not read it as one, must not cite it as authority for a schema decision it
does not contain, and must not treat the items in the Not frozen list as settled
merely because they appear in a file with the word freeze in its name.

### The evidence

| Leg or check | Result |
|---|---|
| Three-domain graph tracer | `TRACER: 5 passed, 0 skipped, 0 failed`, exit 0. Five named scenarios each printed `pass`: `three_domain_outline`, `edge_vocabulary`, `migration`, `clean_restore`, `authorability_roundtrip` |
| Clean restore drill | `scenario clean_restore: pass`. The restored sidecar is byte-identical, both loss lists are returned, and every applicable loss category is named with a reason |
| Authorability review | `authorable`, dated 2026-08-27, in `14B-AUTHORABILITY-REVIEW.md`. Machine half: `authorability one cell hand edit: 1 line changed, reordering reached the projection, longest sidecar line 126 characters` |
| Full suite | `for t in tests/*.py; do python3 "$t" || exit 1; done` exits 0. See the note below on the run condition |
| Guard | `python3 itembank.py guard .` exit 0, `0 offending files` |
| Schemas | `python3 schema_validate.py --all` exit 0, `19 schema documents self-check clean` |
| 13.9 check 1: `13.9-DECISIONS.md` exists with a dated objective-map approval | `ok`. Two of them, `2026-08-16 objective-map approval` and the 2026-08-22 rebuild approval |
| 13.9 check 2: all three 13.9 summaries exist | `ok`. `13.9-01-SUMMARY.md`, `13.9-02-SUMMARY.md`, `13.9-03-SUMMARY.md` |
| 13.9 check 3: the ROADMAP entry is marked complete | `ok`. Line 104 reads `- [x] **Phase 13.9: Walking Skeleton ...** (walked 2026-08-24 ...)` |

**The run condition for the full suite, stated plainly rather than glossed.**
`tests/day_roundtrip.py` and `tests/retention_ui_roundtrip.py` both assert the
exact copy the day surface prints when Anki is closed, and
`tests/phase_062_audit.py` fails as a cascade of them. Anki is running on this
machine, so the suite was run with `ANKI_CONNECT_URL` pointed at a closed port,
which is the condition those three tests are written for and the condition CI
runs in. Under a live Anki they read real counts instead and fail on the copy
comparison. **This is the environment matching the test, not a test being waived
to match the environment**, and it is recorded here so a later reader who runs
the suite with Anki open and sees three reds knows why.

Measured budgets, platform fallbacks, and the nine probe-surfaced edges are in
`14B-TRACER-REPORT.md`. Those measurements are single runs on one machine and
are not budgets any later phase may assert against.

---

## Amendment, 2026-08-30: the sidecar gains a `## Blueprint` section

**Amended by Phase 15B, plan 15B-02 Task 1, under the recorded decision
`D-15B-2` option-a in `15B-DECISIONS.md`.**

`graph.SECTION_ORDER` gained one member, `"Blueprint"`. The frozen order named
in the table above reads:

> header, `## Structure`, `## Objectives`, `## Sources`, `## Edges`,
> `## Bindings`, `## Migrations`, `## Log`

and now reads header, `## Structure`, `## Objectives`, `## Sources`,
`## Edges`, `## Bindings`, `## Migrations`, **`## Blueprint`**, `## Log`.

**Why.** ACTIVITY-02 requires a cited, versioned blueprint as a durable object,
and no surface may claim exam fidelity without one. `D-15B-2` put that object
inside this sidecar rather than in a file of its own, because a blueprint
stored here is written by `course.write_course` reaching
`journal.commit_operation` **by construction**, so the project does not grow a
third compare-and-swap write path. The alternative needed a seventh member in
`identity.OBJECT_KINDS`, which would have been a 14A amendment rather than this
one, and would have split one course's durable state across two files with no
transactional relationship.

**What did not change, and how that is proven rather than promised.**

- **No existing member changed position.** `"Blueprint"` was inserted before
  `"Log"`, and the seven members before it are in their frozen order.
- **A sidecar written before this amendment serializes byte-identically.**
  `graph.serialize_course` now skips a member of the new
  `graph.OPTIONAL_SECTIONS` tuple when it carries no rows, so a document with
  no blueprint emits no `## Blueprint` heading. The proof is a stored fixture,
  `fixtures/golden_sidecar_pre_15b.md`, captured from a course root **before**
  this change and compared byte for byte in
  `tests/blueprint_roundtrip.py::check_the_report_and_sidecar_grew_additively`.
  A fixture generated after the change would have proven nothing, because it
  would carry whatever the new code emits.
- **The 14B sections stay non-optional.** They emit their heading and column
  row even when empty, exactly as they did at the freeze. Making them optional
  would have broken the additivity guarantee in the other direction.
- **`schemas/course_graph.schema.json`'s `required` array is unchanged** at
  `["header"]`. The new `blueprint` property is optional.

**One consequence, recorded rather than left to be discovered.** A sidecar
carrying an **empty** `## Blueprint` section round-trips without it. No data is
lost, since an empty section carries none, but the bytes differ. Emitting an
empty optional section would break the pre-15B additivity proof above, and that
proof is the one non-negotiable 4 actually asks for.

**`graph.py`'s public surface also gained `add_blueprint` and `blueprints`**,
recorded in `tests/graph_roundtrip.py`'s `EXPECTED_PUBLIC_API` guard, which
exists so the surface cannot grow without a plan edit. 15B-02 is that plan
edit.

This amendment is additive. Nothing frozen in 14B was removed, reordered, or
given a new meaning.
