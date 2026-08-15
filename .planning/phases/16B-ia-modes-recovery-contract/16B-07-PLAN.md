---
phase: 16B-ia-modes-recovery-contract
plan: 07
type: execute
wave: 7
depends_on: ["16B-06"]
files_modified:
  - surfaces/ia.py
  - surfaces/theme.py
  - surfaces/daemon.py
  - tests/mode_layer_roundtrip.py
  - .planning/phases/16B-ia-modes-recovery-contract/16B-DECISIONS.md
autonomous: true
requirements: [APP-03]
estimate:
  tokens: 68000
  raw_tokens: 68000
  tasks: 3
  confidence: low
must_haves:
  truths:
    - "The seven mode layers each name their controller and never collapse into one settings pile: learner preference, author or course strategy, objective constraint, accommodation override, instructor policy, runtime authority, and system safety exist as seven ordered entries, each carrying its controller and one example, exposed as data rather than as prose."
    - "The two fixed layers are rendered read-only and never as a toggle: the settings surface shows runtime authority and system safety under the exact heading 'Always fixed by itembank', so a learner sees why a control is absent rather than wondering if it is missing."
    - "A conflict resolves toward the higher layer and says so in one exact sentence: mode_layer_resolve returns the request from the highest-authority layer present, and the copy is '{Setting name} is set by {higher layer name} for this course and can't be changed here.' with both fields substituted."
    - "The conflict fixture proves one real case end to end: a learner-preference value contradicted by instructor policy resolves toward instructor policy and renders that exact sentence, which is the fixture 16B-RESEARCH.md recommends and the shape 16C's STRATEGY-02 fixture reuses rather than duplicates."
    - "A learner preference can never win over runtime authority or system safety: for every setting name, a request at either fixed layer wins over every request at any lower layer, asserted across the whole seven-layer matrix rather than spot-checked."
    - "16B ships the pure precedence function over an explicitly supplied mapping and no live-state collector: mode_layer_resolve reads only its arguments, imports no strategy, accommodation, or instructor record, and touches no file, so the composed resolver reading live state stays Phase 16C's work under D8."
    - "Every existing caller of theme_page renders byte-identically: the new sections argument defaults to the empty string and the shipped settings page's bytes are unchanged when it is omitted, proven by a SHA-256 comparison rather than by inspection."
  prohibitions:
    - statement: "A learner preference, an accommodation, an author strategy, or an instructor policy must never override runtime authority or system safety; scoring, keyed disclosure, retries, and the formal-test pause are fixed during a sitting and are not user-configurable."
      status: kept
      verification: flagged-unverified
    - statement: "A fixed layer must not be rendered as a toggle, a checkbox, or an editable field, because an affordance that cannot take effect is a false statement about who decides."
      status: kept
      verification: flagged-unverified
    - statement: "A model must not write a score, an evidence event, or a disclosure decision; the mode-layer table names the runtime as the controller of those and this phase adds no path around it."
      status: kept
      verification: flagged-unverified
    - statement: "The seven layers must not be collapsed into one settings pile; a preference and a policy that happen to share a name are two records with two controllers, and merging them destroys the authority information the table exists to carry."
      status: kept
      verification: flagged-unverified
  artifacts:
    - "surfaces/ia.py gains MODE_LAYER_ROWS, MODE_LAYER_FIXED_HEADING, MODE_LAYER_CONFLICT_TEMPLATE, mode_layer_rows, mode_layer_conflict_copy, and mode_layer_resolve"
    - "surfaces/theme.py's theme_page gains a sections keyword defaulting to the empty string"
    - "surfaces/daemon.py's handle_settings_get passes the rendered fixed-layer section into theme_page"
    - "tests/mode_layer_roundtrip.py with check_layer_table_shape, check_instructor_beats_preference, check_fixed_layers_always_win, check_fixed_rows_are_read_only, and check_theme_page_unchanged_by_default"
    - "16B-DECISIONS.md gains the dated D-16B-12 scope line separating 16B's pure function from 16C's live-state collector"
  key_links:
    - "mode_layer_resolve must take the whole request mapping as an argument and read nothing else. The moment it imports a strategy registry or reads an instructor record it becomes the composed resolver D8 assigns to Phase 16C, and the two phases then own two implementations of one precedence contract."
    - "theme_page's new argument must default to the empty string and be appended inside the existing main element, or every shipped caller's bytes change and tests/theme_roundtrip.py fails for a reason that has nothing to do with mode layers. The byte-identity check is what makes that failure impossible to miss."
    - "The conflict sentence's two substitutions are the display name of the setting and the display name of the winning layer, not their internal keys. Substituting the key would surface instructor_policy to a learner, which is the wrong register and is not what the locked copy says."
    - "MODE_LAYERS is already a tuple in surfaces/ia.py from plan 16B-02 and is the single ordering source. MODE_LAYER_ROWS must be built over it rather than restating the order, or two orderings exist and the higher-authority-last rule can drift between them."
