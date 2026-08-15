---
phase: 16A-semantic-capability-activity-contract
plan: 04
type: execute
wave: 4
depends_on: ["16A-03"]
files_modified:
  - capabilities.py
  - schemas/capability_profile.schema.json
  - surfaces/lesson.py
  - fixtures/lesson_capability_corpus.py
  - tests/capability_stress_corpus_tracer.py
autonomous: true
requirements: [CAP-02]
estimate:
  tokens: 84000
  raw_tokens: 84000
  tasks: 3
  confidence: low
must_haves:
  truths:
    - "Every one of the fourteen roles in capabilities.SEMANTIC_ROLE_CATALOG has a capability profile carrying all six CAP-02 fields, and the registry carries exactly one entry beyond those fourteen, guided_mode, so a role with no profile is a failing assertion rather than an omission nobody notices."
    - "The shipped hover, focus, and touch glossary is catalogued as glossary_definition, which is CAP-02's own named first catalogued capability, and its profile describes the shipped behavior rather than a wished-for one."
    - "Registering a capability name that already exists raises CapabilityError naming the duplicate; the registry never silently merges two entries and never lets a later registration win (CAP-02 adjacency probe)."
    - "capabilities.profile for an unregistered name returns None, never raises and never a partial dict; capabilities.profiles over an empty registry returns an empty tuple (CAP-02 empty probe)."
    - "capabilities.profiles returns entries in registration order, which is the literal source order of the module-level dict, and two calls in the same interpreter return equal tuples (CAP-02 ordering probe)."
    - "A capability whose renderer resolves to unavailable shows its declared static instructional path, proven against shipped behavior: the inline check's no-session copy now comes from the registry instead of a string literal inside _callout_html, and the rendered bytes for a gate-less check are identical to what shipped before this plan."
    - "The capability profile is a published contract: schemas/capability_profile.schema.json validates every registry entry through the shipped schema_validate.py, using only keywords in that validator's SUPPORTED set, and a profile missing any of the six CAP-02 fields fails validation rather than passing quietly."
    - "No decorative block is required by style alone: no capability profile, lint check, or style rule added by this plan makes any block mandatory, and the tracer asserts a lesson using zero optional callouts still lints clean."
  prohibitions:
    - statement: "A capability profile must not decide keyed disclosure or settle a score; renderer availability answers whether a renderer exists, and runtime.public_item, runtime.explain_payload, and runtime.glossable remain the only answers to what a learner may see."
      status: kept
      verification: flagged-unverified
    - statement: "No style rule, capability profile, or validation check may require a decorative block; CAP-02's own clause is that no decorative block is required by style alone."
      status: kept
      verification: flagged-unverified
    - statement: "A capability whose unavailable path is undefined must not be registered; a profile with an empty offline_fallback fails validation, because a capability with no fallback fails CAP-02's Degraded clause by construction."
      status: kept
      verification: flagged-unverified
  artifacts:
    - "capabilities._CAPABILITY_PROFILES grown to exactly fifteen entries"
    - "capabilities.resolved_availability, capabilities.validate_profile, capabilities.CAPABILITY_CONTEXT_KEYS, capabilities.MEDIA_RIGHTS_STATES, capabilities.MEDIA_AVAILABILITY"
    - "schemas/capability_profile.schema.json"
    - "surfaces/lesson.py: _static_instructional_html, and _callout_html's check branch reading its copy from the registry"
    - "fixtures/lesson_capability_corpus.py gains build_unavailable_capability"
    - "tests/capability_stress_corpus_tracer.py gains scenario_capability_profiles and scenario_unavailable_renderer"
  key_links:
    - "The inline check's no-session copy is the one place the shipped renderer already implements CAP-02's Degraded clause. Moving that literal into the registry proves the contract against behavior that already exists and is already tested, rather than against machinery this phase invented. The byte-identity assertion is what makes it a proof: if the registry string differs from the shipped one by a character, tests/gate_roundtrip.py goes red."
    - "resolved_availability takes a context dict and returns a state; it reads no file, no environment variable, and no global. Availability is a fact about the caller's situation, not about the module, so a module that decided it internally would be untestable and would make a static CLI render and a served render disagree for reasons neither could inspect."
    - "The schema is validated by schema_validate.py, whose check_schema walks the whole document first and refuses any keyword outside its SUPPORTED set. A capability_profile.schema.json using a keyword outside that set is refused outright rather than partially applied, which is why the schema is written against that keyword list rather than against general JSON Schema knowledge."
    - "The registry has fifteen entries and the catalog has fourteen. The cross-check that every catalog role has a profile and that exactly one profile has no catalog role is what keeps the two lists from drifting; without it, adding a role in a later phase would leave a profile-less capability that nothing notices."
---

<objective>
Give every semantic capability the six-field support profile CAP-02 requires,
publish that profile as a validated schema, and prove the Degraded clause
against behavior the renderer already has.

CAP-02, quoted: "Each semantic capability declares an accessible-behavior,
offline-fallback, renderer-availability, version, validation, and known-limits
profile ... no decorative block is required by style alone. Owner: capability
owner via MAINT. Durable object: capability support profile. Authority:
capability registry. Degraded: an unavailable renderer shows the static
instructional path."

Two things about that requirement are easy to get wrong and are settled here.

