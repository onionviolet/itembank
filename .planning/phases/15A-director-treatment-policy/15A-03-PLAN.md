---
phase: 15A-director-treatment-policy
plan: 03
type: execute
wave: 3
depends_on: ["15A-02"]
files_modified:
  - director.py
  - fixtures/corpus_14b.py
  - tests/director_roundtrip.py
autonomous: true
requirements: [TREAT-02]
estimate:
  tokens: 58000
  raw_tokens: 58000
  tasks: 2
  confidence: low
must_haves:
  truths:
    - "Every objective-to-source coverage claim carries a stable locator, a confidence token, and exactly one of the five graph.BINDING_STATES values, and the state is computed by one ordered six-rule classifier whose rules are evaluated first-match-wins in the order the plan fixes."
    - "Heading or name similarity alone can never produce covered: a claim whose match_kind is anything other than locator is classified unknown before any other rule is consulted, and the fixture's heading-similarity decoy, whose heading text matches the objective statement word for word, classifies unknown."
    - "The shipped auditor's older five-state coverage vocabulary and TREAT-02's vocabulary stay two distinct, correctly-scoped classifiers: every state string director writes is a member of graph.BINDING_STATES, asserted by a recursive walk over every record the fixture produces, and auditor.coverage_report is never called with a director state nor its output written into a director state field."
    - "TREAT-02 adjacency edge: two claims for one objective sharing a source but carrying different locators are two separate claims that never merge; two claims with an identical objective, source, and locator triple collide, and the second is refused with director.duplicate_coverage_claim rather than silently overwriting the first."
    - "TREAT-02 empty edge: an objective with no source binding at all classifies missing; a source bound but carrying no resolvable locator classifies unknown; neither classifies covered, and an unverifiable claim reads as unknown rather than as covered."
    - "TREAT-02 ordering edge: coverage claims are emitted in the document's authored objective order, then by binding insertion order within one objective, and two classification passes over one unchanged document produce byte-identical claim lists."
    - statement: "Locator equality is exact string equality after Unicode NFC normalization and line-ending normalization, with no case folding and no fuzzy or similarity matching anywhere in the comparison path, so no near-match can ever reach the covered branch."
      verification: backstop
  prohibitions: []
  artifacts:
    - "director.py gains MATCH_KINDS, THIN_SPAN_CHARS, COVERAGE_CLAIM_KEYS, locator_key, resolve_locator, coverage_claim, and classify_coverage"
    - "fixtures/corpus_14b.py gains build_coverage_fixture with one claim per binding state plus a heading-similarity decoy"
    - "tests/director_roundtrip.py gains check_coverage_classifier and check_coverage_states"
  key_links:
    - "classify_coverage returns members of graph.BINDING_STATES and nothing else. auditor.coverage_report, shipped since Phase 11, returns a lookalike five-state vocabulary scoped to syllabus-objective-to-bank-item coverage. The two look alike and a reader searching the codebase for the coverage function finds the auditor's first, because it is the one that runs today. Writing one vocabulary into the other's field produces a green test that means the wrong thing."
    - "covered is reachable only by falling through all five earlier rules. Every degradation path, every unrecognized value, and every unresolvable locator lands on unknown, thin, missing, or conflicting. Making covered unreachable by degradation is what enforces TREAT-02's similarity rule structurally rather than by care."
---

<objective>
Give every objective-to-source coverage claim a stable locator, a confidence
token, and exactly one of the five TREAT-02 states, computed by one ordered
classifier that cannot be reordered by accident and whose `covered` branch is
reachable only by a resolved locator.

The defect this closes is the one TREAT-02 names in plain words: heading or
name similarity alone cannot produce covered, and an unverifiable claim reads
as unknown, not covered. A course that reports coverage it does not have is
worse than a course that reports a gap, because the gap gets filled and the
false claim does not.

Decisions already made, cited, and never re-derived here:

