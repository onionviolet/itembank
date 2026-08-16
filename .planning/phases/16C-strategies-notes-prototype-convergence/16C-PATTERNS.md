# Phase 16C: Strategies, Notes & Prototype Convergence - Pattern Map

**Mapped:** 2026-08-15
**Files analyzed:** 8 planned deliverable groups (notes module, learner-artifact record, strategy registry, composed precedence resolver, progress-claim renderer, note-output trio, legacy-upgrade pipeline, fixtures and tests)
**Analogs found:** 8 / 8 (all on shipped code; the modules 16C composes with from 14A/14B/16A/16B are plan text, not on disk, and are marked as such)

Authoritative goal: `.planning/ROADMAP.md:2032-2112` ("### Phase 16C: Strategies, Notes & Prototype Convergence"). All 14A/14B/16A/16B signatures cited below are read from plan frontmatter and objectives only; none of those files exist on disk yet, and the first 16C plan must open with the recorded precondition check the ROADMAP names at `.planning/ROADMAP.md:2089-2095` (halt by name on divergence, check `14B-FREEZE.md`, `16A-FREEZE.md`, `16B-FREEZE.md`, and Phase 13.9 A9 closure).

## File Classification

| New 16C Thing | Role | Data Flow | Closest Shipped Analog | Match Quality |
|---|---|---|---|---|
| Notes module (note records, anchors, revisions, promotion state) | runtime-tier data module | CRUD via compare-and-swap, append-only evidence side effects | `evidence.py` (store discipline) + `subjects.py` (record validation) | role-match |
| Note storage under approved roots | file layout convention | file I/O, atomic write | `evidence.py:38-40` (`EVIDENCE_DIRNAME`/`LOG_FILENAME`) and `runtime.py:1430-1437` (`write_session`) | exact for write discipline |
| Learner-artifact record (rubric, pending/review state, pending evidence) | runtime-tier record + evidence event | event-driven, append-only | `evidence.py` mark/mark_proposal event pattern (`evidence.py:51-57` KNOWN_EVENT_TYPES) | exact |
| Strategy registry (finite registered strategies as data) | model/runtime-tier registry | pure lookup, validation | `subjects.py:1-60` (profiles as versioned data, code-owned fallback) | exact |
| Composed mode-layer precedence resolver | pure resolver over live layer state | request-response, pure function | `selection.py:1-35` (pure, everything-arrives-as-arguments) + `surfaces/ia.py` `mode_layer_resolve` (plan text, not on disk; 16B-07-PLAN.md) | role-match |
| Progress-claim renderer (tuple display, per-objective fill, no aggregates) | render-only surface component | transform, no I/O | `surfaces/retention_view.py:1-25` | exact |
| Note-output trio (notebook page, Cornell, concept map) as projections | validator + projection over one parsed model | transform | `model.py:2250-2261` (`STYLE_CHECK_CATALOGUE`) + `surfaces/lesson.py` renderers (e.g. `render` helpers around lines 633-845) | exact |
| Legacy-upgrade audit and bounded-diff pipeline | read-legacy, propose, write-through-one-writer | batch, dry-run by default | `surfaces/migrate.py:1-50` | exact |
| Cross-subject missing-feature fixtures (four synthetic subjects) | fixtures | static data | `fixtures/subject_loop_emt.md`, `subject_loop_math.md`, `subject_loop_cs.md` | exact (extend to a fourth history subject) |
| Tests | direct-execution roundtrip scripts | subprocess/import, `fail()` | `tests/subject_loop_roundtrip.py:1-30, 278` | exact |

## Pattern Assignments

### Notes module and note storage

**Analog:** `evidence.py` and `runtime.py`.