The first is scope. `ROADMAP.md`'s Phase 16A entry states that "the shipped
hover, focus, and touch glossary definitions (RTS-05, complete) are the first
catalogued capability". A capability profile is retroactive documentation of
what already ships as much as it is a declaration about what is new, and a
profile that describes a wished-for behavior rather than the shipped one is
worse than no profile.

The second is authority. A profile sits close to disclosure without being it. A
`renderer_availability` of `available` answers "does a renderer for this exist".
It does not answer "may this learner see this", which `runtime.public_item`,
`runtime.explain_payload`, and `runtime.glossable` answer and which no other
module may. `runtime.glossable`'s own docstring states the principle: "the
runtime, not the author and not a model, decides what reaches the learner".
Plan 16A-09's adversarial suite attacks this boundary directly; this plan makes
it structural by keeping `capabilities.py` free of any import of `runtime` or
`evidence`.

The Degraded clause is proven against shipped behavior rather than against new
machinery. `surfaces/lesson.py`'s `_callout_html` already implements it once:
when a `[!CHECK: <id>]` block is rendered with no gate context, it emits the
copy `This check is available when you are reading with a session.` instead of
the live band. That is exactly "an unavailable renderer shows the static
instructional path", written before CAP-02 existed. This plan moves that literal
into the registry so there is one source of truth for it, and asserts the
rendered bytes are unchanged, which turns an existing behavior into a proof.

Decisions already made, cited, and never re-derived here:

- **`16A-DECISIONS.md` `## D-16A-2`**: which module the registry lives in. Under
  `option-a` it is the root-level `capabilities.py` plan 16A-02 created.
- **`16A-DECISIONS.md` `## D-16A-5`**:
  `RENDERER_AVAILABILITY = ("available", "degraded", "unavailable")`.
- **`16A-DECISIONS.md` `## D-16A-8`**: media rights are declared, not enforced,
  in 16A, and `MEDIA_RIGHTS_STATES` references `identity.RIGHTS_STATES` rather
  than minting a second tuple. This plan lands that constant; plan 16A-05 uses
  it.
- **`16A-PATTERNS.md`, the `schemas/capability_profile.schema.json` Pattern
  Assignment**: every schema under `schemas/` is checked by
  `schema_validate.py`'s hand-rolled subset validator, whose `SUPPORTED`
  keyword set is `type`, `properties`, `required`, `additionalProperties`,
  `enum`, `const`, `items`, `minItems`, `uniqueItems`, `minLength`, `pattern`,
  `minimum`, `maximum`, `$defs`, `$ref`, `oneOf`. A schema using anything
  outside that set is refused outright.
- **The phase-shape constraint on visual scope**: no color, spacing,
  typography, motion, or token decision anywhere in Phase 16A.

Purpose: make every capability's support, fallback, and limits inspectable.
Output: fifteen profiles, one published schema, and one degradation proven.
</objective>

<context>
@.planning/phases/16A-semantic-capability-activity-contract/16A-DECISIONS.md
@.planning/phases/16A-semantic-capability-activity-contract/16A-PRECONDITION.md
@.planning/phases/16A-semantic-capability-activity-contract/16A-RESEARCH.md
@.planning/phases/16A-semantic-capability-activity-contract/16A-PATTERNS.md
@.planning/phases/16A-semantic-capability-activity-contract/16A-VALIDATION.md
@.planning/REQUIREMENTS.md
@capabilities.py
@surfaces/lesson.py
@schema_validate.py
@schemas/visual_interaction.schema.json
@tests/capability_stress_corpus_tracer.py
</context>

## Artifacts this phase produces (plan 16A-04 share)

New symbols introduced by this plan, and by nothing earlier:

- `capabilities.CAPABILITY_CONTEXT_KEYS` (tuple constant)
- `capabilities.MEDIA_RIGHTS_STATES` and `capabilities.MEDIA_AVAILABILITY`
- `capabilities.resolved_availability`
- `capabilities.validate_profile`
- Fourteen new entries in `capabilities._CAPABILITY_PROFILES`, taking it to
  fifteen
- `schemas/capability_profile.schema.json`
- `surfaces/lesson.py`: `_static_instructional_html`
- `fixtures/lesson_capability_corpus.py`: `build_unavailable_capability`
- `tests/capability_stress_corpus_tracer.py`: `scenario_capability_profiles`,
  `scenario_unavailable_renderer`

No CLI command and no daemon route is produced by this plan.

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: the full capability registry, fifteen profiles with all six CAP-02 fields</name>
  <files>capabilities.py</files>
  <read_first>
- `.planning/REQUIREMENTS.md` `CAP-02` in full, including its Owner, Durable
  object, Authority, Degraded, and Fixture sentences.
- `.planning/ROADMAP.md`, the Phase 16A entry's final sentence naming the
  shipped glossary as the first catalogued capability.
- `capabilities.py` in full as it stands after plans 16A-02 and 16A-03, in
  particular `CAPABILITY_PROFILE_KEYS`, `RENDERER_AVAILABILITY`, the single
  seeded `callout_prerequisite` entry, and `SEMANTIC_ROLE_CATALOG`'s fourteen
  entries.