- **REQUIREMENTS.md TREAT-02**, quoted: "Every objective-to-source and coverage
  claim carries a stable locator, confidence, and state (covered, thin,
  missing, conflicting, unknown); heading or name similarity alone cannot
  produce covered... Degraded: an unverifiable claim reads as unknown, not
  covered."
- **14B-03-PLAN.md behavior block**, quoted: "A binding whose `state` cell
  holds an unrecognized value degrades to `unknown` on read, with the source
  string preserved in `original_state`, and never to `covered`. TREAT-02's rule
  that similarity alone cannot produce covered is enforced by making `covered`
  unreachable by degradation." This plan extends that rule from the read path
  to the classification path.
- **15A-RESEARCH.md Pitfall 1**: `auditor.coverage_report` uses a different,
  older five-state vocabulary scoped to a different pairing and predates
  TREAT-02. Do not rename one to match the other; keep them as two distinct,
  correctly-scoped classifiers.
- **15A-01 and 15A-02**: the recommendation record already carries a `coverage`
  block validated against a schema whose `state` and `match_kind` are closed
  enums. This plan computes the state rather than trusting the provider's.

Decisions this plan makes and locks, so the executor never guesses:

| Open question | Locked answer | One-line rationale |
|---|---|---|
| Who decides the coverage state | `director.classify_coverage`, locally and deterministically, from the claim's own fields. The provider's proposed `coverage.state` is recorded as `proposed_state` and never adopted | A model asserting its own coverage is exactly the self-certification AGENT-02 forbids; the state is a local computation over a locator that either resolves or does not. |
| The classifier's rule order | Six ordered rules, first match wins, in the exact order fixed in Task 1 | An unordered rule set is two implementations. Fixing the order in the plan means the executor transcribes it. |
| What makes a claim thin | A resolved span shorter than `THIN_SPAN_CHARS = 240` characters, or a confidence of `low` | 240 characters is roughly one substantive paragraph. It is a named module constant so it can be tuned in one place without touching the rule order. |
| What makes a claim conflicting | Two or more resolved claims for one objective carrying different non-empty `assertion` values | Mechanical and testable. The `assertion` is agent-supplied and labeled synthesis; the classifier compares it, it does not interpret it. |
| Locator equality | Exact string equality after Unicode NFC normalization and line-ending normalization to `\n`, no case folding, no fuzzy match | The project already normalizes whitespace and line endings before fingerprinting (D-14A-2). Case folding or fuzzy matching would reopen the similarity path TREAT-02 closes. |
| Duplicate claims | An identical `(objective, source_object_id, locator)` triple is refused with `director.duplicate_coverage_claim`; a differing locator is a second, separate claim | Two claims about different passages of one source are two real claims; the same claim recorded twice is a bug that should surface rather than overwrite. |

Purpose: make a coverage claim checkable rather than assertable.
Output: the locator resolver, the six-rule classifier, and a fixture carrying
one claim per state plus a decoy.
</objective>

<context>
@.planning/phases/15A-director-treatment-policy/15A-RESEARCH.md
@.planning/phases/15A-director-treatment-policy/15A-PATTERNS.md
@.planning/phases/15A-director-treatment-policy/15A-01-PLAN.md
@.planning/phases/15A-director-treatment-policy/15A-02-PLAN.md
@.planning/phases/14B-graph-course-package-prototype/14B-03-PLAN.md
@.planning/PLANNING-DIRECTIVES.md
@.planning/PLAN-TEMPLATE.md
</context>

## Artifacts this phase produces (plan 15A-03 share)

Added to `director.py`. Every symbol below is new in this phase.

- Constants: `MATCH_KINDS = ("locator", "heading-similarity", "none")`,
  `THIN_SPAN_CHARS = 240`,
  `COVERAGE_CLAIM_KEYS = ("objective_id", "source_object_id", "locator",
  "match_kind", "confidence", "assertion", "span_chars", "proposed_state",
  "state")`.
- Functions: `locator_key(text)`, `resolve_locator(source_text, locator)`,
  `coverage_claim(...)`, `classify_coverage(claims)`.
