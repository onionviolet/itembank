---
phase: 17A-visual-system-component-foundation
plan: 08
type: execute
wave: 3
depends_on: ["17A-01", "17A-02"]
files_modified:
  - surfaces/home.py
  - surfaces/daemon.py
  - schemas/settings.schema.json
  - itembank.json
  - tests/home_roundtrip.py
autonomous: true
requirements: [VISUAL-01]
must_haves:
  truths:
    - "The home is a shelf with resume state and one next action, not a file list."
    - "All four home modes ship and are selectable by setting; shelf is the default Weibao chose on 2026-08-21."
    - "Every card states what it knows and what it does not. A card never invents progress it cannot compute."
    - "The next action states why it is next, in one sentence, sourced from evidence and not from a model."
    - "The agent has its own area, and a proposal about an object also surfaces on that object."
  artifacts:
    - "surfaces/home.py, the four home modes over one data function."
    - "tests/home_roundtrip.py covering each mode, the empty case, the no-evidence case, and the setting switch."
  key_links:
    - "Resume state comes from the existing session files, not a new store."
    - "The next action comes from selection/retention, never from a model."
---

<objective>
Replace the file list with the home 16B already designed and Weibao approved on
2026-08-20, and ship the three home shapes he did not pick as settings rather
than deleting them.
</objective>

<context>
@.planning/EXEC-CONTEXT.md
@fixtures/visual_system_flow.json
@surfaces/visual_fixture.py
@surfaces/daemon.py
</context>

<findings>
Measured 2026-08-21.

1. **The home is already designed and rendered.** The `shelf_resume` stage in
   `fixtures/visual_system_flow.json` carries `kind: "home"`: course cards with
   resume state, one `next_action` with a `why`, and an activity list.
   `surfaces/visual_fixture.py` renders it in all three directions. Nothing in
   the daemon has ever used it.

2. **The daemon home is pre-16B.** `handle_index` lists bank and day-plan
   stems. It is a directory listing, and it was the only home a learner could
   reach until the reading link landed on 2026-08-21.

3. **There is no course object in code.** `course.md` says so in its own first
   paragraph: "No tool parses it. Phase 14B owns the durable course schema."
   The shelf therefore cannot show real course cards yet, and this plan must
   not pretend otherwise.

4. **What DOES exist for a card today:** the bank and its item count, session
   files with a cursor and responses, the evidence store, and
   `selection`/`retention` for choosing what is next and why. That is enough
   for a real shelf with honest labels; it is not enough for the word "course".

5. **Weibao chose the shelf on 2026-08-21**, and asked for the other options to
   be implemented rather than dropped, and for the agent area to keep room for
   the placements he did not pick.
</findings>

<tasks>
<task type="auto">
  <name>Task 1: one data function, honest about what it does not know</name>
  <files>surfaces/home.py, tests/home_roundtrip.py</files>
  <action>
Write the test first.

`home_state(root)` returns one dict every mode renders from: cards, a single
next action or None, and an activity list. It reads the banks the daemon
already found, the newest session per bank, the evidence store, and
`selection`/`retention` for the next action.

Each card carries what is known and a typed reason for anything that is not.
A bank with no session is `not_started`, not `0%`. A bank whose objectives
cannot be resolved says so rather than showing a denominator it invented.
**A card never displays progress it could not compute.**

The next action carries a `why` of one sentence, built from evidence: which
objective, how many times it was missed, and over what denominator. If
evidence cannot support a reason, the next action is None and the home says
what would make one possible. **No model produces this text.** The runtime
chooses what is next, the same as everywhere else.

Call it a bank until 14B lands. The word "course" on a screen that cannot
parse a course is the kind of lie this project has rules against. Leave one
named seam so 14B swaps the noun and the grouping without touching the modes.
  </action>
  <verify>python tests/home_roundtrip.py exits 0 with an empty root, a bank with no session, a bank mid-session, and a bank with evidence.</verify>
</task>

<task type="auto">
  <name>Task 2: four modes, one setting, shelf by default</name>
  <files>surfaces/home.py, schemas/settings.schema.json, itembank.json, tests/home_roundtrip.py</files>
  <action>
Add `home` to settings: `shelf` (default), `next-action`, `agent`, `split`.
Additive, with a schema description naming what each shows and who it suits.

- `shelf`: cards, the next action with its why, activity. The chosen default.
- `next-action`: the single next action full width with its reason, everything
  else one click behind it.
- `agent`: the agent area is the home, with card state beside it as context.
- `split`: cards and agent side by side, and it must degrade to `shelf` at
  phone width rather than crushing two columns.

All four render from `home_state`. A mode is a template, never a second data
path, or the four will disagree about what is true. An unknown value in the
setting falls back to `shelf` and says so once, rather than failing to serve a
home at all.
  </action>
  <verify>python tests/home_roundtrip.py, python tests/daemon_roundtrip.py, python tests/config_roundtrip.py all exit 0.</verify>
</task>

<task type="auto">
  <name>Task 3: the daemon serves it, and the file list stays reachable</name>
  <files>surfaces/daemon.py, tests/home_roundtrip.py</files>
  <action>
`GET /` renders the configured home. The old stem list moves to `/banks` and
stays linked from the home, because it is the only view that shows a stem
collision and the daemon still needs somewhere to report one.

The empty case keeps its current copy: a daemon serving nothing says so and
says what to add.

Reading stays first on every card, per the 2026-08-21 fix.
  </action>
  <verify>python tests/daemon_roundtrip.py and python tests/home_roundtrip.py exit 0, and python itembank.py guard . exits 0.</verify>
</task>

<task type="auto">
  <name>Task 4: the agent keeps its area, and proposals surface in place</name>
  <files>surfaces/home.py, surfaces/daemon.py, tests/home_roundtrip.py</files>
  <action>
Weibao chose "own area, proposals surface in place, with room for everything
else so it is not lost."

The Agent area stays whole. In addition, a pending proposal about an object
appears on that object: a lesson revision on the lesson page, a bank extension
on the bank's card. One badge, the count, and a link into the Agent area for
the full diff. The proposal is never accepted from the badge, because
acceptance belongs to one place.

Keep the room he asked for: the Agent area holds a named, empty slot for
inline affordances (ask about this item, revise this lesson) so the third
placement option is registered rather than discarded. It renders as "not built
yet" with the option name, not as a hidden TODO.

Until 17A-07 lands there are no real proposals. Render the zero case honestly
and do not fabricate one.
  </action>
  <verify>python tests/home_roundtrip.py exits 0 including the zero-proposal case.</verify>
</task>
</tasks>

<out_of_scope>
No course object; that is 14B, and this plan says "bank" until it lands. No
scoring, marking, or key disclosure on the home. No model-written next action.
No new evidence store. No deletion of the three home modes Weibao did not pick.
</out_of_scope>

<summary_obligations>
Per the 2026-08-21 budget rule, write a summary ONLY if this plan is left
incomplete or a measured fact contradicts it. Otherwise the commit messages
are the record.
</summary_obligations>