- `surfaces/lesson.py` lines 1121 to 1160, `_callout_html`, specifically the
  `slug == "check"` branch at lines 1137 to 1146 and the exact copy string at
  line 1141. That string is the `inline_check` profile's `offline_fallback` and
  must be transcribed character for character.
- `surfaces/lesson.py`'s gloss functions and the `LOADING_COPY` and
  `UNAVAILABLE_COPY` constants the `GLOSS_ENHANCEMENT_JS` block interpolates,
  for the `glossary_definition` profile's accessible-behavior and
  offline-fallback text. The reader page ships every definition, so its offline
  fallback is real and is not the fetch path's unavailable copy; describe what
  actually happens with no network.
- `runtime.py` lines 44 to 99, `public_item`, the `visual` branch, for the
  `visual_interaction` profile's known-limits.
- `runtime.py` lines 1509 to 1531, `glossable`, in full. Its docstring states
  the authority boundary this module must not cross; the module docstring cites
  it.
- `identity.py`, whichever lines define `RIGHTS_STATES`, to confirm it is a
  plain module-level tuple importable with no side effect.
  </read_first>
  <behavior>
- `len(capabilities.profiles())` is exactly `15`.
- Every entry's key set is exactly `CAPABILITY_PROFILE_KEYS`, every
  `renderer_availability` is a member of `RENDERER_AVAILABILITY`, every
  `version` is a positive integer, and every one of `accessible_behavior`,
  `offline_fallback`, `validation`, and `known_limits` is a non-empty string.
- For every entry in `SEMANTIC_ROLE_CATALOG` there is exactly one profile that
  maps to it, and exactly one profile, `guided_mode`, maps to no catalog role.
- `capabilities.profile("glossary_definition")` exists and its
  `accessible_behavior` describes the shipped hover, focus, and touch behavior.
- `capabilities.profile("inline_check")["offline_fallback"]` equals exactly the
  string `surfaces/lesson.py` emits today for a gate-less check.
- `capabilities.register` called with a name already in the registry raises
  `CapabilityError` whose message contains the duplicate name, and mutates
  nothing.
- `capabilities.profile("no_such_name")` returns `None`.
- `capabilities.profiles({})` returns an empty tuple.
- `capabilities.profiles()` called twice returns two equal tuples whose entry
  order equals the module-level dict's literal source order.
- `capabilities.resolved_availability(name, context)` returns a member of
  `RENDERER_AVAILABILITY` for any registered name and any context dict,
  including an empty one, and returns the string `unavailable` for an
  unregistered name.
- `capabilities.validate_profile(entry)` returns a list of finding strings,
  empty for a valid entry, and includes a finding naming `offline_fallback` for
  an entry whose `offline_fallback` is the empty string.
  </behavior>
  <action>
1. Grow `capabilities._CAPABILITY_PROFILES` from one entry to exactly fifteen.
   The names, in this literal source order, which is also the order
   `profiles()` returns:

   `callout_key`, `callout_warning`, `callout_prerequisite`,
   `callout_misconception`, `callout_tip`, `callout_example`,
   `callout_counterexample`, `callout_excerpt`, `glossary_definition`,
   `callout_uncertainty`, `callout_summary`, `inline_check`, `hint_ladder`,
   `visual_interaction`, `guided_mode`.

   The first fourteen are in `SEMANTIC_ROLE_CATALOG`'s order, so the two lists
   read the same way down the page. `guided_mode` is last because it is the one
   capability that is not a teaching role.

   Every entry carries all seven `CAPABILITY_PROFILE_KEYS`. Write real prose in
   each field, describing what the shipped or newly built mechanism actually
   does. Three fields have non-obvious content rules:
   - `offline_fallback` must never be the empty string. A capability with no
     fallback fails CAP-02's Degraded clause by construction, and
     `validate_profile` refuses it.
   - `validation` names the concrete check that catches a malformed use, by lint
     code where one exists, for example the sentence
     `model.lint reports an unknown callout kind as lesson.unknown_semantic.`
     A capability with no validation path says so in plain words rather than
     leaving the field vague.
   - `known_limits` states a real limitation. Do not write the word `none`.
     Every one of these fifteen has at least one: the callout labels are not
     translated, the glossary suppresses a definition that could disclose keyed
     material, the hint ladder tiers are authored rather than generated, guided
     mode does not persist reading position in this phase, and so on.

   For `inline_check`, `offline_fallback` must be exactly the string
   `surfaces/lesson.py` line 1141 emits today, transcribed character for
   character:
   `This check is available when you are reading with a session.`
   Do not paraphrase it, do not add a trailing space, and do not change its
   punctuation. Task 3 asserts the rendered bytes are unchanged, and a
   one-character difference turns that assertion red.

   For `glossary_definition`, set `version` to `1` and state in
   `accessible_behavior` that the definition is reachable by hover, by keyboard
   focus, and by touch activation, and that the reader page ships every
   definition so no network is needed. State in `known_limits` that a suppressed
   term returns a bare 404 indistinguishable from an unknown one, which is a
   real shipped behavior recorded in the Phase 03.1 decision log. Put that
   clause in one field, not both.

2. Add `CAPABILITY_CONTEXT_KEYS`, a closed tuple naming every boolean fact a
   caller may supply about its own situation. Exactly these five, in this order:
   `("serving_runtime", "gate_context", "scripting", "math_assets", "network")`.
   Each is a fact about the caller, never about the module.