- New `DirectorError` codes: `director.duplicate_coverage_claim`,
  `director.unknown_match_kind`.

Added to `fixtures/corpus_14b.py`:

- `build_coverage_fixture(dest)` returning a dict with the keys
  `course_root`, `source_texts`, `claims`, and `decoy_claim`, building one
  claim per `graph.BINDING_STATES` member plus one heading-similarity decoy.

New test functions in `tests/director_roundtrip.py`:
`check_coverage_classifier()` and `check_coverage_states()`.

No CLI command, no daemon route, no schema file, and no journal record type is
produced by this plan.

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: the locator resolver and the six ordered classification rules</name>
  <files>director.py, tests/director_roundtrip.py</files>
  <read_first>
- `director.py` as it stands after plan 15A-02, in full: `DIRECTOR_CODES`,
  `RECOMMENDATION_KEYS`, `validate_recommendation`, `rank_candidates`,
  `untreated_objectives`, and the module docstring's tier contract.
- `graph.py` as landed: `BINDING_STATES`, `EDGE_CONFIDENCES`, and the
  `add_binding` degradation rule that an unrecognized `state` reads back as
  `unknown` with the source string preserved in `original_state`.
- `auditor.py` lines 370 to 489, `coverage_report` and its `_row` calls, read
  once so the two vocabularies are understood as distinct. This module is read,
  never imported by `director.py` in this plan.
- `identity.py` as landed: `normalize_for_fingerprint`, for the whitespace and
  line-ending normalization shape this project already uses.
- `15A-RESEARCH.md` Pitfall 1 in full.
- `tests/director_roundtrip.py` as it stands after plan 15A-02.
  </read_first>
  <behavior>
Assertions added to `tests/director_roundtrip.py` in a new
`check_coverage_classifier()` function, written before the code. Run and
confirm it fails.

Locator normalization and resolution:

- `director.locator_key("Section  2.1\r\n")` equals
  `director.locator_key("Section  2.1\n")`. Line endings normalize.
- `director.locator_key` applies Unicode NFC: the composed and the decomposed
  spellings of a single accented character produce equal keys.
- `director.locator_key("Section 2.1")` does not equal
  `director.locator_key("section 2.1")`. There is no case folding.
- `director.locator_key("Section 2.1")` does not equal
  `director.locator_key("Section 2")`. There is no prefix matching.
- `director.resolve_locator(source_text, locator)` returns a dict with the
  exact key set `{"resolved", "span_chars"}`. `resolved` is `True` only when
  the normalized locator occurs as an exact substring of the normalized source
  text; `span_chars` is the character length of the matched span, and `0` when
  it did not resolve.
- `director.resolve_locator("", "anything")` returns `resolved` `False` and
  `span_chars` `0`, raising nothing.
- `director.resolve_locator(source_text, "")` returns `resolved` `False`. An
  empty locator never resolves, because everything contains the empty string
  and a claim with no locator is not a claim.

The six ordered rules, first match wins:

- `director.classify_coverage` applied to a claim list for one objective
  returns a state that is a member of `graph.BINDING_STATES`.
- Rule 1: a claim whose `source_object_id` is the empty string classifies
  `missing`, even when its `match_kind` is `locator` and its confidence is
  `high`.
- Rule 2: a claim whose `match_kind` is `heading-similarity` classifies
  `unknown`, even when its locator resolves, its span is long, and its
  confidence is `high`. A claim whose `match_kind` is `none` also classifies
  `unknown`.
- Rule 3: two claims for one objective, both with `match_kind` `locator`, both
  resolving, carrying the two different non-empty `assertion` values
  `The intake sequence begins with scene safety.` and
  `The intake sequence begins with airway assessment.`, classify
  `conflicting`. Two claims carrying the same non-empty `assertion` do not.
- Rule 4: a claim whose `confidence` is `unknown` classifies `unknown`, even
  when its locator resolves and its span is long.