---

<objective>
Make the seven-layer mode contract a thing the code can read and the settings
page can show, without building the enforcement composition that belongs to the
next subphase.

The ROADMAP's Phase 16B goal states that "the mode layering from synthesis
section 8 is contracted so learner preferences, author strategies, objective
constraints, accommodation overrides, instructor policy, fixed runtime
authority, and fixed system safety each name their controller and never collapse
into one settings pile".

`16B-UI-SPEC.md`'s Mode-Layer Precedence Contract names 16B's concrete
deliverable in four numbered points and its Decision D8 draws the boundary: 16B
documents the table, exposes the configurable layers as settings, renders the
fixed layers read-only, and ships one fixture proving a conflict resolves toward
the higher layer. The composed resolver that reads every layer's live state is
Phase 16C's, because 16C owns the strategy registry the objective-constraint and
author-strategy layers actually read from.

The line this plan draws, and Task 1 records as `D-16B-12`: 16B ships a **pure
precedence function over an explicitly supplied mapping**, which is the shared
primitive both phases need. 16C ships the **collector** that populates that
mapping from live strategy, accommodation, and instructor records. Two functions,
one precedence rule, no duplication.

Decisions already made, cited, and never re-derived here:

- **`16B-DECISIONS.md` `## D8`**: full precedence resolution composing every
  layer's live state is out of 16B's scope and belongs to Phase 16C.
- **`16B-UI-SPEC.md` Mode-Layer Precedence Contract**, the seven-row table with
  its controller and example columns, the exact conflict sentence, and the
  read-only rendering requirement, all binding verbatim.
- **`16B-UI-SPEC.md` Settings Expansion Contract**, its closing paragraph: the
  settings panel also renders the runtime-authority and system-safety rows
  read-only, labelled `Always fixed by itembank`.
- **`16B-RESEARCH.md` Don't Hand-Roll**, the "Mode/feedback authority for a
  sitting" row: the settings and preference layer sits below runtime authority
  in the precedence order and never overrides it.
- **`PLANNING-DIRECTIVES.md` section 4**, non-negotiable number 1: the runtime
  owns correctness, session state, evidence, and disclosure of keyed assessment
  content.

Purpose: make authority visible and machine-readable, and make the one thing a
learner most needs to understand, why a control is not there, say itself.
Output: one seven-row table, one pure precedence function, one settings section,
one fixture.
</objective>

<context>
@.planning/phases/16B-ia-modes-recovery-contract/16B-DECISIONS.md
@.planning/phases/16B-ia-modes-recovery-contract/16B-UI-SPEC.md
@.planning/phases/16B-ia-modes-recovery-contract/16B-RESEARCH.md
@.planning/REQUIREMENTS.md
@.planning/PLANNING-DIRECTIVES.md
@surfaces/ia.py
@surfaces/theme.py
@surfaces/daemon.py
@surfaces/presentation.py
@tests/theme_roundtrip.py
</context>

## Artifacts this phase produces (plan 16B-07 share)

New symbols introduced by this plan, and by nothing earlier:

- `surfaces/ia.py`: `MODE_LAYER_ROWS`, `MODE_LAYER_FIXED_HEADING`,
  `MODE_LAYER_CONFLICT_TEMPLATE`, `mode_layer_rows`,
  `mode_layer_conflict_copy`, `mode_layer_resolve`.
- `surfaces/theme.py`: `theme_page`'s new `sections` keyword argument.
- `surfaces/daemon.py`: the fixed-layer section rendering inside
  `handle_settings_get`.
- `tests/mode_layer_roundtrip.py` (whole file) and on it:
  `check_layer_table_shape`, `check_instructor_beats_preference`,
  `check_fixed_layers_always_win`, `check_fixed_rows_are_read_only`,
  `check_theme_page_unchanged_by_default`, and `main`.
- `16B-DECISIONS.md`: the heading `## D-16B-12. What 16B ships of the mode-layer
  contract and what 16C ships`.