3. Add `resolved_availability(name, context, registry=None)`. It is pure: no
   file read, no environment read, no global. It looks up the profile, reads its
   declared `renderer_availability` as the ceiling, and lowers it based on the
   context dict, returning the lower of the two. The lowering rules are the whole
   of this function's policy and are written here so the executor does not
   invent them:
   - `inline_check` resolves to `unavailable` when `context.get("gate_context")`
     is falsy.
   - `visual_interaction` resolves to `unavailable` when
     `context.get("scripting")` is falsy, and to `degraded` when `scripting` is
     truthy and `context.get("serving_runtime")` is falsy.
   - `glossary_definition` resolves to `degraded` when
     `context.get("scripting")` is falsy, because the shipped page still ships
     every definition inline and every panel stays reachable, so it is reduced
     but never unavailable.
   - `hint_ladder` resolves to `unavailable` when
     `context.get("serving_runtime")` is falsy.
   - `guided_mode` resolves to `available` in every context; it is server
     rendered and needs nothing.
   - Every `callout_*` capability resolves to `available` in every context; a
     labelled section needs nothing.
   - An unregistered name resolves to `unavailable`.

   An unknown key in `context` is ignored rather than refused, so a caller from a
   later phase supplying a sixth fact does not break this function.

4. Add `validate_profile(entry)`, returning a list of human-readable finding
   strings and never raising. It checks: the key set equals
   `CAPABILITY_PROFILE_KEYS`; `renderer_availability` is in
   `RENDERER_AVAILABILITY`; `version` is a positive integer; and each of
   `accessible_behavior`, `offline_fallback`, `validation`, and `known_limits`
   is a non-empty string after stripping. Each finding names the offending
   field.

5. Add `MEDIA_RIGHTS_STATES` and `MEDIA_AVAILABILITY` to `capabilities.py`, for
   plan 16A-05 to use. Under `D-16A-8`, `MEDIA_RIGHTS_STATES` is assigned from
   `identity.RIGHTS_STATES` by reference. Check `identity.py` first: if it
   imports cleanly with no side effect, use a top-level import; if it does not,
   use a function-local import inside a small module-level initialization and
   record which branch was taken in the summary. Do not retype the three state
   strings. A second tuple carrying the same members is the second rights
   vocabulary `16A-RESEARCH.md` Pitfall 4 names by name and Directive section
   4.2 forbids in spirit.

   `MEDIA_AVAILABILITY` is a new closed tuple, `("present", "missing",
   "remote")`, describing whether an asset's bytes sit beside the lesson, are
   absent, or are reachable only over a network. It is not a rights vocabulary
   and does not duplicate one.

6. Add one sentence to the module docstring stating that a profile answers
   whether a renderer exists and what a learner sees when it does not, and never
   whether a learner may see an answer, citing `runtime.glossable`'s docstring
   sentence: "the runtime, not the author and not a model, decides what reaches
   the learner". Keep `capabilities.py` free of any import of `runtime` or
   `evidence`.
  </action>
  <verify>
  <automated>python tests/capability_profile_check.py</automated>
Create `tests/capability_profile_check.py` as part of this task, following
`tests/evidence_roundtrip.py`'s convention (shebang, standard library only,
`ROOT` plus `sys.path.insert`, a local `fail(msg)`). It asserts, in this order,
each with a named failure message: fifteen profiles; every key set equals
`CAPABILITY_PROFILE_KEYS`; `validate_profile` returns empty for all fifteen;
`profile` of an unregistered name is `None`; `profiles({})` is an empty tuple;
two `profiles()` calls are equal and ordered; the fourteen catalog roles all map
to a profile and `guided_mode` is the one extra; `resolved_availability` returns
`unavailable` for `inline_check` with an empty context and `available` with
`gate_context` true; `resolved_availability` returns `unavailable` for an
unregistered name; and `register` with an existing name raises `CapabilityError`
whose message contains the duplicate name while leaving `len(profiles())` at
fifteen. It prints `capability registry ok` and exits 0 on success.
The degraded state this task must also prove is the empty-registry path: assert
`profiles({})` and `profile("callout_key", {})` return an empty tuple and `None`
rather than raising.
  </verify>
  <acceptance_criteria>
- `python tests/capability_profile_check.py` prints `capability registry ok` and
  exits 0.
- `python -c "import capabilities as C; print(len(C.profiles()), len(C.SEMANTIC_ROLE_CATALOG), C.CAPABILITY_CONTEXT_KEYS)"`
  prints exactly
  `15 14 ('serving_runtime', 'gate_context', 'scripting', 'math_assets', 'network')`.
- `python -c "import capabilities as C, identity; print(C.MEDIA_RIGHTS_STATES is identity.RIGHTS_STATES, C.MEDIA_AVAILABILITY)"`
  prints exactly `True ('present', 'missing', 'remote')`.
- `capabilities.profile("inline_check")["offline_fallback"]` equals exactly
  `This check is available when you are reading with a session.`
- No profile's `known_limits` value equals the string `none` in any casing.
- `grep -c "open(" capabilities.py` reports `0`, and
  `grep -cE "^import (evidence|runtime)|^from (evidence|runtime)" capabilities.py`
  reports `0`.
