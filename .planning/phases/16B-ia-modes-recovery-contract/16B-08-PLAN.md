---
phase: 16B-ia-modes-recovery-contract
plan: 08
type: execute
wave: 8
depends_on: ["16B-07"]
files_modified:
  - surfaces/ia.py
  - surfaces/daemon.py
  - tests/degraded_state_roundtrip.py
autonomous: true
requirements: [FLOW-02, APP-03]
estimate:
  tokens: 76000
  raw_tokens: 76000
  tasks: 3
  confidence: low
must_haves:
  truths:
    - "All eight degraded states preserve the last accepted state and expose the next safe action: crash, cancellation, disk full or interrupted write, offline, permission denied, future or unknown schema, agent or model unavailable, and corrupted course each render their exact locked sentence, their own named error code, and at least one action a learner can take next."
    - "Every banner names its error code and links to exactly one help page, and every one of the eight codes resolves through the offline help route built in plan 16B-03, so a banner is never a dead end (DegradedStateBanner error consideration)."
    - "The one dynamic fragment any banner carries is bounded: the permission-denied banner substitutes the bank-author-written basename only and never a resolved absolute path, and every other banner is a fixed pre-written sentence with no substitution at all (DegradedStateBanner long-text consideration, D9)."
    - "A Socratic or tutoring refusal renders as a locked card stating its unlock condition and never as a chat exchange: the card carries a header, exactly one sentence of the form 'Unlocks after {condition}.', no free-text input, no message thread, no typing indicator, and no control that could read as ask again or continue talking (FLOW-02, LockedRefusalCard populated consideration)."
    - "The unlock sentence's fixed one-sentence format bounds its length by contract rather than by truncation, so no locked card is ever shortened or elided (LockedRefusalCard overflow consideration)."
    - "The locked card renders in the same support region the shipped hint ladder already occupies, so a learner meeting a Socratic refusal sees the visual grammar they already know from a locked hint tier rather than a new interaction pattern."
    - statement: "When several degraded states fire at once, banner precedence is deterministic and each banner routes to exactly one help page; the order is the declared DEGRADED_STATES tuple, and the multi-state case is confirmed by the plan 16B-09 first-launch interruption fixture rather than only by the unit assertion here."
      verification: backstop
    - statement: "A refusal payload with no unlock condition still renders a stated condition rather than a blank card; the exact substitute sentence is contracted at execution against the runtime's real refusal payload shape and confirmed by a held-out check."
      verification: backstop
    - statement: "A locked card renders from the runtime's refusal payload synchronously today, so no loading state is reachable; asserting that by construction needs a held-out timing test."
      verification: backstop
    - statement: "A failure to obtain the refusal payload degrades to the generic locked state rather than to a chat surface; the generic path is confirmed by a held-out check against the runtime's real failure mode."
      verification: backstop
    - statement: "Several simultaneous refusal reasons collapse to one card carrying one stated condition; which reason wins is confirmed by a held-out check once more than one refusal reason can fire at once."
      verification: backstop
    - statement: "Several locked cards in one view, such as a practice list with multiple gated items, need a storyboard scenario; confirmed by a held-out check rather than asserted here."
      verification: backstop
    - statement: "A degraded banner must render before, not after, any slow recovery attempt; the ordering is confirmed by a held-out interruption check rather than by construction."
      verification: backstop
  prohibitions:
    - statement: "A locked refusal must not render as a chat turn, a message bubble, a typing indicator, or anything carrying a free-text input; the card states its unlock condition and offers only what legitimately unlocks it."
      status: kept
      verification: flagged-unverified
    - statement: "A locked card must not show a dimmed, blurred, or otherwise present-but-hidden preview of the content it withholds, because withheld content that is in the bytes is not withheld."
      status: kept
      verification: flagged-unverified
    - statement: "Learner-visible copy must not carry a resolved absolute filesystem path; only the bank-author-written basename is ever shown."
      status: kept
      verification: flagged-unverified
    - statement: "A degraded state must not discard the last accepted state or leave the learner with no next action; preserving the prior valid state and naming one safe next step is the whole contract."
      status: kept
      verification: flagged-unverified
    - statement: "A model must not decide how much a refusal reveals; the unlock condition is computed by the runtime and rendered by the surface, and no model output selects it."
      status: kept
      verification: flagged-unverified
  artifacts:
    - "surfaces/ia.py gains DEGRADED_COPY, DEGRADED_ACTIONS, DEGRADED_HELP_CODES, degraded_banner, LOCKED_CARD_TEMPLATE, and locked_refusal_card"
    - "surfaces/daemon.py renders a degraded banner through presentation.state_panel wherever a 16B route can produce one"
    - "tests/degraded_state_roundtrip.py with check_eight_states, check_banner_precedence, check_basename_only, check_banner_help_links_resolve, check_locked_card_shape, and check_locked_card_is_not_chat"
  key_links:
    - "The permission-denied banner is the only banner with a substitution, and that substitution is the one place a filesystem path can reach a learner in this phase. It must call os.path.basename on whatever it is given, including a value that is already a basename, so the rule holds even when a caller passes a full path by mistake."
    - "The locked card's no-leak rule is about bytes, not styling. The withheld content must be absent from the served response, not hidden with a class, because a class is removable in a browser and the response is not."
    - "Banner precedence must read the declared DEGRADED_STATES tuple rather than a second ordering written in the banner function, or two orderings exist and the deterministic-precedence claim depends on which one a caller happens to use."
    - "Every banner's help code must be a member of IA_HELP_CODES from plan 16B-02 and must have an entry in HELP_TABLE from plan 16B-03, asserted as a mapping over the tuple rather than spot-checked, so a state added later without a help entry fails the test that exists to catch it."