The phase-wide symbol union is repeated in `16B-01-PLAN.md`.

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: the seven-layer table and the pure precedence function</name>
  <files>surfaces/ia.py, tests/mode_layer_roundtrip.py, .planning/phases/16B-ia-modes-recovery-contract/16B-DECISIONS.md</files>
  <behavior>
    - `mode_layer_rows()` returns seven dicts in `MODE_LAYERS` order, each with
      the keys `layer`, `label`, `controller`, `example`, and `fixed`.
    - Exactly two rows have `fixed` True, and they are the last two.
    - `mode_layer_resolve("Timed test mode", {"learner_preference": "off",
      "instructor_policy": "on"})` returns
      `{"value": "on", "winning_layer": "instructor_policy", "conflict": True,
      "copy": "Timed test mode is set by your instructor's policy and can't be changed here."}`
    - `mode_layer_resolve("Reader view", {"learner_preference": "guided"})`
      returns `conflict` False, `winning_layer` `"learner_preference"`, and
      `copy` the empty string.
    - `mode_layer_resolve("Anything", {})` returns `value` None,
      `winning_layer` None, `conflict` False, `copy` the empty string, and
      raises nothing.
    - `mode_layer_resolve` with a key that is not a member of `MODE_LAYERS`
      raises `ValueError` naming the unknown layer, because silently ignoring an
      unknown layer would let a caller believe a request was considered.
  </behavior>
  <read_first>
- `surfaces/ia.py` in full as it stands after plan 16B-05, in particular
  `MODE_LAYERS` and `MODE_LAYERS_FIXED` from plan 16B-02.
- `.planning/phases/16B-ia-modes-recovery-contract/16B-UI-SPEC.md`, the
  "Mode-Layer Precedence Contract" section in full: the seven-row table's
  Controller and Example columns, numbered point 2's exact conflict sentence and
  its worked example, and numbered point 4's scope boundary.
- `.planning/phases/16B-ia-modes-recovery-contract/16B-DECISIONS.md`, `## D8`.
- `tests/evidence_roundtrip.py` lines 1 to 40, for the direct-execution test
  shell and the local `fail` helper.
  </read_first>
  <action>
1. Add `MODE_LAYER_ROWS` to `surfaces/ia.py`, a tuple of seven dicts built in
   `MODE_LAYERS` order, each with the keys `layer`, `label`, `controller`,
   `example`, and `fixed`. Transcribe the label, controller, and example from
   the UI-SPEC table:

   - `learner_preference`: label `Learner preference`; controller
     `You, reversible at any safe transition`; example
     `Reader or guided view, allowed note strategy, choose another next action`.
   - `author_strategy`: label `Author or course strategy`; controller
     `The course builder, within the registered catalog`; example
     `Authored sequence, required artifact, direct-reading treatment`.
   - `objective_constraint`: label `Objective constraint`; controller
     `The objective and blueprint authority`; example
     `Cognitive demand, required construct, permitted evidence`.
   - `accommodation_override`: label `Accommodation override`; controller
     `Your stated need, or the assigning authority`; example
     `Equivalent input or output, pace, reduced motion`.
   - `instructor_policy`: label `Instructor policy`; controller
     `The assigning authority for a bounded course`; example
     `Required path, deadline, formal completion predicate`.
   - `runtime_authority`: label `Runtime authority`; controller
     `Fixed by itembank, never configurable during a sitting`; example
     `Scoring, keyed disclosure, retries, formal-test pause`.
   - `system_safety`: label `System safety`; controller `Fixed by itembank`;
     example `Permission scope, rights and egress checks, no authored-script authority`.

   `fixed` is True for exactly the two members of `MODE_LAYERS_FIXED` and False
   for the other five. Build the tuple by iterating `MODE_LAYERS` rather than by
   restating the order, so one ordering exists.

2. Add:

```
MODE_LAYER_FIXED_HEADING = "Always fixed by itembank"
MODE_LAYER_CONFLICT_TEMPLATE = "{setting} is set by {layer} for this course and can't be changed here."
```

   With a comment stating that `{layer}` is substituted with a display phrase
   rather than an internal key, and giving the UI-SPEC's own worked example
   verbatim: `Timed test mode is set by your instructor's policy and can't be
   changed here.`

3. Add `MODE_LAYER_DISPLAY_PHRASES`, a dict over `MODE_LAYERS` giving the phrase
   that reads correctly inside that sentence:
   `learner_preference` to `your own preference`; `author_strategy` to
   `this course's design`; `objective_constraint` to `this objective's
   requirements`; `accommodation_override` to `your accommodation settings`;
   `instructor_policy` to `your instructor's policy`; `runtime_authority` to
   `itembank's assessment rules`; `system_safety` to `itembank's safety rules`.

