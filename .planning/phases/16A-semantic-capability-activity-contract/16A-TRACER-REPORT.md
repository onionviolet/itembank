# Phase 16A tracer report

**Run 2026-08-28 on Darwin arm64, Python 3.14.6.** Every figure below was
produced by that run on that machine. No target, budget, or estimated number
appears anywhere in this file.

---

## 1. What was run

```
$ python tests/capability_stress_corpus_tracer.py
scenario thin_slice: pass
scenario additivity_golden_parse: pass
scenario fourteen_roles: pass
scenario unknown_semantics: pass
scenario example_order: pass
scenario capability_profiles: pass
scenario unavailable_renderer: pass
scenario media_metadata: pass
scenario activity_declarations: pass
scenario unsupported_response_form: pass
scenario output_modes: pass
scenario backburner_catalog: pass
scenario localization: pass
scenario assessment_authority: pass
scenario medical_case: pass
scenario disputed_timeline: pass
scenario section_order: pass
scenario portability: pass
TRACER: 18 passed, 0 skipped, 0 failed
```

```
$ python tests/assessment_authority_adversarial.py
ADVERSARIAL: 18 attempted, 18 refused, 0 succeeded
```

```
$ python tests/capability_profile_check.py
capability registry ok

$ python tests/activity_declaration_check.py
activity declarations ok

$ python tests/output_mode_check.py
output modes ok

$ python tests/localization_render_check.py
localization render ok
```

```
$ python itembank.py guard .
0 offending files
```

```
$ for t in tests/*.py; do python "$t" || echo "FAIL $t"; done
FAIL tests/day_roundtrip.py
FAIL tests/phase_062_audit.py
FAIL tests/retention_ui_roundtrip.py
```

Those three are **pre-existing** and are not caused by Phase 16A. All three
were re-run against a clean `git stash` of this phase's work during plan
16A-03's execution and failed there too. `tests/day_roundtrip.py` specifically
fails because a live Anki instance is reachable on this machine, so the
"Anki closed" locked copy it asserts is not what `day --check` prints here.

## 2. The nine freeze-gate legs

One row per leg of `ROADMAP.md`'s Phase 16A freeze-gate paragraph.

| # | Leg | Result | Covered by |
|---|---|---|---|
| 1 | one synthetic lesson exercising every semantic teaching role, plus one unknown optional and one unknown required semantic, in both continuous and guided modes | passed | `scenario_fourteen_roles`, `scenario_unknown_semantics` |
| 2 | the medical evolving-case fixture with a dated jurisdiction warning and no premature reveal | passed | `scenario_medical_case` |
| 3 | the disputed-timeline fixture preserving disagreement, locators, and uncertainty | passed | `scenario_disputed_timeline` |
| 4 | the localization fixture set inside the corpus | passed | `scenario_localization`, `tests/localization_render_check.py` |
| 5 | the capability profile fixture with one renderer marked unavailable showing the static instructional path | passed | `scenario_capability_profiles`, `scenario_unavailable_renderer` |
| 6 | the two-output-mode composition fixture plus one backburner catalog entry | passed | `scenario_output_modes`, `scenario_backburner_catalog` |
| 7 | the purpose-first activity set including one unsupported response form falling back to its declared static equivalent | passed | `scenario_activity_declarations`, `scenario_unsupported_response_form` |
| 8 | the adversarial runtime-authority fixture in which every leak, invented-score, auto-grade, and frozen-sitting edit attempt is refused | passed | `tests/assessment_authority_adversarial.py`, recorded by `scenario_assessment_authority` |
| 9 | the corpus opened outside the app with every derived HTML, index, and cache deleted, staying readable and rebuilding | passed | `scenario_portability`, `scenario_section_order` |

**No leg is marked `weaker proof` or `not run`.**

Leg 2 deserves a sentence about why it is a full-strength proof rather than a
weaker one, because the plan anticipated it might not be. The assertion is made
on `lesson_page`'s return value with a real gate context built the way
`surfaces/daemon.py` builds one. `lesson_page` **is** the daemon's renderer:
the route calls it and sends its output with
`handler.send_html(page.encode("utf-8"))` and nothing in between, so its return
value is the served bytes. The truncation asserted is therefore Phase 6.2's
server-side stop, not a DOM hide. The scenario asserts the resolution token is
absent from the served bytes while the check is open, present in the canonical
Markdown throughout, and present in the served bytes once the check is cleared,
which also rules out a gate that withholds permanently rather than gating.