- Rule 5: a claim whose resolved `span_chars` is `239` classifies `thin`, and a
  claim whose `confidence` is `low` classifies `thin` regardless of span
  length.
- Rule 6: a claim with `match_kind` `locator`, a resolving locator,
  `span_chars` of `240`, a non-empty `source_object_id`, a confidence of
  `medium` or `high`, and no conflicting sibling, classifies `covered`. The
  boundary is proven on both sides: `239` is `thin` and `240` is `covered`.
- Rule order is proven, not assumed: a single claim that satisfies the trigger
  of rules 2, 4, and 5 at once classifies `unknown`, because rule 2 fires
  first.
- An unrecognized `match_kind` raises `DirectorError` with code
  `director.unknown_match_kind` naming the value and the three accepted
  members. It never degrades to `locator`.

Vocabulary firewall:

- Every state `classify_coverage` can return is in `graph.BINDING_STATES`,
  asserted by driving all six rules and collecting the returned set, then
  asserting the collected set is a subset of `set(graph.BINDING_STATES)`.
- `hasattr(director, "auditor")` is `False`. The shipped auditor's coverage
  classifier is a different, correctly-scoped tool and this module does not
  reach it.
- `director.MATCH_KINDS` has exactly three members and
  `graph.BINDING_STATES` still has exactly five after importing `director`.
  </behavior>
  <action>
1. Add `check_coverage_classifier()` to `tests/director_roundtrip.py` first,
   wired into `main()`, with every assertion above. Run
   `python tests/director_roundtrip.py` and confirm it fails.

2. Add to `director.py` the constants
   `MATCH_KINDS = ("locator", "heading-similarity", "none")` and
   `THIN_SPAN_CHARS = 240`. Give `THIN_SPAN_CHARS` a comment stating that 240
   characters is roughly one substantive paragraph, that it is the single place
   the thin threshold is tuned, and that a change to it is a change to what the
   course claims about itself. Give `MATCH_KINDS` a comment stating that only
   the first member can lead to a covered classification and that this is
   TREAT-02's similarity rule made structural.

3. Add the two codes `director.duplicate_coverage_claim` and
   `director.unknown_match_kind` to `DIRECTOR_CODES` with these exact message
   templates:
   - `director.duplicate_coverage_claim`: `"a coverage claim for objective %s
     against source %s at locator %s is already recorded; a repeated claim is
     refused rather than overwriting the first"`
   - `director.unknown_match_kind`: `"%s is not one of the three match kinds
     (locator, heading-similarity, none); an unrecognized match kind is refused
     rather than treated as a locator match"`

4. Implement `locator_key(text)`: apply `unicodedata.normalize("NFC", text)`,
   replace `\r\n` and `\r` with `\n`, and return the result. No case folding,
   no whitespace collapsing beyond line endings, no stripping. Its docstring
   states in plain sentences that case folding or fuzzy matching here would
   reopen the similarity path TREAT-02 closes, and that this function is the
   only place a locator is normalized.

5. Implement `resolve_locator(source_text, locator)`: return
   `{"resolved": False, "span_chars": 0}` when `locator` is empty or
   `source_text` is empty; otherwise compute both keys with `locator_key` and
   return `resolved` `True` with `span_chars` equal to `len(locator_key(locator))`
   when the locator key occurs as an exact substring of the source key, and
   `resolved` `False` with `span_chars` `0` otherwise. The function is pure and
   reads no file; the caller supplies the source text.

6. Implement `classify_coverage(claims)` taking a list of claim dicts for ONE
   objective and returning one member of `graph.BINDING_STATES`. Raise
   `director.unknown_match_kind` for any claim whose `match_kind` is not in
   `MATCH_KINDS`, before any rule runs. Then apply these six rules in this
   exact order, first match wins, and write the order into the function's
   docstring as a numbered list so it cannot be reordered by a later edit
   without the docstring going wrong:
   1. `claims` is empty, or every claim has an empty `source_object_id`, gives
      `missing`.
   2. No claim has `match_kind` equal to `"locator"` gives `unknown`.
   3. Two or more claims whose `match_kind` is `"locator"` and whose
      `assertion` values are non-empty and not all equal gives `conflicting`.
   4. No claim whose `match_kind` is `"locator"` has a `confidence` other than
      `"unknown"` gives `unknown`.
   5. No claim whose `match_kind` is `"locator"` has both `span_chars` at least
      `THIN_SPAN_CHARS` and `confidence` in `("high", "medium")` gives `thin`.
   6. Otherwise `covered`.
   Read the confidence rank from `graph.EDGE_CONFIDENCES` membership, never
   from a literal list in this module.