4. Add `def mode_layer_rows():` returning `MODE_LAYER_ROWS` as a list of shallow
   copies, so a caller cannot mutate the module constant.

5. Add `def mode_layer_conflict_copy(setting_name, layer):` returning
   `MODE_LAYER_CONFLICT_TEMPLATE.format(setting=setting_name,
   layer=MODE_LAYER_DISPLAY_PHRASES[layer])`, raising `KeyError` for an unknown
   layer.

6. Add `def mode_layer_resolve(setting_name, requests):` with a docstring
   stating in its first paragraph: that it is the pure half of the mode-layer
   contract; that it reads only its two arguments, imports no strategy,
   accommodation, or instructor record, and touches no file; and that the
   collector which populates `requests` from live state is Phase 16C's under
   `D8`, so there is one precedence rule and not two.

   Behavior, exactly:
   - Raise `ValueError("unknown mode layer: %r" % key)` for any key of
     `requests` that is not a member of `MODE_LAYERS`.
   - The winning layer is the member of `MODE_LAYERS` with the highest index
     that appears in `requests`.
   - `conflict` is True when `requests` has two or more keys and the winning
     layer is not the single lowest-indexed key present; more precisely, True
     when at least one lower-indexed layer also supplied a request whose value
     differs from the winning value.
   - `copy` is `mode_layer_conflict_copy(setting_name, winning_layer)` when
     `conflict` is True, else the empty string.
   - Return `{"value": ..., "winning_layer": ..., "conflict": ..., "copy": ...}`.
   - With an empty mapping, return `value` None, `winning_layer` None,
     `conflict` False, `copy` empty, and raise nothing.

7. Append `## D-16B-12. What 16B ships of the mode-layer contract and what 16C
   ships` to `16B-DECISIONS.md`, recording in one paragraph: that 16B ships
   `MODE_LAYER_ROWS`, the read-only settings rendering, and the pure
   `mode_layer_resolve` over an explicitly supplied mapping; that 16C ships the
   collector that populates that mapping from live strategy, accommodation, and
   instructor records under `STRATEGY-02`; and that the fixture shape is shared
   rather than duplicated.

8. Create `tests/mode_layer_roundtrip.py` following the shipped
   direct-execution convention, with its own local `fail(msg)`. Add
   `check_layer_table_shape()` asserting:
   - `len(ia.MODE_LAYER_ROWS)` is 7 and their `layer` values equal
     `list(ia.MODE_LAYERS)` exactly.
   - Exactly two rows have `fixed` True and they are the final two.
   - Every row's `label`, `controller`, and `example` is a non-empty string, and
     no two rows share a `label`.
   - `mode_layer_rows()` returns copies: mutating a returned dict does not
     change `MODE_LAYER_ROWS`.

   Add `check_instructor_beats_preference()` and
   `check_fixed_layers_always_win()` asserting every behavior in this task's
   `<behavior>` block, plus the whole-matrix rule: for every one of the twenty-one
   ordered pairs of distinct layers, supplying two differing values resolves to
   the higher-indexed layer, and in particular every pair whose higher member is
   `runtime_authority` or `system_safety` resolves to that fixed layer.

   Add `main()` printing `"MODE LAYERS: 3 passed, 0 failed"`, guarded by
   `if __name__ == "__main__": sys.exit(main())`.

9. Run:

```
python tests/mode_layer_roundtrip.py
python -c "import sys; sys.path.insert(0,'.'); from surfaces import ia; print(len(ia.MODE_LAYER_ROWS), sum(1 for r in ia.MODE_LAYER_ROWS if r['fixed'])); print(ia.mode_layer_resolve('Timed test mode', {'learner_preference':'off','instructor_policy':'on'})['copy'])"
```

   Expected: exit 0, then `7 2`, then exactly
   `Timed test mode is set by your instructor's policy and can't be changed here.`

   No em dash characters in any file this task writes.
  </action>
  <verify>
  <automated>python tests/mode_layer_roundtrip.py</automated>
Expected: final line `MODE LAYERS: 3 passed, 0 failed`, exit 0. The degraded
state this task proves is the empty-request case: `mode_layer_resolve` with no
requests returns a fully-shaped result with `value` None and raises nothing,
rather than raising or inventing a default.
  </verify>
  <acceptance_criteria>