- Module placement: a root-level runtime-tier peer. `evidence.py:12-16` states the tier rule explicitly ("a peer of runtime.py, not an extension of it, and never imported by model.py"). The planned 14A `journal.py` claims the same placement ("journal.py at the repository root, a runtime-tier peer of runtime.py and evidence.py", `.planning/phases/14A-identity-lifecycle-operation/14A-02-PLAN.md:35`; plan text, not on disk). A 16C notes module should be a root-level peer named to avoid the reserved names below.
- Atomic durable write: copy `runtime.py:1430-1437` (`write_session`: write to `target + ".tmp"`, then `os.replace`) and `evidence.py:1128-1154` (index rebuilt through `index + ".tmp"` then `os.replace`). Under the 14A contract, durable note mutations should route through `journal.commit_operation` once it exists (plan text, `14A-02-PLAN.md:106`, fourteen-step compare-and-swap sequence; not on disk). Until the precondition check confirms it, the shipped `.tmp` + `os.replace` pattern is the only on-disk precedent.
- Append-only evidence effects: note-derived evidence (for example a promotion review outcome) is a new event type added to `KNOWN_EVENT_TYPES` (`evidence.py:51-66`), written only through `evidence.append_event` (`evidence.py:735`), never `append_line` directly (the rule `surfaces/migrate.py:7-10` states). Readers filter through `live_events` (`evidence.py:1355`), so retraction works for free.
- Anchor and relocation states (resolved, relocated_exact, relocated_probable, orphaned) are a closed vocabulary declared as a module tuple, the `GATE_MODES` / `KNOWN_VERIFIERS` shape (`evidence.py:75-77` area, `subjects.py:54`).
- Must not copy: `evidence.py`'s single-log-per-store assumption does not make notes evidence. Notes are learner-owned artifacts, not evidence events; only review and promotion outcomes touch the evidence log. Never let a note record settle a score or mastery (ROADMAP.md:2043-2046).
- Schema: publish a note schema JSON under `schemas/` restricted to the keyword subset `schema_validate.py:27-31` supports (unsupported keywords are refused, `schema_validate.py:50-71`), and validate fixtures in tests via `schema_validate.validate` (`schema_validate.py:120`). The 16A plans name shared note and activity schemas (plan text, ROADMAP.md:2084-2086); reuse rather than fork once 16A exists.

### Learner-artifact record (pending evidence)

**Analog:** the mark / mark_proposal split in `evidence.py`.

- `evidence.py:51-57` already distinguishes `mark` (a settled human verdict) from `mark_proposal` (advisory, never settling). Retention states the read-side rule: "pending manual responses count toward pacing/attempts only; the latest accepted human mark settles constructed work; a model proposal or interaction event never settles anything" (`retention.py:23-26`, D-09/D-16/D-22). A learner artifact with a rubric copies exactly this: the runtime records pending, a reviewer event settles, and nothing else does.
- Must not copy: do not invent a second scorer or a parallel verdict store. The runtime invariant (CLAUDE.md) allows advisory proposals inside the one evidence store only.

### Strategy registry

**Analog:** `subjects.py:1-60`.

- Registry shape: strategies are versioned data records, never Python subclasses (`subjects.py:10-12`, D-01/D-02). A code-owned conservative fallback exists and is never replaced by settings data (`DEFAULT_PROFILE`, `subjects.py:39-48`, D-03). 16C's "unavailable strategy falls back to continuous reading" (ROADMAP.md:2056) maps one-to-one: continuous reading is the code-owned default strategy.
- Closed vocabularies as sorted tuples: follow the `LINT_CODES` construction, `tuple(sorted({...}))` so sortedness and dedup are structural (`model.py:2172-2215`; precedent restated by `surfaces/gift.py:29-35` GIFT_CODES, `surfaces/settings.py:39` SETTINGS_CODES, `model_adapter.py:32-33`). Any strategy-lint or note-lint codes 16C adds should be new dotted members of an existing or new sorted tuple, additive only (D-16 comment at `model.py:2172-2173`).
- Must not copy: no Cartesian product of style toggles (ROADMAP.md:2056-2057). The registry is finite; do not model strategies as free-form settings the way `itembank.json` models preferences.

### Composed mode-layer precedence resolver

**Analog:** `selection.py:1-35` for the shape; `surfaces/ia.py` for the contract (plan text, not on disk).