7. Re-run `python tests/director_roundtrip.py` until it passes, then run
   `python itembank.py guard .` and confirm it reports `0 offending files`.
  </action>
  <verify>
  <automated>python tests/director_roundtrip.py</automated>
Expected: prints `OK director_roundtrip` and exits 0. Degraded states this task
proves: an empty source text, an empty locator, and an unrecognized match kind
each land on a refusal or on a non-covered state rather than on a permissive
default, and a claim triggering three rules at once resolves by the fixed
order rather than by whichever branch happened to run first.
  </verify>
  <acceptance_criteria>
- `python tests/director_roundtrip.py` exits 0 and prints `OK director_roundtrip`.
- `python itembank.py guard .` prints `0 offending files` and exits 0.
- `python -c "import director; print(len(director.MATCH_KINDS), director.THIN_SPAN_CHARS)"`
  prints `3 240`.
- `python -c "import director; print(director.resolve_locator('', 'x'), director.resolve_locator('abc', ''))"`
  prints `{'resolved': False, 'span_chars': 0} {'resolved': False, 'span_chars': 0}`.
- `python -c "import director; print(director.locator_key('A\r\nB') == director.locator_key('A\nB'), director.locator_key('A') == director.locator_key('a'))"`
  prints `True False`.
- `python -c "import director; print(hasattr(director,'auditor'))"` prints `False`.
- `python -c "import director,graph; print(len(graph.BINDING_STATES))"` prints `5`.
- `director.py` contains `def classify_coverage(`, `def resolve_locator(`, and
  `def locator_key(`.
- `classify_coverage`'s docstring contains a numbered list of exactly six
  rules.
- Neither `director.py` nor `tests/director_roundtrip.py` contains an em dash
  character.
  </acceptance_criteria>
  <done>A coverage state is computed locally from a locator that either
  resolves or does not, by six rules in a fixed order, with covered reachable
  only through the resolved-locator branch.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: the five-state fixture, the decoy, duplicates, and ordering</name>
  <files>director.py, fixtures/corpus_14b.py, tests/director_roundtrip.py</files>
  <read_first>
- `director.py` as it stands after Task 1, in full, especially
  `classify_coverage`'s six-rule docstring.
- `fixtures/corpus_14b.py` as it stands after plan 15A-02, especially
  `build_recommendation_fixture` and the fixed-seed rule.
- `REQUIREMENTS.md`, the TREAT-02 entry in full including its Fixture sentence,
  quoted: "a 15A synthetic binding set carrying one covered, one thin, one
  missing, one conflicting, and one unknown claim, plus a heading-similarity
  decoy that must not read as covered."
- `graph.py` as landed: `add_binding`'s parameter list, so a claim converts to
  a binding row without inventing a column.
- `tests/director_roundtrip.py` as it stands after Task 1.
  </read_first>
  <behavior>
Assertions added to `tests/director_roundtrip.py` in a new
`check_coverage_states()` function, written before the code.

The five-state fixture, one claim per state:

- `fixtures.corpus_14b.build_coverage_fixture(dest)` returns a dict whose
  `claims` key holds exactly five claim groups, keyed by the five members of
  `graph.BINDING_STATES`.
- For each of the five keys, `director.classify_coverage` applied to that
  group returns exactly that key. All five states are produced by real fixture
  data, not by constructing the state string directly.
- Every claim dict in the fixture has the exact key set
  `set(director.COVERAGE_CLAIM_KEYS)`.