- `python tests/mode_layer_roundtrip.py` exits 0 with final line
  `MODE LAYERS: 3 passed, 0 failed`.
- `len(ia.MODE_LAYER_ROWS)` is `7` and exactly the last two have `fixed` True.
- `[r["layer"] for r in ia.MODE_LAYER_ROWS] == list(ia.MODE_LAYERS)`.
- `ia.mode_layer_resolve("Timed test mode", {"learner_preference": "off",
  "instructor_policy": "on"})["copy"]` equals exactly
  `Timed test mode is set by your instructor's policy and can't be changed here.`
- All twenty-one ordered layer pairs resolve to the higher-indexed layer.
- `ia.mode_layer_resolve("x", {"not_a_layer": 1})` raises `ValueError` naming
  `not_a_layer`.
- `mode_layer_resolve`'s source contains no `import` statement and no `open(`
  call, asserted by reading `inspect.getsource(ia.mode_layer_resolve)`.
- `16B-DECISIONS.md` contains the literal heading `## D-16B-12.`
- No file this task writes contains an em dash character, verified with the
  `chr(0x2014)` form.
  </acceptance_criteria>
  <reversibility rating="costly">`MODE_LAYER_ROWS` and the conflict sentence
  become the vocabulary Phase 16C's collector and Phase 17A's rendering both
  read. The seven layer names were already fixed by `MODE_LAYERS` in plan
  16B-02 and by the LOCKED synthesis table, so only the display phrases are new
  here.</reversibility>
  <done>Seven layers exist as data with their controllers, a conflict resolves
  upward, and the function that decides it reads nothing but its
  arguments.</done>
</task>

<task type="auto">
  <name>Task 2: the settings page renders the fixed layers read-only</name>
  <files>surfaces/theme.py, surfaces/daemon.py, tests/mode_layer_roundtrip.py</files>
  <read_first>
- `surfaces/theme.py`, `theme_page` at line 415 in full, including its docstring
  and the exact place its sections are assembled into the returned document.
- `surfaces/daemon.py`, `handle_settings_get` at line 1118 in full.
- `.planning/phases/16B-ia-modes-recovery-contract/16B-UI-SPEC.md`, the Settings
  Expansion Contract's closing paragraph naming the read-only rows and the exact
  heading `Always fixed by itembank`.
- `surfaces/presentation.py`, `details_section` and `esc`.
- `tests/theme_roundtrip.py` in full, so the existing assertions on the settings
  page are known before it is extended.
  </read_first>
  <action>
1. Add one keyword argument to `theme_page`:

```
def theme_page(config, sections=""):
```

   Its default is the empty string. The value is inserted verbatim immediately
   before the closing of the page's `main` element and nowhere else. Extend the
   docstring with one sentence stating that `sections` is additive extra markup
   appended after the Theme section, that it defaults to empty so every existing
   caller renders byte-identically, and that it is HTML the caller has already
   escaped.

2. Add a fixed-layer renderer. Because `surfaces/theme.py` must not grow a
   dependency on `surfaces/ia.py` for one string, build the markup in
   `surfaces/daemon.py` inside `handle_settings_get`:

   - `rows = [r for r in ia.mode_layer_rows() if r["fixed"]]`.
   - Build one section: an `<h2>` carrying
     `ia.MODE_LAYER_FIXED_HEADING`, then one `<div class="fixed-layer">` per
     row containing the escaped `label`, the escaped `controller`, and the
     escaped `example`.
   - Render it inside `presentation.details_section` with the summary
     `Always fixed by itembank` so it is a native disclosure and not a new
     widget.
   - Pass it as `theme.theme_page(cfg, sections=that_markup)`.

   The section contains no `<input>`, no `<select>`, no `<button>`, no
   `<textarea>`, no `contenteditable` attribute, and no form of any kind. State
   that in a comment: a fixed layer rendered as a toggle would be an affordance
   that cannot take effect.

3. Also render, in the same section, one line per **configurable** layer naming
   its controller, so the seven layers are visible as seven and not as two. Use
   the same non-interactive markup. The five configurable rows are informational
   text here; the actual settings controls for the learner-preference and
   accommodation layers are the four groups plan 16B-06 added and the shipped
   theme control, and this section links to neither, it only names who decides.