- `for t in tests/*.py; do python "$t" || exit 1; done` exits 0.
- The two golden SHA-256 values in `16A-PRECONDITION.md` are unchanged.
- No em dash character appears in `capabilities.py` or in
  `tests/capability_profile_check.py`.
  </acceptance_criteria>
  <reversibility rating="costly">The fifteen capability names and the six-field
  profile shape become a published contract that plan 16A-05, plan 16A-07, and
  Phases 16B, 16C, and 17A read, and that the schema in Task 2 publishes. Rated
  costly rather than one-way because neither half was chosen here: the six
  fields are CAP-02's own, transcribed, and the module boundary was settled at
  plan 16A-01 Task 3's blocking `D-16A-2` checkpoint. Renaming a capability
  before the 16A freeze is a code change; after it, plan 16A-10's freeze record
  makes it a published-surface rename.</reversibility>
  <done>Every semantic capability declares its support, its fallback, its
  validation, and its real limits, and the registry refuses a profile that does
  not.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: publish the profile as a schema the shipped validator accepts</name>
  <files>schemas/capability_profile.schema.json, tests/capability_profile_check.py</files>
  <read_first>
- `schema_validate.py` lines 1 to 40 in full, in particular the `SUPPORTED`
  keyword tuple at lines 27 to 31 and `check_schema` at lines 13 to 19, which
  walks the whole document before any instance is examined and refuses any
  keyword outside `SUPPORTED`.
- `schemas/visual_interaction.schema.json` in full, the closest shipped analog:
  a closed `enum`, `additionalProperties: false`, and a `required` array listing
  every field.
- `capabilities.py` in full as it stands after Task 1.
- `.planning/REQUIREMENTS.md` `CAP-02`'s six field names, verbatim, so the
  schema's `required` array uses the requirement's own vocabulary.
- `tests/protocol_roundtrip.py`, to see how the repository couples a published
  vocabulary to its schema, so the same coupling is added rather than a new
  style of check invented.
  </read_first>
  <behavior>
- `schema_validate.check_schema` on `schemas/capability_profile.schema.json`
  returns without raising, meaning every keyword in the document is inside the
  validator's `SUPPORTED` set.
- Validating each of the fifteen registry entries against the schema produces no
  error.
- Validating an entry missing any one of the six CAP-02 fields produces an
  error naming the missing field.
- Validating an entry whose `renderer_availability` is outside
  `RENDERER_AVAILABILITY` produces an error.
- Validating an entry carrying an extra key produces an error, because
  `additionalProperties` is `false`.
- Validating an entry whose `offline_fallback` is the empty string produces an
  error, because that field carries `minLength: 1`.
  </behavior>
  <action>
1. Create `schemas/capability_profile.schema.json`. Its shape, following
   `schemas/visual_interaction.schema.json`:
   - `type: "object"`, `additionalProperties: false`.
   - `properties` with exactly the seven `CAPABILITY_PROFILE_KEYS`:
     `name` (`type: "string"`, `minLength: 1`), `accessible_behavior`
     (`type: "string"`, `minLength: 1`), `offline_fallback`
     (`type: "string"`, `minLength: 1`), `renderer_availability`
     (`type: "string"`, `enum` listing exactly `available`, `degraded`,
     `unavailable`), `version` (`type: "integer"`, `minimum: 1`), `validation`
     (`type: "string"`, `minLength: 1`), `known_limits` (`type: "string"`,
     `minLength: 1`).
   - `required` listing all seven.

   Use no keyword outside `schema_validate.SUPPORTED`. In particular do not use
   `description`, `title`, `$schema`, `default`, `examples`, `format`, or
   `anyOf`: `check_schema` walks the whole document and refuses any of them
   outright, so a schema carrying a friendly description would be rejected
   rather than partially applied. Read the `SUPPORTED` tuple before writing a
   single key, and if a documentation keyword is genuinely wanted, record that
   as an open item in the summary rather than adding it and finding out.

2. Add a schema-coupling assertion to `tests/capability_profile_check.py`: it
   calls `schema_validate.check_schema` on the schema document, then validates
   every one of the fifteen registry entries against it, then validates four
   deliberately broken entries (one missing `offline_fallback`, one with
   `renderer_availability` set to `sometimes`, one carrying an extra key
   `colour`, and one with `offline_fallback` set to the empty string) and
   asserts each produces an error naming the offending field or value.

3. Add a drift assertion in the same file: the schema's
   `properties.renderer_availability.enum` array equals
   `list(capabilities.RENDERER_AVAILABILITY)`, and the schema's `required` array
   sorted equals `sorted(capabilities.CAPABILITY_PROFILE_KEYS)`. This is the
   same coupling discipline `tests/protocol_roundtrip.py` already applies to the
   lint namespace: the tuple and the schema are read from their two homes and
   compared, never restated in the test.
  </action>
  <verify>
  <automated>python tests/capability_profile_check.py</automated>
Expected: prints `capability registry ok` and exits 0, now including the schema
assertions. The degraded state this task must also prove is the validator's own
refusal path: temporarily add the keyword `description` to a copy of the schema
in a temporary directory, call `check_schema` on it, and confirm it raises
`SchemaError` rather than silently ignoring the keyword. Do not commit the
modified copy.
  </verify>
  <acceptance_criteria>