- The fixture's source texts are fictional and are generated from the same
  fixed seed the existing corpus generators use, so a rebuild is
  byte-identical.

The heading-similarity decoy:

- The fixture's `decoy_claim` has a `locator` whose text is a heading that
  matches its objective's statement word for word, its `match_kind` is
  `heading-similarity`, its `confidence` is `high`, and its `span_chars` is
  greater than `director.THIN_SPAN_CHARS`.
- `director.classify_coverage([decoy_claim])` returns `unknown`. It does not
  return `covered`, and the test asserts that specific inequality by name so a
  future regression that returns `thin` also goes red for the right reason.
- Changing only the decoy's `match_kind` to `"locator"` and leaving every other
  field identical makes the same claim classify `covered`. This proves the
  decoy is otherwise a well-formed covered claim and that `match_kind` is the
  single field carrying the refusal.

Duplicates and adjacency:

- `director.coverage_claim(...)` called twice with the same `objective_id`,
  `source_object_id`, and `locator` against a claim list already carrying the
  first raises `DirectorError` with code
  `director.duplicate_coverage_claim`, and the message names all three values.
- The same call with a different `locator` appends a second claim; the returned
  list has two members and both are retained. Two claims about different
  passages of one source are two claims.
- Two claims that differ only by trailing whitespace in their locator are
  duplicates, because `locator_key` normalizes line endings; two claims that
  differ only by letter case are NOT duplicates, because `locator_key` does not
  case-fold. Both directions are asserted.

Ordering and stability:

- `director.coverage_claims_for(doc, source_texts)` returns claims in the
  document's authored objective order, and within one objective in the order
  the `## Bindings` rows appear.
- Two consecutive calls on the same unchanged document and the same source
  texts return lists that compare equal member for member, including key order
  within each dict.
- Serializing the returned list with `json.dumps(..., sort_keys=True)` twice
  produces byte-identical strings.

Vocabulary firewall, on real data:

- Walking every claim the fixture produces and every state
  `classify_coverage` returns for it, every state string is a member of
  `graph.BINDING_STATES`.
- No claim's `state` or `proposed_state` field, at any point, holds a value
  outside `graph.BINDING_STATES` plus the empty string.
  </behavior>
  <action>
1. Add `check_coverage_states()` to `tests/director_roundtrip.py` first, wired
   into `main()`, with every assertion above. Run and confirm it fails.

2. Add to `director.py` the constant `COVERAGE_CLAIM_KEYS = ("objective_id",
   "source_object_id", "locator", "match_kind", "confidence", "assertion",
   "span_chars", "proposed_state", "state")` with a comment stating that
   `proposed_state` is what the provider suggested and is history only, that
   `state` is what `classify_coverage` computed, and that no code path reads
   `proposed_state` to decide anything.

3. Implement `coverage_claim(claims, objective_id, source_object_id, locator,
   match_kind, confidence, assertion, source_text, proposed_state="")`. It
   refuses a duplicate `(objective_id, source_object_id, locator_key(locator))`
   triple with `director.duplicate_coverage_claim`, refuses an unrecognized
   `match_kind` with `director.unknown_match_kind`, calls `resolve_locator` to
   fill `span_chars`, sets `state` to the empty string, appends the new claim
   in `COVERAGE_CLAIM_KEYS` order, and returns the extended list. It never
   mutates the list it was given; it returns a new list.

4. Implement `coverage_claims_for(doc, source_texts)`: walk `doc["objectives"]`
   in authored order, and for each objective walk the `## Bindings` rows whose
   `objective` matches and whose `binding_kind` is `source`, in row order,
   building one claim per row through `coverage_claim` with the source text
   looked up from the `source_texts` mapping. A source id absent from the
   mapping produces a claim whose `match_kind` is `none` and whose
   `span_chars` is `0`, never an exception, because a source that cannot be
   read is an unknown claim and not a crash. Then set each claim's `state` by
   calling `classify_coverage` over that objective's whole claim group.