---

<objective>
Make every way this phase can fail end in a sentence, a code, and a next step,
and make a refusal look like the locked card the product already uses rather
than like a conversation.

The ROADMAP's Phase 16B goal closes with the requirement that "crash,
cancellation, offline, permission-denied, future-schema, and agent-unavailable
states preserve the last accepted state and expose the next safe action, with a
model-unavailable state still allowing reading, scoring, the authored hint
ladder, evidence, and reports". `16B-UI-SPEC.md`'s Degraded-State Matrix locks
eight rows of exact copy and one next safe action each, and its Locked-Card
Refusal Contract generalizes the shipped RTS-09 hint-tier card to the Socratic
refusal FLOW-02 names.

FLOW-02's own text is the reason the card matters: "a Socratic or tutoring
refusal renders as a locked card stating its unlock condition, never as a chat
exchange (bake-in 2026-08-14, consistent with RTS-09's locked-card contract)".
The card is not a styling choice; it is the visible form of the rule that the
runtime, not the model, decides how much is said.

Decisions already made, cited, and never re-derived here:

- **`16B-UI-SPEC.md` Degraded-State Matrix**, all eight rows, exact copy and
  next safe action, binding verbatim.
- **`16B-UI-SPEC.md` Locked-Card Refusal Contract**, the exact card shape: a
  header of the form `{Step or capability name}, locked`, exactly one sentence
  of the form `Unlocks after {condition}.`, no first person, no encouragement,
  no progress indicator over the card, no dimmed-but-visible preview, and no
  control that could be mistaken for ask again or continue talking.
- **`16B-DECISIONS.md` `## D9`**: path-bearing copy shows the bank-author-written
  basename only, reusing the shipped `lesson.src_unreadable` precedent.
- **`16B-DECISIONS.md` `## D-16B-9`**: banner precedence is the declared
  `DEGRADED_STATES` tuple order and the first member present wins the banner
  slot, with every other fired state still reachable through its own help link.
- **`16B-UI-SPEC.md` Copywriting Contract**, the reused LOCKED strings: the
  model-unavailable sentence and the sparse-evidence sentence are reused
  verbatim and never re-worded.
- **`PLANNING-DIRECTIVES.md` section 4**, non-negotiable number 1: the runtime
  owns disclosure of keyed assessment content.

Purpose: make failure legible and make refusal honest.
Output: eight banners, one locked card, one new test suite.
</objective>

<context>
@.planning/phases/16B-ia-modes-recovery-contract/16B-DECISIONS.md
@.planning/phases/16B-ia-modes-recovery-contract/16B-UI-SPEC.md
@.planning/phases/16B-ia-modes-recovery-contract/16B-RESEARCH.md
@.planning/phases/16B-ia-modes-recovery-contract/16B-PATTERNS.md
@.planning/UI-SPEC.md
@.planning/REQUIREMENTS.md
@surfaces/ia.py
@surfaces/daemon.py
@surfaces/lesson.py
@surfaces/presentation.py
@tests/hint_roundtrip.py
</context>

## Artifacts this phase produces (plan 16B-08 share)

New symbols introduced by this plan, and by nothing earlier:

- `surfaces/ia.py`: `DEGRADED_COPY`, `DEGRADED_ACTIONS`,
  `DEGRADED_HELP_CODES`, `degraded_banner`, `LOCKED_CARD_TEMPLATE`,
  `LOCKED_CARD_HEADER_TEMPLATE`, `locked_refusal_card`.
- `surfaces/daemon.py`: the degraded-banner rendering helper used by the 16B
  route handlers.
- `tests/degraded_state_roundtrip.py` (whole file) and on it:
  `check_eight_states`, `check_banner_precedence`, `check_basename_only`,
  `check_banner_help_links_resolve`, `check_locked_card_shape`,
  `check_locked_card_is_not_chat`, and `main`.

The phase-wide symbol union is repeated in `16B-01-PLAN.md`.

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: the eight degraded banners, their codes, and their next safe actions</name>
  <files>surfaces/ia.py, tests/degraded_state_roundtrip.py</files>
  <behavior>
    - `degraded_banner("offline")` returns a dict with keys `state`, `text`,
      `code`, `token`, and `actions`, whose `text` is the exact Degraded-State
      Matrix sentence for offline and whose `code` is `ia.offline`.
    - `degraded_banner("permission_denied", target="airway_bank.md")` substitutes
      that basename into the sentence.
    - `degraded_banner("permission_denied", target="C:/Users/w/private/airway_bank.md")`
      substitutes `airway_bank.md` and the returned text contains no path
      separator.
    - `degraded_banner("not_a_state")` raises `ValueError` naming the unknown
      state.
    - Every returned `actions` list is non-empty and every action dict has a
      `label` and an `href`.
    - Every returned `token` is the literal `unknown`, because no degraded state
      is a learner error.
  </behavior>
  <read_first>
- `.planning/phases/16B-ia-modes-recovery-contract/16B-UI-SPEC.md`, the
  "Degraded-State Matrix" table in full, all eight rows, both columns.
- `.planning/phases/16B-ia-modes-recovery-contract/16B-UI-SPEC.md`, the Color
  section's final row assigning `--unknown` to every degraded banner and its
  note that none of these states is a learner error.
- `surfaces/ia.py` in full as it stands after plan 16B-07, in particular
  `DEGRADED_STATES`, `IA_HELP_CODES`, and `HELP_TABLE`.
- `surfaces/lesson.py` lines 77 to 90, `STYLE_DEGRADED_COPY` and the `WARN_CSS`
  comment naming the basename rule, and the `os.path.basename(bank_path)` call
  sites near lines 1797, 1821, 1935, and 1947. This is the shipped precedent D9
  reuses.
- `surfaces/presentation.py`, `state_panel`, the shared polite status region
  every banner renders through.
  </read_first>
  <action>
1. Add `DEGRADED_COPY` to `surfaces/ia.py`, a dict over the eight members of
   `DEGRADED_STATES`, each value the Degraded-State Matrix's exact sentence:

   - `crash`: `Restored your last saved position. Nothing was lost since your last saved step.`
   - `cancelled`: `Cancelled. Partial results are marked below and were not saved as final.`
   - `disk_full`: `This save could not complete (disk full or interrupted). Your previous version is intact. Free up space and try again.`
   - `offline`: `You're offline. Reading, practice, scoring, hints, and evidence keep working. Anything that needs a network connection is marked unavailable below.`
   - `permission_denied`: `itembank could not access {target}. Check that the folder is still shared with itembank, then try again.`
   - `future_schema`: `This file was saved by a newer version of itembank. The parts itembank recognizes are shown below; nothing is changed or deleted.`
   - `agent_unavailable`: `Generated help is unavailable. You can keep learning with the lesson and authored hints.`
   - `course_corrupted`: `This course's full record couldn't be loaded. Showing its last valid overview.`

   Add a comment stating that `permission_denied` is the only row with a
   substitution and that `{target}` is always passed through
   `os.path.basename`, and that `agent_unavailable` reuses a LOCKED string from
   the project-level `UI-SPEC.md` Copywriting contract and is never re-worded.

2. Add `DEGRADED_ACTIONS`, a dict over the same eight keys, each a tuple of one
   or two action dicts with `label` and `href`. Use the Degraded-State Matrix's
   own "Next safe action offered" column:

   - `crash`: one action, label `Continue where you left off`, href `/`.
   - `cancelled`: two actions, `Resume this operation` href `/activity`, and
     `Discard the partial results` href `/activity`.
   - `disk_full`: one action, `Try the save again`, href `/`.
   - `offline`: one action, `Keep working offline`, href `/`.
   - `permission_denied`: two actions, `Re-grant access` href `/settings`, and
     `Continue with the rest of the course` href `/`.
   - `future_schema`: one action, `Continue with the recognized parts`, href `/`.
   - `agent_unavailable`: one action, `Continue the authored loop`, href `/`.
   - `course_corrupted`: two actions, `Open last valid overview` and
     `View files`, whose hrefs are supplied by the caller through the
     `course_id` field and default to `/` when it is absent.

   Every action list is non-empty, which is the "expose the next safe action"
   half of the contract made structural.

3. Add `DEGRADED_HELP_CODES`, a dict over the same eight keys mapping each state
   to its help code: `crash` to `ia.crash_recovered`, and every other state `s`
   to `"ia." + s`. Add an assertion-shaped comment stating that every value must
   be a member of `IA_HELP_CODES` and a key of `HELP_TABLE`, which the test
   asserts as a mapping over the tuple.

4. Add `def degraded_banner(state, target=None, course_id=None):` with a
   docstring stating that it returns one banner as a plain dict, that it renders
   nothing itself, that `{target}` is always reduced to a basename per D9, and
   that the banner's token is always `unknown` because no degraded state is a
   learner error. Behavior:

   - Raise `ValueError("unknown degraded state: %r" % state)` when `state` is
     not a member of `DEGRADED_STATES`.
   - `text` is `DEGRADED_COPY[state]`, with `{target}` replaced by
     `os.path.basename(str(target or ""))` when the state is
     `permission_denied`, and with no substitution otherwise.
   - `code` is `DEGRADED_HELP_CODES[state]`.
   - `token` is the literal `unknown`.
   - `actions` is `DEGRADED_ACTIONS[state]` with the `course_corrupted` hrefs
     filled from `course_id` when given, plus one appended action
     `{"label": "Read more about this", "href": "/help/" + code}`, so every
     banner links to exactly one help page.
   - Return `{"state": state, "text": text, "code": code, "token": token,
     "actions": actions}`.

5. Add `def degraded_banner_for(states, **kw):` taking an iterable of state
   names and returning the banner for the first member of `DEGRADED_STATES` that
   appears in it, plus a second key `also_fired` listing every other fired
   state's help code. This is D-16B-9's deterministic precedence, reading the
   declared tuple and no second ordering. Return `None` for an empty iterable.

6. Create `tests/degraded_state_roundtrip.py` following the shipped
   direct-execution convention with its own local `fail(msg)`.

   `check_eight_states()` asserts every behavior in this task's `<behavior>`
   block, plus: `sorted(ia.DEGRADED_COPY) == sorted(ia.DEGRADED_STATES)`, the
   same for `DEGRADED_ACTIONS` and `DEGRADED_HELP_CODES`, and that each of the
   eight `text` values is the exact locked sentence, asserted by literal string
   comparison for all eight and not by substring.

   `check_banner_precedence()` asserts: `degraded_banner_for(["offline",
   "crash"])["state"]` is `crash`; `degraded_banner_for(["course_corrupted",
   "disk_full"])["state"]` is `disk_full`; for every one of the twenty-eight
   unordered pairs of distinct states, the returned state is the one with the
   lower `DEGRADED_STATES` index; `also_fired` lists exactly the other fired
   states' codes; and `degraded_banner_for([])` is `None`.

   `check_basename_only()` asserts: for each of `"airway_bank.md"`,
   `"C:/Users/w/private/airway_bank.md"`,
   `"/home/w/private corpus/airway_bank.md"`, and
   `"..\\..\\secrets\\airway_bank.md"`, the returned text contains
   `airway_bank.md` and contains neither `/` nor `\\`; and that no other banner's
   text contains a path separator for any input.

   `check_banner_help_links_resolve()` asserts every value of
   `DEGRADED_HELP_CODES` is a member of `ia.IA_HELP_CODES` and a key of
   `ia.HELP_TABLE`, and that each banner's `actions` contains exactly one href
   beginning `/help/`.

   Add `main()` printing `"DEGRADED: 4 passed, 0 failed"`.

7. Run:

```
python tests/degraded_state_roundtrip.py
python -c "import sys; sys.path.insert(0,'.'); from surfaces import ia; print(ia.degraded_banner('permission_denied', target='C:/x/y/airway_bank.md')['text'])"
```

   Expected: exit 0, then exactly
   `itembank could not access airway_bank.md. Check that the folder is still shared with itembank, then try again.`

   No em dash characters in any file this task writes.
  </action>
  <verify>
  <automated>python tests/degraded_state_roundtrip.py</automated>
Expected: final line `DEGRADED: 4 passed, 0 failed`, exit 0. The degraded states
are the subject of the task, and the one this check proves hardest is the
path-disclosure case: four different path shapes all reduce to one basename and
none leaves a separator in the rendered sentence.
  </verify>
  <acceptance_criteria>
- `python tests/degraded_state_roundtrip.py` exits 0 with final line
  `DEGRADED: 4 passed, 0 failed`.
- All eight `DEGRADED_COPY` values match the Degraded-State Matrix sentences by
  literal string comparison.
- `degraded_banner("permission_denied", target="C:/x/y/airway_bank.md")["text"]`
  contains `airway_bank.md` and contains neither `/` nor a backslash.
- Every banner's `actions` is non-empty and contains exactly one `/help/` href.
- Every value of `DEGRADED_HELP_CODES` is in `IA_HELP_CODES` and in
  `HELP_TABLE`.
- All twenty-eight state pairs resolve to the lower-indexed member of
  `DEGRADED_STATES`.
- `degraded_banner("not_a_state")` raises `ValueError` naming the state.
- Every banner's `token` is the literal `unknown`.
- No file this task writes contains an em dash character, verified with the
  `chr(0x2014)` form.
  </acceptance_criteria>
  <reversibility rating="costly">The eight sentences are learner-facing copy the
  UI-SPEC locked and Phase 17A will style; the eight codes are a published
  namespace help pages and banners both address. Both were settled by the
  approved UI-SPEC, so this task transcribes rather than decides.</reversibility>
  <done>Eight failures each have a sentence, a code, a help page, and at least
  one thing a learner can do next, and no path escapes.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: the locked refusal card, which is not a chat</name>
  <files>surfaces/ia.py, tests/degraded_state_roundtrip.py</files>
  <behavior>
    - `locked_refusal_card("Second hint tier", "you submit an attempt on this item")`
      returns a dict whose `header` is `Second hint tier, locked` and whose
      `body` is `Unlocks after you submit an attempt on this item.`
    - The returned dict has exactly the keys `header`, `body`, `condition`, and
      `affordance`, and no key carrying withheld content.
    - A condition already ending in a period does not produce a double period.
    - `locked_refusal_card("X", "")` returns a body that is still one complete
      sentence and never the bare string `Unlocks after .`
    - The returned dict contains no key or value matching `message`, `reply`,
      `prompt`, `input`, `send`, or `chat`.
  </behavior>
  <read_first>
- `.planning/phases/16B-ia-modes-recovery-contract/16B-UI-SPEC.md`, the
  "Locked-Card Refusal Contract" section in full, every bullet.
- `.planning/REQUIREMENTS.md`, `FLOW-02` in full, in particular the locked-card
  bake-in sentence.
- `.planning/UI-SPEC.md` section 9, the Agent Interaction Boundaries table and
  the region `[B]` support-region wireframe the card renders into.
- `surfaces/lesson.py`, the shipped hint-tier locked rendering and its no-leak
  discipline, whichever function emits it; find it by searching for the tier
  header text before writing anything, and copy its shape rather than inventing
  a second locked container.
- `tests/hint_roundtrip.py` in full, for how the repository already asserts that
  a locked tier's content is absent from the served bytes rather than merely
  hidden.
  </read_first>
  <action>
1. Add to `surfaces/ia.py`:

```
LOCKED_CARD_HEADER_TEMPLATE = "{name}, locked"
LOCKED_CARD_TEMPLATE = "Unlocks after {condition}."
LOCKED_CARD_NO_CONDITION = "Unlocks after the next authored step."
```

   With a comment stating that `LOCKED_CARD_NO_CONDITION` exists because a
   refusal payload with no stated condition must still render a stated
   condition, never a blank card, and that the exact substitute sentence is this
   plan's own and is carried as a backstop row until the runtime's real refusal
   payload shape is known.

2. Add `def locked_refusal_card(name, condition=""):` with a docstring stating:
   that it returns the card as a plain dict and renders nothing; that the card
   is the general form of the shipped RTS-09 locked hint tier, generalized to
   the Socratic refusal FLOW-02 names; that it carries no withheld content at
   all, so the content it withholds is absent from the bytes rather than hidden
   in them; and that the unlock condition is computed by the runtime and passed
   in, never selected by a model.

   Behavior:
   - `header` is `LOCKED_CARD_HEADER_TEMPLATE.format(name=name)`.
   - `condition` is the stripped input; when it is empty, `body` is
     `LOCKED_CARD_NO_CONDITION`, otherwise `body` is
     `LOCKED_CARD_TEMPLATE.format(condition=condition.rstrip("."))`.
   - `affordance` is `None` when no action legitimately unlocks the card, or a
     single dict `{"label": ..., "href": ...}` when the caller supplies one
     through a keyword argument `affordance`. It is never a form, never a text
     field, and never more than one entry.
   - Return exactly the four keys `header`, `body`, `condition`, and
     `affordance` and nothing else. Accept no parameter carrying the withheld
     content, so the function cannot leak content it was never given.

3. Add `check_locked_card_shape()` and `check_locked_card_is_not_chat()` to
   `tests/degraded_state_roundtrip.py`.

   `check_locked_card_shape` asserts every behavior in this task's `<behavior>`
   block, plus: the body is exactly one sentence, asserted by counting periods
   outside the condition text; the header ends with the literal `, locked`; and
   `set(card) == {"header", "body", "condition", "affordance"}`.

   `check_locked_card_is_not_chat` asserts the negative contract on the
   **rendered** card, not just the dict. Render it through the same helper a
   route would use and assert the resulting markup:
   - contains none of `<input`, `<textarea`, `<form`, `contenteditable`,
     `role="log"`, `aria-live="assertive"`, or the class token `chat`;
   - contains no more than one anchor or button in total;
   - contains no element whose text matches, case-insensitively, any of
     `ask again`, `send`, `reply`, `try asking`, `typing`;
   - contains no `hidden`, `display:none`, `visibility:hidden`,
     `aria-hidden="true"`, or `opacity:0` on any element, which is how a dimmed
     preview would be smuggled in; and
   - contains no first-person pronoun `I` as a standalone word and none of
     `sorry`, `great job`, `keep going`, which is the no-encouragement rule.

   Write the forbidden-literal list as one module-level tuple named
   `FORBIDDEN_IN_LOCKED_CARD` and iterate it, so the assertion is data and a
   later addition is one line.

4. Add `main()` updates: run six checks and print
   `"DEGRADED: 6 passed, 0 failed"`.

5. Run:

```
python tests/degraded_state_roundtrip.py
python -c "import sys; sys.path.insert(0,'.'); from surfaces import ia; c=ia.locked_refusal_card('Second hint tier','you submit an attempt on this item'); print(c['header']); print(c['body']); print(sorted(c))"
```

   Expected: exit 0, then exactly `Second hint tier, locked`, then
   `Unlocks after you submit an attempt on this item.`, then
   `['affordance', 'body', 'condition', 'header']`.

   No em dash characters in any file this task writes.
  </action>
  <verify>
  <automated>python tests/degraded_state_roundtrip.py</automated>
Expected: final line `DEGRADED: 6 passed, 0 failed`, exit 0. The degraded state
this task proves is the empty-condition case: a refusal payload with no stated
condition still renders one complete sentence rather than a blank card or the
fragment `Unlocks after .`
  </verify>
  <acceptance_criteria>
- `python tests/degraded_state_roundtrip.py` exits 0 with final line
  `DEGRADED: 6 passed, 0 failed`.
- `locked_refusal_card("Second hint tier", "you submit an attempt on this item")`
  produces exactly the header `Second hint tier, locked` and the body
  `Unlocks after you submit an attempt on this item.`
- `set(card)` is exactly `{"header", "body", "condition", "affordance"}`.
- `locked_refusal_card("X", "")["body"]` equals `Unlocks after the next authored step.`
- A condition ending in a period produces exactly one trailing period.
- The rendered card contains none of the members of
  `FORBIDDEN_IN_LOCKED_CARD`, and that tuple contains at least the seventeen
  literals listed in step 3.
- `locked_refusal_card`'s signature accepts no parameter that could carry the
  withheld content, asserted by reading
  `inspect.signature(ia.locked_refusal_card)` and checking its parameter names
  are exactly `name`, `condition`, and `affordance`.
- No file this task writes contains an em dash character, verified with the
  `chr(0x2014)` form.
  </acceptance_criteria>
  <reversibility rating="costly">The card shape and the unlock sentence become
  the general refusal grammar for every later surface. The shape was locked by
  the approved UI-SPEC and generalized from shipped RTS-09, so only the
  no-condition substitute sentence is new, and it is carried as a backstop
  row.</reversibility>
  <done>A refusal states its unlock condition in one sentence, carries none of
  the content it withholds, and offers nothing that reads as continuing a
  conversation.</done>
</task>

<task type="auto">
  <name>Task 3: wire the banners into the 16B routes and prove one end to end</name>
  <files>surfaces/daemon.py, tests/degraded_state_roundtrip.py</files>
  <read_first>
- `surfaces/daemon.py`, `handle_activity_get`, `handle_help_get`,
  `handle_course_get`, `handle_course_area_get`, `handle_course_lesson_get`, and
  `handle_index`, all six as they stand after plan 16B-07.
- `surfaces/presentation.py`, `state_panel`, whose `kind`, `status`, and
  `actions` keys are the banner's rendering target.
- `surfaces/ia.py`, `degraded_banner` and `degraded_banner_for` as written in
  Task 1.
- `tests/ia_route_roundtrip.py`, `check_shelf_end_to_end`, whose daemon setup
  this task's end-to-end check reuses in shape.
  </read_first>
  <action>
1. Add one small helper to `surfaces/daemon.py`:

```
def banner_markup(banner):
```

   It takes a `degraded_banner` dict and returns the markup from
   `presentation.state_panel({"kind": banner["token"], "status": banner["text"],
   "actions": banner["actions"]})`, and returns the empty string for `None`. It
   adds no styling and no new element.

2. Wire the banner into the two places a 16B route can actually produce a
   degraded state today, and no others:

   - `handle_index`: when `ia.course_shelf_state` returned at least one card
     with `degraded` True, render
     `banner_markup(ia.degraded_banner("course_corrupted", course_id=<that card's id>))`
     above the card list. When more than one card is degraded, call
     `ia.degraded_banner_for` with the fired states so precedence is the
     declared one rather than the first card encountered.
   - `handle_activity_get`: when `activity_view_state` returned `available`
     False, render `banner_markup(ia.degraded_banner("agent_unavailable"))`
     beneath the existing notice, so the model-unavailable state states the
     LOCKED sentence and offers the authored loop.

   Do **not** wire a banner into a route that cannot produce its state. A crash
   banner, a disk-full banner, an offline banner, a permission-denied banner,
   and a future-schema banner each need a producer this phase does not build;
   they exist as data with tests, and plan 16B-09 and plan 16B-10 exercise the
   ones their fixtures can actually cause. State that boundary in a comment.

3. Add `check_banner_end_to_end()` to `tests/degraded_state_roundtrip.py`. It
   prepares a temp dir with `fixtures/course_storyboard_corpus.build_corrupted_course`,
   starts a real daemon, and asserts against the served `GET /`:
   - Status 200.
   - The body contains the exact `course_corrupted` sentence.
   - The body contains `href="/help/ia.course_corrupted"` at least once.
   - The body contains `Open last valid overview` and `View files`.
   - The body contains no resolved absolute path, asserted by checking the body
     contains no substring equal to the temp directory's own path.
   - Then follow the help link: `GET /help/ia.course_corrupted` returns 200 and
     carries its own cause sentence, so the banner is provably not a dead end.

   Then, with `ITEMBANK_IA_NO_JOURNAL=1` set, assert `GET /activity` carries the
   exact `agent_unavailable` sentence and a `/help/ia.agent_unavailable` link.

4. Update `main()` to run seven checks and print
   `"DEGRADED: 7 passed, 0 failed"`. Run the full suite and the guard:

```
python tests/degraded_state_roundtrip.py
python tests/ia_route_roundtrip.py
for t in tests/*.py; do python "$t" || exit 1; done
python itembank.py guard .
```

   Expected: `DEGRADED: 7 passed, 0 failed` and exit 0; exit 0; exit 0;
   `0 offending files`.

   No em dash characters in any file this task writes.
  </action>
  <verify>
  <automated>python tests/degraded_state_roundtrip.py && python tests/ia_route_roundtrip.py</automated>
Expected: `DEGRADED: 7 passed, 0 failed` and exit 0, then exit 0. The degraded
states this task proves end to end are the corrupted course on the shelf and the
model-unavailable state on the Activity view, each carrying its locked sentence,
its help link, and a next action, with the help link followed and confirmed to
resolve.
  </verify>
  <acceptance_criteria>
- `python tests/degraded_state_roundtrip.py` exits 0 with final line
  `DEGRADED: 7 passed, 0 failed`.
- The served shelf for the corrupted fixture contains the exact
  `course_corrupted` sentence, a `/help/ia.course_corrupted` link, and both
  named actions.
- Following that help link returns 200 with its own cause sentence.
- The served shelf body contains no substring equal to the temp directory's
  absolute path.
- `GET /activity` under `ITEMBANK_IA_NO_JOURNAL=1` contains the exact
  `agent_unavailable` sentence and a `/help/ia.agent_unavailable` link.
- `banner_markup(None)` returns the empty string.
- The five unwired states are wired nowhere, asserted by grepping
  `surfaces/daemon.py` for `degraded_banner("` and finding exactly the two
  literal state names `course_corrupted` and `agent_unavailable`.
- `for t in tests/*.py; do python "$t" || exit 1; done` exits 0 and
  `python itembank.py guard .` reports `0 offending files`.
- No file this task writes contains an em dash character, verified with the
  `chr(0x2014)` form.
  </acceptance_criteria>
  <reversibility rating="reversible">One rendering helper and two call sites.
  </reversibility>
  <done>Two degraded states are produced, rendered, and followed to their help
  pages by a real request, and the six that no 16B route can cause are data with
  tests rather than wiring with no producer.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| filesystem path to learner-visible copy | The permission-denied banner is the one place in this phase where a path can reach a page. |
| withheld assessment content to served bytes | A locked card exists precisely because something must not be disclosed yet. |
| model output to disclosure decision | A tutoring model can argue for revealing more. |
| failure state to next action | A learner in a degraded state has the least context and the most need for a correct next step. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-16B-08-01 | Information Disclosure | a resolved absolute path in the permission-denied banner | high | mitigate | `degraded_banner` always applies `os.path.basename` to `{target}`, including to a value already reduced; four path shapes are asserted to render one basename with no separator, and the end-to-end check asserts the served body contains no substring equal to the temp directory path. |
| T-16B-08-02 | Information Disclosure | withheld content present in the bytes of a locked card but visually hidden | critical | mitigate | `locked_refusal_card` accepts no parameter that could carry the withheld content, asserted by inspecting its signature; the rendered-markup check forbids `hidden`, `display:none`, `visibility:hidden`, `aria-hidden="true"`, and `opacity:0`, which are the ways a dimmed preview would arrive. |
| T-16B-08-03 | Elevation of Privilege | a refusal rendered as a chat turn, inviting a learner to argue a model into disclosing more | high | mitigate | The rendered card is scanned against `FORBIDDEN_IN_LOCKED_CARD`, which bans inputs, forms, contenteditable, log roles, chat class tokens, and every ask-again and reply literal, and permits at most one anchor or button. |
| T-16B-08-04 | Repudiation | a model selecting the unlock condition | high | mitigate | The condition is a parameter the caller supplies from the runtime; `surfaces/ia.py` imports no model adapter, asserted structurally by the offline scan in plan 16B-03 which runs over the same file. |
| T-16B-08-05 | Denial of Service | a degraded state leaving the learner with no next action | high | mitigate | Every `DEGRADED_ACTIONS` entry is non-empty and every banner appends its own help link, asserted for all eight states. |
| T-16B-08-06 | Spoofing | a banner naming a help page that does not exist | medium | mitigate | `check_banner_help_links_resolve` asserts every `DEGRADED_HELP_CODES` value is a member of `IA_HELP_CODES` and a key of `HELP_TABLE`, and the end-to-end check follows one link and asserts a 200 with its cause sentence. |
| T-16B-08-07 | Repudiation | non-deterministic banner precedence when several states fire | medium | mitigate | `degraded_banner_for` reads the declared `DEGRADED_STATES` tuple and no second ordering; all twenty-eight state pairs are asserted, and the multi-state runtime case is carried as a backstop confirmed by plan 16B-09's interruption fixture. |
| T-16B-08-08 | Tampering | script injection through a banner's substituted target | medium | mitigate | The only substitution is a basename, and every banner is rendered through `presentation.state_panel`, whose `esc` call escapes the status text. |
| T-16B-08-09 | Tampering | supply chain: a third-party dependency introduced by this plan | high | mitigate | None is added; every change is standard library only. Per `PLANNING-DIRECTIVES.md` section 4a the absence of dependencies is explicitly not the mitigation: the mitigation is that any dependency ever added here is vendored at a pinned version with a recorded checksum and a named license review, following the KaTeX precedent in `09-03-PLAN.md`. |
</threat_model>

<out_of_scope>
Refused by this plan, by name:

- **No producer for the six unwired states.** Crash detection, cancellation
  handling, disk-full detection, offline detection, permission-denied detection,
  and future-schema detection each belong to the code path that can actually
  encounter them, most of which is Phase 14A's journal and recovery work. This
  plan builds the banners and their tests; plans 16B-09 and 16B-10 wire the ones
  their fixtures can cause.
- No chat surface, no message thread, no free-text refusal input, anywhere.
- No change to the shipped hint ladder, its tiers, or its locked rendering. The
  locked card generalizes RTS-09's shape; it does not modify it.
- No model call, no elaboration layer, no generated-synthesis container.
- No new visual constant and no CSS rule. Banners render through the shipped
  `state_panel` and the card through the shipped support region.
- No change to `runtime.py` or `evidence.py`. Disclosure authority is theirs and
  this plan renders their decisions rather than making any.
</out_of_scope>

<flagged_assumptions>
- **`LOCKED_CARD_NO_CONDITION`'s sentence is this plan's own.** The UI-SPEC locks
  the `Unlocks after {condition}.` form but does not state what a card does when
  the payload carries no condition. The LockedRefusalCard empty row is a
  backstop, and this substitute exists so the card is never blank. If a reviewer
  or the real runtime payload shape suggests different wording, it is one
  constant and one assertion.

- **Five of the seven LockedRefusalCard rows and one DegradedStateBanner row are
  backstop markers.** Loading, error, partial, zero-one-many, and the empty case
  all depend on the runtime's real refusal payload shape and on views that can
  hold several gated items, neither of which exists in 16B. At verification
  time, no explicit evidence for a backstop row is `insufficient_spec` and needs
  a human, never a silent pass.

- **The APP-03 ordering edge is carried as a backstop.** The unit assertion over
  all twenty-eight state pairs is real, but the runtime case where several
  states genuinely fire at once needs a producer this plan does not build; plan
  16B-09's first-launch interruption fixture is where that is confirmed.

- **The shipped hint-tier locked rendering is located at execution, not cited by
  line here.** Task 2's `<read_first>` requires finding it by searching for the
  tier header text before writing anything, because citing a line number that
  moved would send the executor to the wrong function. The requirement is to
  copy its shape and not to invent a second locked container.
</flagged_assumptions>

<summary_obligations>
`16B-08-SUMMARY.md` records: the final line of every verify command; all eight
banner sentences as rendered, quoted, beside the UI-SPEC rows they transcribe;
the four path shapes tested for the basename rule and the rendered result of
each; the exact contents of `FORBIDDEN_IN_LOCKED_CARD`; where the shipped
hint-tier locked rendering was found and how its shape was reused; which two
states were wired into routes and the grep output proving no third was; the
served body confirmation that no temp directory path appeared; which truth was
verified by which command with its actual stdout; and any deviation from this
plan with its reason.
</summary_obligations>

<output>
Create
`.planning/phases/16B-ia-modes-recovery-contract/16B-08-SUMMARY.md`
when done.
</output>