## 3. Measured figures

| Figure | Value |
|---|---|
| tracer wall clock | 9.2 s |
| adversarial suite wall clock | 0.1 s |
| full suite wall clock (78 files) | 368.1 s |
| tracer scenarios | 18 passed, 0 skipped, 0 failed |
| adversarial attacks | 18 attempted, 18 refused, 0 succeeded |
| `build_all_16a` returned entries | 17 |
| corpus files written to disk | 18 |
| corpus total bytes | 64,433 |
| derived files created, deleted, and rebuilt in `scenario_portability` | 51 |
| lint codes added by Phase 16A | 20 |
| capability profiles registered | 15 |
| semantic roles catalogued | 14 |
| callout kinds registered | 11 |

The corpus writes 18 files from 17 returned entries: the seventeenth and
eighteenth are `build_media_lesson`'s bank plus the 67-byte synthetic
placeholder PNG it writes beside it, which is a file on disk and not a returned
bank path.

The 51 derived files are three per parseable corpus bank: a rendered HTML page,
a composed outline record, and a composed glossary record.

## 4. Additivity evidence

The three baseline values from `16A-PRECONDITION.md`'s Additivity baseline
section, recorded before any Phase 16A grammar existed, beside the values found
now:

| File | Recorded 2026-08-27 | Found 2026-08-28 |
|---|---|---|
| `fixtures/lesson_golden_phase3_parse.json` | `4078e7532ed33b341a6d551791d8ecc72175e1e479c63420b56db2b635a8e5aa` | identical |
| `fixtures/lesson_golden_phase3_content.txt` | `800edb4cc180cda67885dc558e6784e713e9d636f9ebf8336919c1df93318a3c` | identical |
| `fixtures/lesson_bank.md` | `e34d5c9d3c2c16115257d5b1640f8aa9386e037ff6a15bc1eb6480d82c64398e` | identical |

Four lesson directives, eleven callout kinds, four preamble registries, twenty
lint codes, and three new `lesson_page` keywords were added, and a bank using
none of them parses and renders byte for byte as it did before any of it
existed.

`git status --porcelain` reports no deleted file after the run:
`scenario_portability` deletes only inside its own temporary tree, and every
path it removes is asserted to be under that root before the removal.

## 5. Open findings

### From plan 16A-09's adversarial suite: ALL THREE RESOLVED 2026-08-28

The three findings below were recorded as open when this report was first
written. They were resolved the same day, before the freeze, rather than
carried into it. The original text is kept for trace; the resolution follows
each.

- **F1. `runtime.glossable` is extremely over-strict for multiple-choice
  items.** `runtime.canonical_key` for an `mc` item returns the bare correct
  option letter, and `glossable` tests it as a substring of the collapsed,
  lowercased definition, so **any definition containing that letter is
  refused**. The fixture works around it with a control term that avoids the
  letter, documented in place. The fix is a runtime decision, not a patch:
  either `canonical_key`'s single-letter output should not be a substring
  fragment, or `glossable` should match option letters on a token boundary.
  **RESOLVED.** Fixed in `runtime.glossable`: fragments match on word
  boundaries, and a single-character fragment discloses only when it appears
  as a capital naming a letter rather than as an article. This was a shipped
  defect, not a 16A regression: it had turned the hover glossary off in any
  bank with a multiple-choice item, killing the feature the 2026-08-20 vision
  entry asks for by name. Regression assertions added, including the admit
  cases, which are what was missing.
- **F2. `glossable`'s verdict has no consumer for the three new mouths.** The
  media `alt`, the activity `static_fallback`, and the `[!EXCERPT]` body are
  all classified as keyed material by the gate, and nothing reads that
  classification before rendering them. Adding a consumer would be inventing
  runtime enforcement Phase 16A is out of scope for. **RESOLVED, and the finding itself was partly wrong.** The excerpt rationale
  was classified as keyed only by the F1 bug. `glossable`'s fragment set is
  now derived from the fields `public_item` WITHHOLDS, which adds the authored
  rationale block, so the two gates agree by construction.