- `schemas/capability_profile.schema.json` exists and
  `python -c "import json, schema_validate; d=json.load(open('schemas/capability_profile.schema.json')); schema_validate.check_schema(d); print('schema accepted')"`
  prints `schema accepted` and exits 0.
- The schema's `required` array has exactly seven members and its
  `additionalProperties` is `false`.
- All fifteen registry entries validate with no error.
- The four deliberately broken entries each produce at least one error.
- `python tests/capability_profile_check.py` exits 0.
- `python tests/protocol_roundtrip.py` exits 0.
- `grep -cE '"(description|title|\$schema|default|examples|format|anyOf)"' schemas/capability_profile.schema.json`
  reports `0`.
- The schema file contains no em dash character.
  </acceptance_criteria>
  <reversibility rating="costly">A file under `schemas/` is a published
  contract by this project's own convention, read by `itembank schema --all` and
  by any agent client. Rated costly rather than one-way because every field and
  every enum member in it is transcribed from a decision already made:
  CAP-02's six fields and `D-16A-5`'s three-member availability tuple. Nothing
  is chosen here. Changing a required field after plan 16A-10's freeze would be
  a schema migration.</reversibility>
  <done>The capability profile is a validated published contract, and an
  incomplete profile fails validation instead of passing quietly.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: the static instructional path, proven byte identical against shipped behavior</name>
  <files>surfaces/lesson.py, fixtures/lesson_capability_corpus.py, tests/capability_stress_corpus_tracer.py</files>
  <read_first>
- `surfaces/lesson.py` lines 1121 to 1160, `_callout_html` in full. The
  `slug == "check"` branch with `gate is None` at lines 1137 to 1146 is the
  exact code this task rewires, and the string at line 1141 is the exact copy
  it must keep producing.
- `capabilities.py` as it stands after Tasks 1 and 2, in particular
  `static_path` and `resolved_availability`.
- `tests/gate_roundtrip.py` in full, or at minimum every assertion mentioning
  the no-session check copy. That suite is the shipped proof this task must keep
  green, and it is the reason the byte-identity claim is checkable rather than
  asserted.
- `tests/capability_stress_corpus_tracer.py` in full as it stands after plan
  16A-03, for the scenario convention and the `main()` counter.
- `.planning/REQUIREMENTS.md` `CAP-02`'s Fixture sentence, verbatim: "a 16A
  profile fixture declaring one synthetic capability's full support profile and
  a second capability with its renderer marked unavailable, asserting the static
  instructional path is shown".
  </read_first>
  <behavior>
- `_static_instructional_html(name, registry=None)` returns one
  `<p class="capability-static">` element containing the HTML-escaped
  `offline_fallback` of the named capability, and the empty string for an
  unregistered name. It adds no class beyond `capability-static`, no inline
  style, and no script.
- `_callout_html`'s gate-less check branch produces exactly the bytes it
  produced before this task, with the copy now sourced from
  `capabilities.static_path("inline_check")` rather than from a literal.
- `build_unavailable_capability(dest_dir)` writes one bank and returns its path,
  and the tracer registers two synthetic capabilities against a copied registry:
  one fully specified and available, one with `renderer_availability` set to
  `unavailable`, using `capabilities.register`'s non-mutating return so the
  module registry is untouched.
- `capabilities.profiles()` still returns fifteen entries after the tracer has
  registered its two synthetic capabilities, proving `register` did not mutate
  the module.
  </behavior>
  <action>
1. Add `_static_instructional_html(name, registry=None)` to
   `surfaces/lesson.py`, beside `_callout_html`. It looks up
   `capabilities.static_path(name, registry)` and returns
   `<p class="capability-static">` wrapping the HTML-escaped text, or the empty
   string when the lookup returns the empty string. Import `capabilities` at the
   top of `surfaces/lesson.py` alongside the existing module imports.

   Introduce no CSS rule, no color, no spacing value, and no token. If
   `LESSON_CSS` needs a rule for `.capability-static` for the text to be legible
   at all, add nothing and record the gap as an open item for Phase 17A in the
   summary: an unstyled paragraph is still readable, and 17A owns how it looks.

2. Rewire `_callout_html`'s gate-less check branch to source its copy from
   `capabilities.static_path("inline_check")` instead of the inline literal at
   line 1141. Keep the surrounding markup exactly as it is: the same
   `<section class="callout callout-check">`, the same
   `<p class="callout-label">` with the icon and the escaped label, and the same
   `<div class="callout-body">` wrapper around a `<p>`. Do not substitute
   `_static_instructional_html` for that markup; the check branch has its own
   established container and changing it would change the shipped bytes.

   The whole point of this step is that nothing observable changes. Run
   `python tests/gate_roundtrip.py` and `python tests/lesson_roundtrip.py`
   before and after and confirm both exit 0 both times. If either goes red, the
   registry string does not match the shipped one and the registry is wrong, not
   the test.

3. Add `build_unavailable_capability(dest_dir)` to
   `fixtures/lesson_capability_corpus.py`, following the established shape:
   literal fictional content, no `random`, deterministic bytes. It writes one
   bank containing one `> [!CHECK: <id>]` block whose id matches a real item in
   the same bank, plus one registered callout, so a gate-less render exercises
   the static instructional path against real shipped code rather than a stub.

