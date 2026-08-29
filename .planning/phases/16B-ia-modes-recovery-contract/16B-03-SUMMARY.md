# 16B-03 summary

Plan `16B-03`, wave 3, three tasks, all complete. Every named error code this
phase can produce now routes to a local page stating its cause and its next safe
action, and the whole path is proven offline both structurally and behaviourally.

## Command output, final line of every verify block

| Command | Final line |
|---|---|
| `python3 tests/ia_route_roundtrip.py` | `IA ROUTES: 10 passed, 0 failed`, exit 0 |
| `python3 tests/daemon_roundtrip.py` | exit 0 |
| `python3 -c "... print(len(ia.HELP_TABLE), sorted(ia.HELP_TABLE)==list(ia.IA_HELP_CODES), ia.help_entry('nope')['cause'])"` | `12 True No additional help is available for this yet.` |
| `python3 itembank.py help-code ia.offline` | a JSON object whose `cause` begins `You're offline.`, exit 0 |
| `python3 itembank.py help-code not.a.code` | `"known": false`, exit 0 |
| the structural no-write ban command | `no write path` |
| `python3 itembank.py guard .` | `0 offending files` |
| the whole suite, 85 files | `0 failing` |

## What was proven

**The bijection, asserted over the tuple rather than a list in the test.** All
twelve `IA_HELP_CODES` members return 200 over HTTP, each page carries that
code's exact `cause` string, and each page's `Error code:` line names exactly
one code. The reverse direction is asserted too: the set of codes reachable
through the route equals `set(ia.IA_HELP_CODES)`. A code added to the tuple later
without a help entry fails `check_help_table_shape`'s
`sorted(ia.HELP_TABLE) == list(ia.IA_HELP_CODES)` assertion.

**The unknown-code path answers rather than refuses.**
`GET /help/ia.no_such_code` is 200 carrying
`No additional help is available for this yet.` `help_entry` raises nothing for
`None`, `""`, `0`, or an unrecognized dotted string.

**The bounded character class refuses malformed codes at dispatch.**
`GET /help/UPPERCASE`, `GET /help/..%2fetc%2fpasswd`, and `GET /help/a/b` are
each 404, produced by `_dispatch` before `handle_help_get` runs and before any
lookup key is constructed. No 404 body carries a traceback or a filesystem path.

**Offline, proven two ways because neither is sufficient alone.** Structurally,
`_scan_for_network` over `surfaces/ia.py`'s comment-stripped source returns an
empty list for all seven markers. Behaviourally, `GET /help/ia.offline` returns
200 with its exact cause sentence from a daemon started with no granted root, no
configured model backend, `ITEMBANK_NO_NETWORK=1` set, and every proxy variable
removed from the child environment.

**The structural check was demonstrated able to fail.**
`_scan_for_network("import socket")` returns a non-empty list, asserted in the
test itself. A check nobody has observed failing is a check nobody has tested.

**Every degraded state has a help code.** All eight `DEGRADED_STATES` members map
into `IA_HELP_CODES` under the rule that `crash` maps to `ia.crash_recovered` and
every other state `s` maps to `"ia." + s`, asserted rather than assumed.

## Deviations from this plan, with reasons

**1. The "no model backend configured" fixture uses `model.active == ""`, which
is neither of the two options the plan named.** Task 3 step 1 said to write
`{"model_backend": "none"}` if the schema's `model_backend` enum admits `"none"`,
and otherwise to write no `itembank.json` at all and record which was used and
why. The schema does carry a top-level `model_backend` key, but it is an **object**
with no enum and therefore no `"none"` member: its own description states that
"an empty `active` or an empty `profiles` array disables model calls entirely, so
a fresh install never phones a provider". The test therefore writes
`{"model": {"active": "", "profiles": []}}`, which loads through the
unknown-key-preserved path and leaves `model_backend` at its restrictive
shipped default of an empty `active`, so no backend is configured. This is stronger than the plan's stated
fallback: writing no file at all would have relied on the shipped default rather
than asserting the state, so the state is written explicitly instead.

**2. Served copy is compared after `html.unescape`.** Several help sentences
carry apostrophes, which the page correctly escapes to `&#x27;`. The assertions
unescape the body before comparing rather than weakening the escaping. Same
treatment as `16B-02`.

**3. `python3` was substituted for `python` in every command.** Carried forward
from `16B-01`.

**4. The full-suite acceptance criterion was run with
`ANKI_CONNECT_URL=http://127.0.0.1:1/`.** Recorded in full in `16B-02-SUMMARY.md`:
three shipped tests assert the exact locked "Anki closed" copy and Anki Desktop
is running on this machine. With Anki unreachable the whole 85-file suite reports
`0 failing`. The cause is environmental and predates 16B.

## Which truth was verified by which command

| Truth | Command | Actual result |
|---|---|---|
| Twelve entries, complete and duplicate-free against the tuple | `check_help_table_shape` | `sorted(HELP_TABLE) == list(IA_HELP_CODES)`, 12 rows |
| Each code routes to one page, each page names one code | `check_help_route_bijection` | 12 pages, 200 each, exact cause, one code named |
| An unknown code is a 200 sentence | `check_help_unknown_code` | fallback sentence present |
| A malformed code is a path-free 404 | same check | three shapes, all 404, no traceback, no path |
| The help path opens no socket | `check_help_is_offline`, structural half | empty marker list |
| The structural check can fail | same check, negative control | non-empty list for `import socket` |
| Help resolves with no backend and no proxy | same check, behavioural half | 200 with the exact cause sentence |
| The route is one row in the shipped structures | `check_route_cli_inventory`, `check_route_order_is_load_bearing` | both pass |

## Artifacts changed

- `surfaces/ia.py`: `HELP_FALLBACK_COPY`, `HELP_TABLE` (twelve entries),
  `help_entry`, `cmd_help_code`.
- `surfaces/daemon.py`: `HELP_GET_RE` beside its sibling regex constants, one
  appended `ROUTES` entry in the trailing stem-parameterised block, one
  `ROUTE_CLI` entry, and `handle_help_get`.
- `surfaces/cli.py`: `cmd_help_code` added to the `surfaces.ia` import and
  `add_parser("help-code")`.
- `tests/ia_route_roundtrip.py`: `_scan_for_network`, `check_help_table_shape`,
  `check_help_route_bijection`, `check_help_unknown_code`,
  `check_help_is_offline`.