- **F3. An `[!EXCERPT]` publishes what it quotes.** A lesson page is authored
  reading material and is not gated on a response, so an author who quotes
  their own rationale into an excerpt has published it. Whether the linter
  should warn on an excerpt body matching an item's rationale is a real option,
  recorded rather than built. **RESOLVED.** `lesson.authored_key_disclosure` warns the author, naming the
  surface and quoting the text, for an excerpt body, a media alt, or an
  activity static fallback that reproduces keyed material. A warning at
  authoring time, not a render-time suppression.

**None of the three was an attack that succeeded.** All eighteen attacks were
refused. These were things the suite learned by attacking honestly, and all
three are now fixed rather than deferred.

### Deferred by decision

- **Media rights enforcement**, deferred by `D-16A-8`. 16A declares rights and
  enforces none of them; the byte-identity assertion in
  `scenario_media_metadata` is what keeps that true. **Owner: whichever
  subphase first packages or exports a media asset.**
- **Media integrity recomputation**, deferred. The `integrity` column is
  declared and never verified. A field that looks verified and is not is worse
  than one that is plainly unverified. **Owner: the same subphase.**
- **A media row's rights are coarser than every other rights record in the
  tree**, recorded in `D-16A-8`'s own execution note: one of `granted`,
  `denied`, `unknown` rather than the seven-key operation map. **Owner: the
  enforcement subphase, which inherits the question.**
- **The annotated worked-example structure**, recorded by `D-16A-6` as a
  Registered-tier enhancement for a later capability-profile version bump.
- **A structured `effective_date` or `jurisdiction` field on `[!WARNING]`**,
  deferred by `D-16A-7`, contingent on 15B's staleness machinery. The medical
  fixture uses free prose with a stated date, which is that decision's form.
- **Interface localization of the new labels and copy.** The seven role labels,
  the unsupported-block copy, and the two media copy strings are English and
  carry the lesson's document language. Every capability profile's
  `known_limits` says so. **Owner: whichever phase introduces an interface
  language setting.**

### Phase 17A CSS handoffs

Every one of these is a class name Phase 16A introduced with **no CSS rule**,
deliberately, because no visual decision is made anywhere in Phase 16A:

- `.capability-static`, from plan 16A-04, reused by 16A-06's activity fallback.
- `.media`, `.media-unavailable`, and `.media-remote`, from plan 16A-05.
- `.callout-unsupported`, from plan 16A-03.
- The seven new `callout-<slug>` classes, from plan 16A-03.
- `.stage` and its `data-stage` and `data-stage-open` attributes, from plan
  16A-02's guided mode.
- `data-required="1"`, from plan 16A-03. Nothing reads it in this phase; it
  exists so a guided-mode stager, an accessibility review, and 17A's visual
  system have a hook already carrying the author's intent.
- Font coverage for CJK and Arabic, from plan 16A-08. The fixtures prove the
  bytes survive; whether the glyphs render is a font-stack question.
- Layout of an unbroken 318-character token, from plan 16A-08.

### Narrow spots recorded rather than fixed

- **`dir="auto"` is not emitted on `<th>` cells**, only on `<p>`, `<li>`,
  `<td>`, `<figcaption>`, and callout bodies. A header cell in a
  mixed-direction table resolves from the document direction.
- **A `[MEDIA:]` reference in the lesson intro, above the first `###` heading,
  renders nothing**, because `lesson_page` renders one section per heading and
  does not render the intro. Pre-16A behavior, unchanged.
- **`> [!KEY!]` renders the generic key callout rather than the index card.**
  No content uses it and no acceptance criterion covers it.
- **An activity's `stimulus` column is free prose resolved against nothing.**
- **An activity's `objective` column is not namespace-checked**, because the
  shipped `item.objective_unnamespaced` rule exposes no reusable helper and
  plan 16A-06 chose not to write a second copy.
- **`compose_outline`'s graph path is exercised by no fixture.** The corpus has
  lessons, not courses.
- **No composed output-mode record reaches a surface.** Both composers return
  dicts; nothing renders them.

## 6. What this report is not

This report records that the machine is green and what it measured. It does
**not** record that the contract is legible or honest. Whether a capability
profile's `known_limits` names the limitation a reader would actually hit,
whether a backburner trigger is a condition someone could test, whether the
three copy strings make sense to a learner, and whether the seven role labels
mean in English what the roles are for are judgments a test cannot make.

That judgment is `16A-REVIEW.md`'s, and it is a human's. An agent never signs
its own contract.
