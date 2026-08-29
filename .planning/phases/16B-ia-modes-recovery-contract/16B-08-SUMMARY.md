# 16B-08 summary

Plan `16B-08`, wave 8, three tasks, all complete. Eight degraded states each
carry an exact sentence, a code, a help page, and at least one next safe action;
banner precedence is the declared tuple over all twenty-eight pairs; and a
locked refusal card states its unlock condition while carrying none of the
content it withholds.

## Command output, final line of every verify block

| Command | Final line |
|---|---|
| `python3 tests/degraded_state_roundtrip.py` | `DEGRADED: 7 passed, 0 failed`, exit 0 |
| `python3 tests/ia_route_roundtrip.py` | `IA ROUTES: 19 passed, 0 failed`, exit 0 |
| `python3 -c "... degraded_banner('permission_denied', target='C:/x/y/airway_bank.md')['text']"` | `itembank could not access airway_bank.md. Check that the folder is still shared with itembank, then try again.` |
| `python3 -c "... locked_refusal_card(...)"` | `Second hint tier, locked`, `Unlocks after you submit an attempt on this item.`, `['affordance', 'body', 'condition', 'header']` |
| the structural no-write ban | `no write path` |
| `python3 itembank.py guard .` | `0 offending files` |
| the whole suite, 86 files | `0 failing` |

## What was proven

**Eight exact sentences.** Every `DEGRADED_COPY` value is compared to the
Degraded-State Matrix sentence by literal string equality, not by substring, so
a reworded sentence fails rather than passing on a shared fragment.

**No path escapes.** Four path shapes, a bare basename, a Windows absolute path,
a POSIX path containing a space, and a relative traversal, all reduce to
`airway_bank.md`, and the resulting text carries neither a forward slash nor a
backslash. The check also sweeps all eight states against all four shapes, so a
future state that interpolates a target cannot leak one silently.

**Precedence is one declared order.** All twenty-eight unordered pairs resolve
to the lower-indexed `DEGRADED_STATES` member, and `also_fired` lists exactly the
other fired state's help code, so a state that loses the banner slot stays
reachable rather than disappearing. An empty fired set returns `None` rather
than an empty banner.

**Every banner links exactly one help page, and every page exists.** Each of the
eight `DEGRADED_HELP_CODES` values is asserted to be an `IA_HELP_CODES` member
and a `HELP_TABLE` key, and each banner carries exactly one `/help/` href. The
end-to-end check then follows one of those links over HTTP and asserts the help
page carries its own cause sentence, so the banner is provably not a dead end.

**No degraded state is coloured as a learner error.** Every banner's token is
the literal `unknown`, asserted for all eight.

**The locked card is not a chat.** The rendered markup contains none of the
nineteen members of `FORBIDDEN_IN_LOCKED_CARD`, carries at most one control, and
uses no first-person pronoun. `locked_refusal_card`'s signature is asserted to be
exactly `name`, `condition`, `affordance`, so the function accepts no parameter
that could carry the withheld content: what is withheld is absent from the bytes
rather than hidden inside them.

**The empty-condition case renders a real sentence.** An unstated condition
yields `Unlocks after the next authored step.` rather than a blank card or the
fragment `Unlocks after .`, and a condition already ending in a period does not
double it.

## The wiring boundary, stated

Only two 16B routes can produce a degraded state today, and only those two are
wired:

- `handle_index` renders the `course_corrupted` banner above the card list when
  the shelf returned at least one degraded card, through `degraded_banner_for`
  so precedence is the declared order rather than the first card encountered.
- `handle_activity_get` renders the `agent_unavailable` banner beneath the
  not-yet-available notice, so the model-unavailable state states its LOCKED
  sentence and offers the authored loop.

The crash, disk-full, offline, permission-denied, and future-schema banners each
need a producer this phase does not build. They exist as data with their own
tests and are not wired into a route that cannot cause them, because a state
nothing can reach, asserted as if it could, is a false claim of coverage. The
boundary is stated in `banner_markup`'s docstring.

## Deviations from this plan, with reasons

**1. `DEGRADED_TOKEN` is a named constant rather than a bare literal.** The plan
said the token is "the literal `unknown`". It is, and the constant names why: no
degraded state is a learner error. Behaviour is identical.

**2. `FORBIDDEN_IN_LOCKED_CARD` has nineteen entries, not seventeen.** The plan
required at least seventeen and listed them across two bullets; the tuple carries
all of them plus `role="log"` and `aria-live="assertive"` counted separately from
the markup group. The test asserts the count is at least seventeen.

**3. `python3` for `python`, and the full-suite criterion run with
`ANKI_CONNECT_URL=http://127.0.0.1:1/`.** Carried forward from
`16B-02-SUMMARY.md`.

## Which truth was verified by which command

| Truth | Command | Actual result |
|---|---|---|
| Eight states, eight exact sentences | `check_eight_states` | all eight equal by literal comparison |
| Every state offers a next safe action | same check | every `actions` list non-empty, every action complete |
| An unknown state is refused by name | same check | `ValueError` naming `not_a_state` |
| No degraded state is a learner error | same check | token `unknown` for all eight |
| Precedence is the declared tuple | `check_banner_precedence` | 28 pairs, all to the lower index |
| A losing state stays reachable | same check | `also_fired` carries its help code |
| No path escapes any banner | `check_basename_only` | 4 shapes times 8 states, no separator |
| Every banner links one existing help page | `check_banner_help_links_resolve` | 8 codes, all in `IA_HELP_CODES` and `HELP_TABLE` |
| A refusal states one condition in one sentence | `check_locked_card_shape` | exact header and body, four keys, one period |
| A refusal cannot carry what it withholds | same check | signature is exactly `name`, `condition`, `affordance` |
| A refusal is not a conversation | `check_locked_card_is_not_chat` | 19 forbidden literals absent, at most one control, no first person |
| A corrupted course produces a real banner on a real page | `check_banner_end_to_end` | sentence, help link, both actions, no absolute path |
| The banner's help link resolves | same check | 200 with its own cause sentence |
| The model-unavailable state states the LOCKED sentence | same check | present on `/activity` with its help link |

## Artifacts changed

- `surfaces/ia.py`: `DEGRADED_COPY`, `DEGRADED_ACTIONS`, `DEGRADED_HELP_CODES`,
  `DEGRADED_TOKEN`, `degraded_banner`, `degraded_banner_for`,
  `LOCKED_CARD_HEADER_TEMPLATE`, `LOCKED_CARD_TEMPLATE`,
  `LOCKED_CARD_NO_CONDITION`, `locked_refusal_card`.
- `surfaces/daemon.py`: `banner_markup`, the banner branch in
  `_course_shelf_body`, and the banner appended in `handle_activity_get`.
- `tests/degraded_state_roundtrip.py`, new: `FORBIDDEN_IN_LOCKED_CARD` and
  seven checks.