- 16B-07 ships `mode_layer_resolve` as a pure function over an explicitly supplied mapping with "no live-state collector"; the composed resolver reading live state "stays Phase 16C's work under D8" (`.planning/phases/16B-ia-modes-recovery-contract/16B-07-PLAN.md`, must_haves truth 6 and key_links; plan text, not on disk). 16C therefore writes a collector that gathers each layer's live state and calls the one 16B function; it must not reimplement precedence, or two implementations of one contract exist (the key_link warning in that same frontmatter).
- The shape to copy from shipped code: `selection.py:8-13`, "selection is pure: deterministic given its inputs and opens no file of its own; the caller reads the snapshot and passes it in." The collector does the file reads; the resolver stays pure.
- Conflict copy is fixed verbatim: "{Setting name} is set by {higher layer name} for this course and can't be changed here." (16B-07-PLAN.md must_haves truth 3; ROADMAP.md:2061-2062). Substitute display names, never internal keys (16B-07 key_links). The seven-layer table lives in `.planning/phases/16B-ia-modes-recovery-contract/16B-UI-SPEC.md:244` ("## Mode-Layer Precedence Contract"); MODE_LAYERS in `surfaces/ia.py` is the single ordering source once it exists (plan text).
- Must not copy: runtime assessment behavior is never user-configurable during a sitting (ROADMAP.md:2059-2060); do not route those settings through the resolver as if they were preferences.

### Progress-claim renderer

**Analog:** `surfaces/retention_view.py:1-25`.

- Render-only: functions accept already-derived dictionaries and perform no arithmetic, no I/O, no model reads, locked copy verbatim, "no streaks, points, targets, or loss states ever render here" (`surfaces/retention_view.py:7-14`). The claim-tuple renderer copies this exactly: it formats the tuple (claim kind, scope and version, numerator, denominator or indeterminate, rule, snapshot or window, settled/pending/unknown, authority, uncertainty) and computes nothing.
- Missing denominator: retention already renders `unknown` instead of a fabricated number (`_fmt_rate`, `surfaces/retention_view.py:22-25`; `retention.py:16-17` D-03 "no denominator yields an explicit null, not 0"). ROADMAP.md:2067-2069 requires "indeterminate rather than an invented percent"; same rule, new word.
- Must not copy: no aggregate completion, mastery, or readiness score anywhere (ROADMAP.md:2065-2066). Do not add a summary row the way a dashboard would; Retrievability is never a percentage (ROADMAP.md:2070).

### Note-output trio (notebook page, Cornell notes, concept map)

**Analog:** the Phase 03.1 style registry in `model.py` plus the lesson renderer in `surfaces/lesson.py`.

- One parser, projections over it: `.planning/STYLE-DISCIPLINE-16A-2026-08-14.md:19-22` is binding: "a semantic style is a validator plus a projection over the one parsed content model. It never introduces a second parser, second renderer, or second content truth." The one parse is `model.parse_lesson` (`model.py:469`); the trio renders from its output the way `surfaces/lesson.py` renders glossary panels, reader nav, and print CSS from one parse (`surfaces/lesson.py:760-845`). Zero re-parsing, zero per-style content forks (ROADMAP.md:2072-2073).
- Per-mode validators: register each mode's checks as new members of a closed catalogue, the `STYLE_CHECK_CATALOGUE` pattern (`model.py:2250-2261`): every emitted code is a `LINT_CODES` member, severity ceilings are declared in code, and "a style file can never add one" (`model.py:2247-2249`). Validator foci per mode come from the STYLE-DISCIPLINE table (Cornell: every cue maps to notes, linear degradation; concept map: every edge typed, textual adjacency fallback; notebook page: ownership, anchors, provenance) at `.planning/STYLE-DISCIPLINE-16A-2026-08-14.md:30-38`.
- Degradation: each output must remain coherent plain Markdown (ROADMAP.md:2074-2075), the same plain-first rule the lesson surface already honors and CLAUDE.md's authored-output verification step 6 requires.
- Must not copy: do not model the trio as cosmetic themes under `styles/*.md`; they are semantic transformations by the binding rule, so they need validators and structure, not tokens.