4. Add two scenarios to `tests/capability_stress_corpus_tracer.py`:
   - `scenario_capability_profiles()`: asserts fifteen profiles; asserts every
     `SEMANTIC_ROLE_CATALOG` role maps to exactly one profile and that
     `guided_mode` is the single extra; asserts `validate_profile` is empty for
     all fifteen; and asserts every profile validates against
     `schemas/capability_profile.schema.json` through `schema_validate`.
   - `scenario_unavailable_renderer()`: builds
     `build_unavailable_capability`'s bank; renders it with no gate context and
     asserts the rendered page contains exactly the `inline_check` profile's
     `offline_fallback` string; asserts
     `capabilities.resolved_availability("inline_check", {})` is `unavailable`
     and that the same call with `{"gate_context": True}` is `available`; then
     builds a copied registry with `register`, adding one fully specified
     available synthetic capability and one synthetic capability marked
     `unavailable`, asserts `_static_instructional_html` on the unavailable one
     returns a paragraph carrying its declared fallback text, and asserts
     `len(capabilities.profiles())` is still `15`, proving `register` did not
     mutate the module registry.

   `scenario_unavailable_renderer` is CAP-02's Fixture sentence executed
   literally: one synthetic capability's full support profile, a second with its
   renderer marked unavailable, and the static instructional path asserted shown.

5. Add one assertion to `scenario_capability_profiles` covering CAP-02's
   no-decorative-block clause: build a minimal bank containing a `## LESSON`
   section, one `### ` heading, and prose only, with zero callouts of any kind,
   and assert `model.lint` reports no error and no warning whose code begins
   `lesson.` or `style.` that names a missing block. A style system that
   required a decorative block would fire here, which is what makes the clause
   checkable rather than aspirational.

6. Update `16A-VALIDATION.md`'s Per-Task Verification Map with three rows for
   plan 16A-04's tasks, naming `tests/capability_profile_check.py`,
   `scenario_capability_profiles`, and `scenario_unavailable_renderer`, with a
   Status of `passing`. Tick the Wave 0 Requirements checkbox for the capability
   registry and its unit assertions.
  </action>
  <verify>
  <automated>python tests/capability_stress_corpus_tracer.py</automated>
Expected final line: `TRACER: 7 passed, 0 skipped, 0 failed`, exit code 0. The
degraded state this task must also prove is the byte identity of the shipped
gate-less check render: run `python tests/gate_roundtrip.py` and
`python tests/lesson_roundtrip.py`, expecting exit code 0 from both, and record
in the summary that both were green before this task as well.
  </verify>
  <acceptance_criteria>
- `python tests/capability_stress_corpus_tracer.py` exits 0 with the final line
  `TRACER: 7 passed, 0 skipped, 0 failed`.
- `python tests/gate_roundtrip.py` exits 0.
- `python tests/lesson_roundtrip.py` exits 0.
- The two golden SHA-256 values in `16A-PRECONDITION.md` are unchanged.
- `grep -c "This check is available when you are reading with a session." surfaces/lesson.py`
  reports `0`, proving the literal now lives only in `capabilities.py`.
- `grep -c "This check is available when you are reading with a session." capabilities.py`
  reports `1`.
- `capabilities.profiles()` returns fifteen entries after the tracer run, proving
  `register` did not mutate the module registry.
- `for t in tests/*.py; do python "$t" || exit 1; done` exits 0.
- `python itembank.py guard .` reports `0 offending files`.
- `16A-VALIDATION.md` has three new filled rows naming plan `16A-04`.
- No em dash character appears in any line this task added.
  </acceptance_criteria>
  <reversibility rating="reversible">A render helper, a fixture builder, and two
  test scenarios. The one behavior change is moving a string's home, and the
  byte-identity assertion is what makes that reversible: the rendered output is
  unchanged either way.</reversibility>
  <done>An unavailable renderer shows its declared static instructional path,
  the copy has one home, and the shipped bytes did not move while that
  happened.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| capability profile to disclosure decision | A `renderer_availability` value sits next to disclosure and could be misread as permission to reveal. |