4. Add `check_fixed_rows_are_read_only()` to `tests/mode_layer_roundtrip.py`. It
   starts a real daemon, requests `GET /settings`, and asserts:
   - Status 200.
   - The body contains the exact heading text `Always fixed by itembank`.
   - The body contains both fixed rows' labels, `Runtime authority` and
     `System safety`, and both their controller strings.
   - The body contains all five configurable layer labels too, so all seven
     appear.
   - Within the substring bounded by the `details-section` carrying the
     `Always fixed by itembank` summary and its closing tag, none of `<input`,
     `<select`, `<button`, `<textarea`, `contenteditable`, or `<form` appears.
   - The shipped Theme section is still present, asserted by one string
     `tests/theme_roundtrip.py` already relies on.

5. Add `check_theme_page_unchanged_by_default()`. It calls
   `theme.theme_page(cfg)` with no `sections` argument and asserts its SHA-256
   equals the SHA-256 of the same call recorded before this task's change. Take
   that baseline first, before editing `theme.py`, with:

```
python -c "import sys,hashlib; sys.path.insert(0,'.'); from surfaces import theme, settings; print(hashlib.sha256(theme.theme_page(settings.load_settings('.')).encode('utf-8')).hexdigest())"
```

   Record the printed value in the plan summary and write it into the test as a
   literal expected hash with a comment naming the date it was taken and the
   command that produced it. If the value later changes for an unrelated reason,
   the test names the drift instead of hiding it.

6. Update `main()` to run five checks and print
   `"MODE LAYERS: 5 passed, 0 failed"`. Run:

```
python tests/mode_layer_roundtrip.py
python tests/theme_roundtrip.py
python tests/daemon_roundtrip.py
```

   Expected: exit 0 from all three.

   No em dash characters in any file this task writes.
  </action>
  <verify>
  <automated>python tests/mode_layer_roundtrip.py && python tests/theme_roundtrip.py</automated>
Expected: `MODE LAYERS: 5 passed, 0 failed` and exit 0, then exit 0. The
degraded state this task proves is the untouched default: `theme_page(cfg)` with
no `sections` argument produces the same bytes it produced before this change,
so no shipped caller moved.
  </verify>
  <acceptance_criteria>
- `python tests/mode_layer_roundtrip.py` exits 0 with final line
  `MODE LAYERS: 5 passed, 0 failed`.
- `python tests/theme_roundtrip.py` and `python tests/daemon_roundtrip.py` both
  exit 0.
- `theme.theme_page(cfg)` with no `sections` argument hashes to the literal
  value recorded before the edit, asserted in the test.
- `GET /settings` returns 200 and contains `Always fixed by itembank`,
  `Runtime authority`, `System safety`, and all five configurable layer labels.
- The fixed-layer disclosure region contains none of `<input`, `<select`,
  `<button`, `<textarea`, `contenteditable`, `<form`.
- `surfaces/theme.py` gained exactly one keyword argument and no import of
  `surfaces.ia`, asserted by `git diff surfaces/theme.py`.
- No file this task writes contains an em dash character, verified with the
  `chr(0x2014)` form.
  </acceptance_criteria>
  <reversibility rating="reversible">One defaulted keyword argument and one
  server-rendered read-only section. Removing the argument restores the previous
  page exactly.</reversibility>
  <done>A learner opening settings can see all seven layers, see which two are
  fixed, and find no control that cannot take effect.</done>
</task>

<task type="auto">
  <name>Task 3: the conflict fixture, shaped so 16C reuses it</name>
  <files>tests/mode_layer_roundtrip.py</files>
  <read_first>
- `.planning/REQUIREMENTS.md`, `STRATEGY-02` in full, including its Fixture
  sentence, so this fixture's shape is the one 16C extends rather than a
  different one.
- `.planning/phases/16B-ia-modes-recovery-contract/16B-RESEARCH.md`, Open
  Question 3 in full, including its recommendation.
- `.planning/phases/16B-ia-modes-recovery-contract/16B-DECISIONS.md`, `## D8`
  and `## D-16B-12`.
- `tests/mode_layer_roundtrip.py` as it stands after Task 2.
  </read_first>
  <action>