5. Add `build_coverage_fixture(dest)` to `fixtures/corpus_14b.py`. It builds
   one course root with five objectives and two sources, all fictional, and
   returns the four keys named in the artifacts section. The five claim groups,
   built so each lands on exactly one state:
   - `covered`: `match_kind` `locator`, a locator that occurs verbatim in the
     source text, `span_chars` at least 240, confidence `high`, one claim.
   - `thin`: `match_kind` `locator`, a locator that resolves to a span of
     exactly 239 characters, confidence `high`, one claim.
   - `missing`: one claim whose `source_object_id` is the empty string.
   - `conflicting`: two claims, both `match_kind` `locator`, both resolving,
     both confidence `high`, carrying the two assertion strings
     `The intake sequence begins with scene safety.` and
     `The intake sequence begins with airway assessment.`
   - `unknown`: one claim, `match_kind` `locator`, resolving, confidence
     `unknown`.
   The `decoy_claim` is a sixth claim whose `locator` is the exact text of its
   objective's statement, whose `match_kind` is `heading-similarity`, whose
   confidence is `high`, and whose resolved span is longer than 240 characters.
   Every string is fictional. No real course, book, learner, or bank content of
   any kind.

6. Re-run `python tests/director_roundtrip.py` until it passes. Then run the
   wave check: `python tests/scoring_roundtrip.py` and
   `python tests/evidence_roundtrip.py`, both expected to exit 0. Then run
   `python itembank.py guard .`.
  </action>
  <verify>
  <automated>python tests/director_roundtrip.py</automated>
Expected: prints `OK director_roundtrip` and exits 0. Also run
`python tests/scoring_roundtrip.py` and `python tests/evidence_roundtrip.py`,
both expected exit 0. Degraded states this task proves: a source id absent from
the source-text mapping produces an unknown claim rather than an exception, a
repeated identical claim is refused rather than overwriting, and a
word-for-word heading match with high confidence and a long span still reads
unknown.
  </verify>
  <acceptance_criteria>
- `python tests/director_roundtrip.py` exits 0 and prints `OK director_roundtrip`.
- `python tests/scoring_roundtrip.py` exits 0.
- `python tests/evidence_roundtrip.py` exits 0.
- `python itembank.py guard .` prints `0 offending files` and exits 0.
- `python -c "import director; print(len(director.COVERAGE_CLAIM_KEYS))"`
  prints `9`.
- `director.py` contains `def coverage_claim(` and `def coverage_claims_for(`.
- `fixtures/corpus_14b.py` contains `def build_coverage_fixture(`.
- `tests/director_roundtrip.py` contains `def check_coverage_states(`.
- None of `director.py`, `fixtures/corpus_14b.py`, or
  `tests/director_roundtrip.py` contains an em dash character.
  </acceptance_criteria>
  <done>All five TREAT-02 states are produced by real fixture data, the
  heading-similarity decoy reads unknown, a duplicate claim is refused, and the
  claim list is order-stable across runs.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| provider-proposed coverage state to recorded state | A model's own claim about how well a source covers an objective crosses into durable course state. |