### Legacy-upgrade audit and bounded-diff pipeline

**Analog:** `surfaces/migrate.py:1-50`.

- Copy: read legacy stores read-only (`surfaces/migrate.py:5-8`), write only through the one writer (`evidence.append_event`, lines 7-10), deterministic identity via `source_key(kind, path, ref)` sha256 (`surfaces/migrate.py:12-27, 66`), no resolution by heuristics ("no stem-similarity path, deliberately", lines 29-40), and dry run by default with a printed reconciliation, `--write` opt-in (`surfaces/migrate.py:42-47, 378` `cmd_migrate`). The 16C bounded diff before editing (ROADMAP.md:2076-2079) is the same posture: audit first (the eleven-item baseline), present the diff, then mutate through the compare-and-swap path.
- Must not copy: `migrate.py` appends evidence; the 16C pipeline mutates artifacts, so its writes go through the 14A journal operations (plan text: six distinct handlers link/import/copy/move/edit/supersede over one `commit_operation`, `14A-03-PLAN.md:79`; not on disk) and halt for explicit review whenever keyed content, difficulty, or objective alignment would change (ROADMAP.md:2081-2083).

### Fixtures and tests

**Analogs:** `fixtures/subject_loop_emt.md` / `subject_loop_math.md` / `subject_loop_cs.md` (three synthetic subjects already exist; 16C adds a fourth, history, per ROADMAP.md:2096-2099) and `tests/subject_loop_roundtrip.py`.