1. Add `check_conflict_fixture()` to `tests/mode_layer_roundtrip.py`, written so
   a 16C plan can add rows to its table rather than write a second fixture. It
   is driven by one module-level list `CONFLICT_CASES`, each entry a tuple of
   `(setting_name, requests_dict, expected_winning_layer, expected_value)`,
   with these six rows and a comment above the list stating that Phase 16C
   appends rows here rather than creating a second fixture:

   - `("Timed test mode", {"learner_preference": "off", "instructor_policy": "on"}, "instructor_policy", "on")`
   - `("Reader view", {"learner_preference": "guided", "author_strategy": "continuous"}, "author_strategy", "continuous")`
   - `("Retry after a wrong answer", {"learner_preference": "unlimited", "runtime_authority": "one"}, "runtime_authority", "one")`
   - `("Reduced motion", {"learner_preference": "off", "accommodation_override": "on"}, "accommodation_override", "on")`
   - `("Show the answer key now", {"learner_preference": "yes", "instructor_policy": "yes", "runtime_authority": "no"}, "runtime_authority", "no")`
   - `("Read outside the approved roots", {"learner_preference": "yes", "system_safety": "no"}, "system_safety", "no")`

   For each row assert: `mode_layer_resolve` returns the expected winning layer
   and value; `conflict` is True; and `copy` equals
   `ia.mode_layer_conflict_copy(setting_name, expected_winning_layer)` exactly,
   which is also asserted to contain the setting name and the winning layer's
   display phrase and to contain neither the internal layer key nor an
   underscore.

2. Assert the two authority rows explicitly and by name, because they are the
   non-negotiable half: row three, row five, and row six each show a learner
   preference losing to a fixed layer, and the test's failure message names
   non-negotiable number 1 when any of them does not.

3. Assert the scope boundary structurally: `inspect.getsource(ia)` contains no
   function that both calls `mode_layer_resolve` and reads a file, and
   `surfaces/ia.py` defines no name matching `collect_mode_layers`,
   `live_mode_state`, or `mode_layer_state`. A collector appearing in 16B would
   mean the phase built 16C's half after all, and the check names D8 in its
   failure message.

4. Update `main()` to run six checks and print
   `"MODE LAYERS: 6 passed, 0 failed"`. Run the full suite and the guard:

```
python tests/mode_layer_roundtrip.py
for t in tests/*.py; do python "$t" || exit 1; done
python itembank.py guard .
```

   Expected: `MODE LAYERS: 6 passed, 0 failed` and exit 0; exit 0;
   `0 offending files`.

   No em dash characters in any file this task writes.
  </action>
  <verify>
  <automated>python tests/mode_layer_roundtrip.py</automated>
Expected: final line `MODE LAYERS: 6 passed, 0 failed`, exit 0. The degraded
state this task proves is the authority floor: three of the six cases are a
learner preference losing to a fixed layer, and each names non-negotiable number
1 in its failure message.
  </verify>
  <acceptance_criteria>
- `python tests/mode_layer_roundtrip.py` exits 0 with final line
  `MODE LAYERS: 6 passed, 0 failed`.
- `CONFLICT_CASES` has exactly six rows and carries the comment naming Phase 16C
  as the appender.
- Every case's `copy` equals `mode_layer_conflict_copy(setting, winner)` and
  contains no underscore and no internal layer key.
- Cases three, five, and six each resolve to a fixed layer over a learner
  preference, and their failure messages name non-negotiable number 1.
- `surfaces/ia.py` defines none of `collect_mode_layers`, `live_mode_state`,
  `mode_layer_state`.
- `for t in tests/*.py; do python "$t" || exit 1; done` exits 0 and
  `python itembank.py guard .` reports `0 offending files`.
- No file this task writes contains an em dash character, verified with the
  `chr(0x2014)` form.
  </acceptance_criteria>
  <reversibility rating="reversible">Test coverage only.</reversibility>
  <done>One conflict per interesting pair resolves upward with the exact locked
  sentence, a learner preference never beats a fixed layer, and 16C's collector
  is provably absent from this phase.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| learner preference to assessment behavior | A preference is user input that must never reach scoring, disclosure, retries, or the formal-test pause. |