| registry to renderer | The renderer now reads a user-visible string from the registry; a wrong string in the registry becomes wrong copy on a learner's screen. |
| schema to registry | Two homes for the same vocabulary drift apart silently unless something compares them. |
| test registration to module state | A test that registers a synthetic capability could leak it into every later scenario if registration mutated the module. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-16A-04-01 | Elevation of Privilege | a capability profile read as a disclosure permission | high | mitigate | The module docstring states the boundary and cites `runtime.glossable`; `capabilities.py` imports neither `runtime` nor `evidence`, asserted by grep in the acceptance criteria, so it structurally cannot reach a disclosure decision. Plan 16A-09 attacks this directly. |
| T-16A-04-02 | Tampering | a registry string silently changing shipped learner-visible copy | high | mitigate | Task 3 asserts the shipped gate-less check render is byte identical by keeping `tests/gate_roundtrip.py` and `tests/lesson_roundtrip.py` green, and the acceptance criteria assert the literal appears exactly once in the tree and in `capabilities.py`. |
| T-16A-04-03 | Tampering | a capability registered with no fallback, failing CAP-02's Degraded clause silently | high | mitigate | `validate_profile` refuses an empty `offline_fallback` and the schema carries `minLength: 1` on that field; both the unit check and the tracer assert all fifteen validate clean. |
| T-16A-04-04 | Spoofing | a schema and a registry vocabulary that disagree | medium | mitigate | Task 2 step 3 adds a drift assertion comparing the schema's `enum` and `required` arrays against the module tuples, read from both homes rather than restated in the test, following `tests/protocol_roundtrip.py`'s established coupling discipline. |
| T-16A-04-05 | Tampering | a test registration leaking a synthetic capability into later scenarios | medium | mitigate | `register` returns a new dict and mutates nothing, and `scenario_unavailable_renderer` asserts `len(profiles())` is still fifteen after registering two synthetic capabilities. |
| T-16A-04-06 | Repudiation | a profile whose `known_limits` says `none`, hiding a real limitation | medium | mitigate | The action forbids the word and the acceptance criteria assert no profile's `known_limits` equals `none` in any casing; the freeze-gate human review in plan 16A-10 reads the fifteen profiles for honesty, which is the part a grep cannot check. |
| T-16A-04-07 | Tampering | a second rights vocabulary minted for media | high | mitigate | `MEDIA_RIGHTS_STATES` is assigned from `identity.RIGHTS_STATES` by reference and the acceptance criteria assert identity with `is`, not equality, so a retyped tuple with the same members fails the check. |
| T-16A-04-08 | Tampering | supply chain: a third-party dependency introduced by this plan | high | mitigate | None is added; every change is standard library only, and the schema is validated by the repository's own `schema_validate.py`. Per `PLANNING-DIRECTIVES.md` section 4a the absence of dependencies is explicitly not the mitigation: the mitigation is that any dependency ever added here is vendored at a pinned version with a recorded checksum and a named license review, following the KaTeX precedent in `09-03-PLAN.md`. |
| T-16A-04-09 | Information Disclosure | real course content entering the repository through the new fixture builder | high | mitigate | `build_unavailable_capability` writes from a literal fictional constant with no `random` and no external read; `python itembank.py guard .` reporting `0 offending files` is an acceptance criterion. |
</threat_model>

<out_of_scope>
Refused by this plan, by name, so no adjacent temptation is decided by executor
judgment:

- Media asset metadata and the `## MEDIA` registry. This plan lands
  `MEDIA_RIGHTS_STATES` and `MEDIA_AVAILABILITY` as constants only; plan 16A-05
  owns the grammar, the parser, and the lint codes.
- Any media rights enforcement. `D-16A-8` settles that 16A declares and does not
  enforce, and no code path in this plan gates on a rights value.
- The registered output modes and the backburner catalog. Plan 16A-07 owns
  `OUTPUT_MODES`, `BACKBURNER_MODES`, `compose_outline`, `compose_glossary`, and
  `backburner_entry`.
- Any CSS rule for `.capability-static` or for any callout slug. Phase 17A owns
  how these look; this plan records the gap rather than filling it.
- Any edit to `runtime.py`, `evidence.py`, or `surfaces/quiz.py`.
- A `description` or `title` keyword in the schema, however much more readable
  it would be. `schema_validate.check_schema` refuses any keyword outside its
  `SUPPORTED` set outright.
- A mutable module-level registry. `register` returns a new dict; a later plan
  that wants a mutating registration must raise it as its own decision rather
  than adding one.
</out_of_scope>

<flagged_assumptions>
- **CAP-02's three probe rows are resolved by this plan** as the explicit
  criteria carried in `must_haves.truths`: adjacency as the duplicate-name
  refusal, empty as `profile` returning `None` and `profiles({})` returning an
  empty tuple, and ordering as the literal source order being stable across
  calls.
- **The lowering rules in `resolved_availability` are this plan's own policy,
  not a requirement's.** CAP-02 names the six profile fields and the Degraded
  clause; it does not say which context facts lower which capability. The seven
  rules in Task 1 step 3 are written out so the executor transcribes rather than
  invents, and they are recorded here as a plan-level decision that a later
  phase may extend additively.
- **`.capability-static` has no CSS rule after this plan.** An unstyled
  paragraph is legible, and Phase 17A owns how it looks. Task 3 step 1 records
  the gap rather than filling it, so the absence is a recorded handoff and not
  an oversight.
</flagged_assumptions>

<summary_obligations>
`16A-04-SUMMARY.md` records: the fifteen capability names in registry order; the
`inline_check` `offline_fallback` string verbatim and confirmation that
`tests/gate_roundtrip.py` was green both before and after Task 3; which import
branch Task 1 step 5 took for `identity.RIGHTS_STATES`; the schema's `required`
array and `enum` array as written; whether `check_schema` accepted the schema on
the first attempt and, if not, which keyword it refused; the four broken-entry
validation results; the tracer's final summary line verbatim; the two golden
SHA-256 values as re-verified; whether any profile's `known_limits` needed
rewriting to avoid the word `none`; which truth was verified by which command
with the command's actual stdout; and any deviation from this plan with its
reason.
</summary_obligations>

<output>
Create
`.planning/phases/16A-semantic-capability-activity-contract/16A-04-SUMMARY.md`
when done.
</output>