| source text to locator resolution | Arbitrary source bytes are searched for a locator supplied by an agent. |
| coverage claim to reviewer | The coverage report is what a reviewer trusts to know which objectives are actually served by a source. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-15A-03-01 | Spoofing | a model self-certifying coverage by asserting `covered` | high | mitigate | The provider's value is stored as `proposed_state` and is never read for a decision; `state` is computed by `classify_coverage` from the claim's own resolvable fields. Asserted by driving all six rules against fixture data and by the `proposed_state` comment stating it is history only. |
| T-15A-03-02 | Spoofing | a heading or name similarity presented as real coverage | high | mitigate | Rule 2 fires before every rule except the missing check, so any `match_kind` other than `locator` lands on `unknown` regardless of confidence or span. The decoy assertion changes only `match_kind` between the unknown and covered outcomes, proving that field alone carries the refusal. |
| T-15A-03-03 | Tampering | the shipped auditor's older coverage vocabulary written into a TREAT-02 state field | high | mitigate | `hasattr(director, "auditor")` is `False`, and every returned state is asserted to be a member of `graph.BINDING_STATES` by a walk over real fixture data rather than over a hand-written list. |
| T-15A-03-04 | Tampering | a duplicate claim silently overwriting an earlier one | medium | mitigate | `coverage_claim` refuses an identical objective, source, and normalized-locator triple with `director.duplicate_coverage_claim` naming all three, and never mutates the list it was given. |
| T-15A-03-05 | Elevation of Privilege | a fuzzy or case-insensitive locator match widening what counts as covered | high | mitigate | `locator_key` applies only NFC and line-ending normalization. The tests assert both that line endings normalize and that case does not, so a later relaxation goes red. The residual risk, that some future locator kind needs a normalization this function does not do, is recorded as the backstop truth in this plan's must-haves. |
| T-15A-03-06 | Denial of Service | a pathological locator making resolution scan the source repeatedly | low | accept | Resolution is a single `in` test over two normalized strings, linear in the source length, once per claim. Accepted because the operation is local, single-user, and bounded by the fixture and by the adapter's own output cap. |
| T-15A-03-07 | Information Disclosure | real source text entering the repository through the coverage fixture | high | mitigate | `build_coverage_fixture` writes only fictional generated text from the existing fixed seed into a temp directory, and `python itembank.py guard .` is in the acceptance criteria of both tasks. |
| T-15A-03-08 | Tampering | supply chain: a text-similarity, fuzzy-matching, or NLP dependency introduced here | high | mitigate | None is added; the whole classifier is `unicodedata.normalize`, a string replace, a substring test, and a `sorted`. Per `PLANNING-DIRECTIVES.md` section 4a the absence of dependencies is not itself the mitigation: any dependency ever added here is vendored at a pinned version with a recorded checksum and a named license review, following the KaTeX precedent in `09-03-PLAN.md`. A similarity library would be the specific wrong dependency here, because its whole purpose is the near-match TREAT-02 forbids. |
</threat_model>

<out_of_scope>
Refused by this plan, by name:

- No call to `auditor.coverage_report` and no import of `auditor`. It may
  become an input signal to a recommendation in a later phase; it is not one
  here, and its state strings never enter a director field.
- No renaming, aliasing, or unification of the two coverage vocabularies.
  `15A-RESEARCH.md` Pitfall 1 names keeping them distinct as the correct
  outcome.
- No fuzzy matching, no stemming, no token overlap, no edit distance, no
  embedding, no similarity score of any kind.
- No writing of coverage claims into the course sidecar. A claim becomes a
  `## Bindings` row only through `course.bind_source`, which plan 15A-01
  already routes through, and widening that path is not this plan's work.
- No egress, no rights check, no autonomy enforcement. Plan 15A-04 owns them.
- No protocol replay, no resume, no reverse. Plan 15A-05 owns them.
- No change to `graph.py`, `course.py`, `journal.py`, `identity.py`,
  `auditor.py`, `model_adapter.py`, or any schema file. This plan's whole diff
  is `director.py`, `fixtures/corpus_14b.py`, and `tests/director_roundtrip.py`.
- No confidence number, no coverage percentage, no aggregate coverage score for
  a course or a module.
</out_of_scope>

<summary_obligations>
`15A-03-SUMMARY.md` records: the six-rule order as landed, copied verbatim from
`classify_coverage`'s docstring; the exact `span_chars` values the covered and
thin fixture claims resolved to, proving the 239 and 240 boundary was exercised
with real text rather than with a hand-set integer; which truth was verified by
which command; the backstop truth's residual risk restated in one sentence with
whatever evidence the fixture actually produced for it; and any deviation from
this plan with its reason.
</summary_obligations>

<output>
Create
`.planning/phases/15A-director-treatment-policy/15A-03-SUMMARY.md`
when done.
</output>
</content>
