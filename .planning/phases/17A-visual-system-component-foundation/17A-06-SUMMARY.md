# 17A-06 summary

Written 2026-08-21. Task 1 was resolved before this session and its record is
`17A-06-DECISIONS.md`. This file covers Task 2, the part of Task 3 that is
done, and the part that is not.

## What shipped

| Commit | What |
|---|---|
| `3199680` | `build(17A-06)` the pin note, and the ETARGET and PyPI-collision findings |
| `790d428` | `feat(17A-06)` the `local-qwen` profile, still inactive |
| `d2a3f5f` | `feat(17A-06)` the embedded console, and the egress-label fix |
| `e13182e` | `test(17A-06)` `tests/local_harness_roundtrip.py` |
| `9fb3061` | `build(17A-06)` the locked dsh tree at the tested version |

## The exact working profile

```json
{
  "name": "local-qwen",
  "transport": "openai_compatible",
  "endpoint": "http://127.0.0.1:11434/v1/chat/completions",
  "model": "qwen3.8-27b:latest",
  "timeout_seconds": 120,
  "max_output_bytes": 262144,
  "context_window": 32768
}
```

`model_backend.active` stays empty. A fresh install still reaches no model.

Two facts measured while writing this, both worth keeping:

- **The field is `endpoint`.** A profile written with `base_url` fails with
  `settings.invalid_value`, surfaced through `invoke` as
  `adapter.profile_invalid`. It has its own check.
- **`resolve_profile` refuses every name while `active` is empty,** including
  a name passed explicitly. Switching a local model on is one settings edit,
  not two. The suite activates the shipped record in memory rather than
  changing the file.

## The five unavailable states and their copy

Every one is typed, carries the interaction id, and returns no candidate.
None raises.

| Condition | Code | What the learner is told |
|---|---|---|
| No active profile | `adapter.profile_disabled` | "No backend is active. Choose one before starting a skill." |
| Nothing listening | `adapter.unreachable` | "endpoint unreachable: <url>" |
| No answer in time | `adapter.timeout` | "endpoint timed out after <n>s" |
| Body is not JSON | `adapter.malformed_response` | "endpoint returned non-JSON body" |
| `base_url` instead of `endpoint` | `adapter.profile_invalid` | "profile 'local-qwen' (openai_compatible) requires an endpoint" |

A sixth, `adapter.transport_unknown`, covers a `dsh_stdio` row written before
that module exists. Studying, scoring, and authored hints are untouched by any
of them.

## The embedded console

The Agent tab frames `@deepseek-ai/dsh` at `http://127.0.0.1:3080`.

- The frame element carries `lang="en"` and an English `title`. The served
  document is `<html lang="zh-CN">` and a framed document's language cannot be
  reassigned from outside, so the panel says in words that the tool sets its
  own interface language rather than claiming `en` on content itembank does
  not own.
- There is no JavaScript on this page, so it cannot probe whether the console
  is running. It names the command, `dsh web --port 3080`, instead.
- The panel does not claim where the console's text goes. `dsh` reads its own
  configuration and itembank does not set it.

### The theming probe (open question 4)

`dsh web --help` exposes four options: `--host`, `--port`, `--trusted-host`,
`-h`. **None of them is theming.** The indigo accent does not reach inside the
frame through the CLI. The plugin route (`dsh plugin --profile web add`) and
the `cordis.patch.yml` row replacement named in `17A-06-DECISIONS.md` were not
investigated. Today the tab visibly hands off to a different-looking tool,
which is the honest option and costs nothing to keep.

## What is NOT done, and it is half of Task 3

The plan's Task 3 asks for two things. The embed is one. The other is not
built:

> choose a skill, run it against the active profile through
> `model_adapter.invoke`, show the draft as a bounded diff, and on accept call
> `journal.commit_operation` exactly once.

**The skill buttons on the Agent tab are still fixture buttons.** They run
nothing, `model_adapter.invoke` is not called from that page, and no journal
entry is produced. The summary obligation to record "the single journal entry
a run produces, and the undo path" therefore has no honest answer yet: there
is no run.

What is true today is the boundary, not the wiring. `journal.commit_operation`
already does compare-and-swap with an operation log and a prior revision, and
the Agent tab's journal panel already reads the real operation journal through
`live_journal`, with reads and external edits correctly marked not-undoable.
The writer exists and the reader exists. Nothing joins them from this page.

Also still true: `report_only` autonomy is displayed but does not yet disable
an accept control, because there is no accept control to disable.

## The egress label, fixed in passing

`live_backends` decided local by matching a list of transport names, and that
list did not contain `openai_compatible`, the one transport the adapter itself
tags `"local"`. The shipped `local-qwen` row would have rendered "Item text and
lesson prose leave this machine." Local is now derived from the endpoint host,
so an `openai_compatible` profile pointing at a real remote server is still
correctly called hosted. The guard was proven by reverting the fix and
watching the suite fail.

## The pin, and why it took three attempts

Recorded in full in `deps/dsh-pins.txt`. Short version: the top-level version
is not a pin. `dsh` declares roughly sixty first-party dependencies and every
one is a caret range, so a lockfile built from `0.1.0-rc.7` alone resolved 185
of 191 dsh-scoped packages to `0.1.0-rc.8` while the verified install has
`rc.7` throughout.

Three findings that cost time and should not be rediscovered:

1. **A fresh resolve fails outright.** `@aws-sdk/core ^3.977.9` is demanded by
   a transitive package and does not exist; the registry's highest is
   `3.977.8`, which is what the working install has. Overridden.
2. **`deepseek-harness-sdk` does not exist on PyPI.** `17A-06-DECISIONS.md`
   names it as the package to pin for the stdio seam. PyPI does carry
   `deepseek-harness` 0.2.0 and it is an unrelated third-party client from a
   different author. The Python seam has no pinnable artifact today, which is
   a real obstacle to the not-done half of Task 3.
3. **Nested lockfile keys are easy to miss.** The first override list was
   derived from keys starting with `node_modules/@deepseek-ai/`, which skips
   packages nested under `node_modules/@deepseek-ai/dsh/node_modules/`. Three
   stayed at `rc.8`. The lockfile check caught them.

589 packages locked, every one with an integrity hash. Reproduce with
`cd deps/dsh && npm ci`.

## Verification

    python tests/local_harness_roundtrip.py     10 checks, exit 0
    python tests/visual_system_roundtrip.py     exit 0
    python tests/model_adapter_roundtrip.py     exit 0
    python itembank.py guard .                  exit 0

Pre-existing and not caused by this plan: `itembank.json` fails settings-schema
validation on three missing keys (`teaching`, `selection.profiles`,
`reader.gloss_hover`). Present before the profile was added.