- Test convention: direct-execution stdlib scripts, no pytest, module-level `fail(msg)` printing "FAIL:" and exiting 1 (`tests/subject_loop_roundtrip.py:278`, `tests/evidence_roundtrip.py:38`), driving real modules against temporary synthetic banks (`tests/subject_loop_roundtrip.py:1-22`). Test names follow `*_roundtrip.py`; 16B plan text already reserves `tests/mode_layer_roundtrip.py`, so 16C tests need distinct names (suggest `notes_roundtrip.py`, `strategy_roundtrip.py`, `note_output_roundtrip.py`, `legacy_upgrade_roundtrip.py`; none exist on disk today).
- Fixture builders: no shipped `fixtures/*.py` corpus builder exists except `fixtures/grandchild_spawner.py` (a process helper, not a corpus builder). Plan text reserves `fixtures/corpus_14b.py`, `fixtures/course_storyboard_corpus.py`, and `fixtures/lesson_capability_corpus.py` (14B and 16B/16A frontmatter; not on disk). A 16C corpus builder should follow that naming shape, for example `fixtures/missing_feature_corpus.py`.
- Structural closed-set tests: copy `tests/config_roundtrip.py:700-713` (SETTINGS_CODES is sorted, deduped, and every code reachable by some test input) for any new strategy or note lint-code tuple.
- Named freeze-gate fixtures: STRATEGY-01 (fallback to continuous reading), STRATEGY-02 (conflict matrix, extending 16B's conflict fixture rather than duplicating it), NOTE-01 (broken anchor stays attached to objective), NOTE-02 (unreviewed note stays private) per ROADMAP.md:2096-2111.

## Shared Patterns

### Atomic write
**Source:** `runtime.py:1430-1437` (`write_session`), `evidence.py:1128-1154` (index rebuild). Apply to every durable 16C write: temp file, validate, `os.replace`. Once 14A executes, prefer `journal.commit_operation` (plan text).

### Append-only evidence with read-side retraction filter
**Source:** `evidence.py:735` (`append_event`), `evidence.py:1355` (`live_events`), `evidence.py:162` (`append_line`, one locked write syscall). New event types are additive entries in `KNOWN_EVENT_TYPES` (`evidence.py:51-57`) with the plan number recorded in the comment above it, matching the existing per-plan annotations at `evidence.py:42-50`.

### Closed sorted code tuples
**Source:** `model.py:2176` (`LINT_CODES`), `surfaces/settings.py:39` (`SETTINGS_CODES`), `surfaces/gift.py:35` (`GIFT_CODES`). Construction is `tuple(sorted({...}))`; additions are additive, renames are breaking.

### Schema validation
**Source:** `schema_validate.py:27-31` (supported keyword subset), `schemas/*.json`. New 16C schemas must stay inside the subset or the validator refuses them (`schema_validate.py:50-71`); `schema_validate.py --all` self-checks every document in CI (`schema_validate.py:247-284`).

### Pure derivation over one captured snapshot
**Source:** `retention.py:1-45`, `selection.py:1-13`. Every 16C derived claim (progress tuples, strategy eligibility, resolver output) is a pure function of arguments; callers do the I/O.

## Reserved Names (plan text, not on disk)

To compose without collision, 16C must not claim these module names, all reserved by unexecuted plan frontmatter:

| Name | Reserved by | Evidence |
|---|---|---|
| `identity.py`, `journal.py`, `discovery.py` | 14A | `14A-02-PLAN.md:8,35`, `14A-03-PLAN.md:8`, `14B-01-PLAN.md:19` |
| `graph.py`, `course.py`, `course_package.py`, `sample_course.py` | 14B | `14B-01-PLAN.md:8-9,28-29,82` |
| `capabilities.py` | 16A | `16A-01-PLAN.md:194` (module boundary D-16A-2) |
| `surfaces/ia.py` (MODE_LAYERS, mode_layer_resolve) | 16B | `16B-07-PLAN.md` frontmatter files_modified and artifacts |
| `fixtures/course_storyboard_corpus.py`, `fixtures/lesson_capability_corpus.py` | 16A/16B | plan frontmatter file lists |
| `tests/mode_layer_roundtrip.py`, `tests/journal_roundtrip.py`, `tests/operations_roundtrip.py`, `tests/graph_roundtrip.py`, `tests/course_package_roundtrip.py`, `tests/identity_roundtrip.py`, `tests/ia_route_roundtrip.py` | 14A/14B/16B | plan frontmatter file lists |

Suggested non-colliding 16C names (suggestions only, planner decides): `notes.py`, `strategies.py`, `learner_artifact.py` (or fold into `notes.py`), `surfaces/progress_view.py` or extension of `surfaces/ia.py` once it exists, `surfaces/note_outputs.py`, `surfaces/legacy_upgrade.py`. None of these exist on disk today.

## No Analog Found

| Thing | Reason | Fallback |
|---|---|---|
| Anchor/selector with quoted-context hash and relocation states | No shipped anchoring code exists; D-14A-2 component IDs (the anchor targets) are plan text in 14B | Design from the ROADMAP.md:2036-2043 vocabulary; hash discipline follows `evidence.py:17-19` (sha256 as change detection, never security) |
| Concept-map structure model | No graph renderer ships; `graph.py` is 14B plan text | Textual adjacency fallback per STYLE-DISCIPLINE table; validator via STYLE_CHECK_CATALOGUE pattern |

## Metadata

**Analog search scope:** repository root modules, `surfaces/`, `tests/`, `fixtures/`, `schemas/`, `styles/`, `.planning/phases/14A-*`, `14B-*`, `16A-*`, `16B-*` (frontmatter and objectives only)
**Files read in full or targeted:** `schema_validate.py`, `model.py:2170-2299`, `evidence.py` (head plus anchors), `runtime.py` anchors, `subjects.py` head, `retention.py` head, `selection.py` head, `surfaces/migrate.py` head, `surfaces/retention_view.py` head, `surfaces/settings.py` anchors, `tests/subject_loop_roundtrip.py` head, `16B-07-PLAN.md` frontmatter and objective, `.planning/STYLE-DISCIPLINE-16A-2026-08-14.md` head, ROADMAP.md Phase 16C section
**Pattern extraction date:** 2026-08-15