| settings page markup to authority claim | An interactive control implies the value takes effect. |
| precedence function to live state | A pure function that starts reading records becomes an enforcement mechanism nobody reviewed. |
| new page section to shipped page bytes | An additive section can silently change a shipped surface. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-16B-07-01 | Elevation of Privilege | a learner preference overriding runtime authority or system safety | critical | mitigate | `mode_layer_resolve` resolves by `MODE_LAYERS` index with the two fixed layers last, and `check_fixed_layers_always_win` asserts all twenty-one ordered pairs plus three named authority cases whose failure messages cite non-negotiable number 1. |
| T-16B-07-02 | Spoofing | a fixed layer rendered as a toggle, implying a learner can change it | high | mitigate | The fixed-layer section contains no form control at all, asserted by scanning the rendered region for `<input`, `<select`, `<button`, `<textarea`, `contenteditable`, and `<form`. |
| T-16B-07-03 | Elevation of Privilege | a live-state collector appearing in 16B and becoming a second precedence implementation | high | mitigate | `mode_layer_resolve` reads only its arguments, asserted by scanning its source for `import` and `open(`; a structural check asserts no collector-shaped name exists in `surfaces/ia.py`, naming D8 on failure. |
| T-16B-07-04 | Tampering | script injection through a layer label or controller string into the settings page | medium | mitigate | Every rendered value comes from the module-level `MODE_LAYER_ROWS` constant, never from user input, and is still emitted through `presentation.esc`. |
| T-16B-07-05 | Tampering | the shipped settings page changing bytes for an unrelated reason | medium | mitigate | `sections` defaults to the empty string and `check_theme_page_unchanged_by_default` asserts the no-argument call hashes to a value recorded before the edit. |
| T-16B-07-06 | Repudiation | a conflict message naming an internal key rather than a phrase a learner understands | low | mitigate | `MODE_LAYER_DISPLAY_PHRASES` supplies the substitution and the fixture asserts the rendered copy contains no underscore and no internal layer key. |
| T-16B-07-07 | Tampering | supply chain: a third-party dependency introduced by this plan | high | mitigate | None is added; every change is standard library only. Per `PLANNING-DIRECTIVES.md` section 4a the absence of dependencies is explicitly not the mitigation: the mitigation is that any dependency ever added here is vendored at a pinned version with a recorded checksum and a named license review, following the KaTeX precedent in `09-03-PLAN.md`. |
</threat_model>

<out_of_scope>
Refused by this plan, by name:

- **No live-state collector.** No function reads a strategy registry, an
  accommodation record, an instructor policy record, or a course record to build
  the `requests` mapping. That is Phase 16C's under `D8` and `D-16B-12`, and a
  structural check asserts its absence.
- **No enforcement wiring.** No shipped code path calls `mode_layer_resolve`
  during a sitting, a render, or a scoring decision in this phase. It is a
  primitive with tests and a settings rendering, and nothing else consumes it.
- No new settings key for any layer. The four groups plan 16B-06 added are the
  phase's settings growth.
- No change to `runtime.py`, `evidence.py`, or `model.py`. The runtime-authority
  layer describes what those modules already enforce and adds nothing to them.
- No accommodation behavior. `accessibility.reduced_motion` is declared by plan
  16B-06 and enforced by nothing in this phase; naming its controller is not
  honoring it.
- No new visual constant, no CSS rule, and no widget. The fixed-layer section is
  a native `details` disclosure through the shipped helper.
</out_of_scope>

<flagged_assumptions>
- **`MODE_LAYER_DISPLAY_PHRASES` is this plan's own wording.** The UI-SPEC locks
  the sentence template and gives one worked substitution
  (`your instructor's policy`); the other six phrases are written here to read
  correctly in the same sentence. They are display text with no behavior behind
  them, so a reviewer may reword any of them without touching a test that
  asserts behavior, but the fixture asserts the rendered sentence matches
  `mode_layer_conflict_copy` exactly, so a reword must change both.

- **The `conflict` definition treats two identical values at two layers as no
  conflict.** A learner preference of `on` under an instructor policy of `on` is
  not a case where anything was overridden, so showing the sentence would tell a
  learner a control was taken away when nothing was. If a reviewer prefers the
  stricter reading, the change is one line in `mode_layer_resolve` and one row
  in `CONFLICT_CASES`.

- **No shipped code path calls `mode_layer_resolve` in this phase.** That is
  deliberate and is what `D8` asks for, but it means the function's correctness
  is proven only by its own fixture until 16C wires it. The 16B freeze record
  states that explicitly rather than implying the contract is enforced.
</flagged_assumptions>

<summary_obligations>
`16B-07-SUMMARY.md` records: the final line of every verify command; the
`theme_page(cfg)` SHA-256 recorded before the edit and re-verified after,
side by side; the exact rendered conflict sentence for all six `CONFLICT_CASES`
rows; confirmation that the fixed-layer region contains no form control, with
the scanned region quoted; the recorded `## D-16B-12` text; the confirmation
that no collector-shaped name exists in `surfaces/ia.py`; which truth was
verified by which command with its actual stdout; and any deviation from this
plan with its reason.
</summary_obligations>

<output>
Create
`.planning/phases/16B-ia-modes-recovery-contract/16B-07-SUMMARY.md`
when done.
</output>
