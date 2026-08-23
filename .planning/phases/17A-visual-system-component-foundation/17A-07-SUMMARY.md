# 17A-07 summary

Written as the run goes, one append per task, so a cut-off run still leaves
an honest record.

## Task 1: the run-propose-accept state machine

Shipped in `37bd995`. `surfaces/agent_operation.py` and
`tests/agent_operation_roundtrip.py` (12 checks, exit 0, no network).

### The four states

| State | When | What it carries |
|---|---|---|
| `idle` | before any run | the note that nothing is running |
| `running` | inside `start`, between request built and result | skill, interaction id |
| `proposed` | an `ok` invoke result | draft, citations, target rel path, object kind, expected base fingerprint, bounded diff, provider row |
| `settled` | every ending: unavailable codes, refusals, conflicts, accepts | typed code or ok flag, reason, next action where applicable, entry id and revision on accept |

`running` is the shape the machine passes through while `invoke` is on the
wire; `start` returns `proposed` or `settled`.

### Exact copy for every adapter code

`NEXT_ACTIONS` in `surfaces/agent_operation.py` holds one sentence per entry
in `model_adapter.ADAPTER_CODES`, all fourteen:

- `adapter.profile_disabled`: no backend active; choose one in Settings,
  Model; studying, scoring and authored hints are unaffected.
- `adapter.profile_invalid`: profile has a field this transport does not
  take (for example `base_url` instead of `endpoint`).
- `adapter.profile_unknown`: active name matches no profile; pick again.
- `adapter.unreachable`: nothing answered at the endpoint; start the model
  server; nothing was written.
- `adapter.timeout`: no answer in time; retry or raise `timeout_seconds`.
- `adapter.malformed_response`: body was not JSON; check the endpoint URL.
- `adapter.http_error`: HTTP error from the endpoint; check URL and key.
- `adapter.executable_missing`: the backend command was not found.
- `adapter.subprocess_error`: the command failed; run it once in a terminal.
- `adapter.provider_refused`: the backend refused; check its logs.
- `adapter.request_invalid`: itembank built a rejected request; a bug.
- `adapter.output_cap_exceeded`: raise `max_output_bytes` or ask smaller.
- `adapter.transport_unknown`: transport not shipped; choose a listed one.
- `adapter.internal_error`: unexpected boundary failure; nothing written.

The import raises if a code is missing from the map, so a new adapter code
cannot ship with no copy; the suite asserts set equality as well.

### The single journal entry, and its id shape

One accepted proposal calls `journal.commit_operation` exactly once. The
journal records it as one prepared entry resolved by one applied entry
(the applied entry's `resolves_entry` names the prepared one); the suite
counts both at exactly one each and refuses on any refused line. The
settled state carries `entry_id`, the id of the applied entry, in the
module's existing opaque hex form (32 lowercase hex characters, minted by
`journal.new_entry_id`). A second `accept` returns the settled state
unchanged and appends nothing.

### The undo path

No second mechanism was invented. The settled state carries the applied
entry id; undo is `journal.undo(base, entry_id, actor_kind, actor_name)`,
which restores the entry's recorded before-image as a new forward
`restore` revision. Task 3 proves this end to end.

### What report_only refuses, and how it says so

`accept` under `auditor_autonomy: report_only` returns a settled refusal:
"auditor_autonomy is report_only, so drafts are shown but never written.
To let an accepted draft become a revision, set auditor_autonomy to
'draft_and_approve' in itembank.json." Any other unknown value, including
a missing setting, reads as report_only. Proposing is never blocked;
only the write is.

### Decisions made inside the plan's gaps

- The write target comes from an `agent_runs` section in the settings
  document keyed by skill id (`target` plus object `kind`), never from
  the model candidate, so a stray answer cannot choose what gets
  overwritten. A skill with no entry settles with `agent.no_run_target`
  naming the skill and the key.
- A well-formed JSON answer that is not a draft settles with the page-level
  code `agent.candidate_invalid` rather than proposing an empty change.
- Object identity follows the registry: a path with a previous applied row
  keeps its object id (`edit_in_place`, revisions chain); a new path mints
  one (`mint`, revision 1).

## Task 2: the Agent tab drives it, and says what it cannot do

Shipped in `aa7b5bd`. `surfaces/visual_fixture.py` and the same suite
(17 checks, exit 0). All five verification commands exit 0:
`agent_operation_roundtrip`, `local_harness_roundtrip`,
`visual_system_roundtrip`, `journal_roundtrip`, and `itembank.py guard .`.

### Which skills rendered unavailable, and why

The list is read from `.claude/skills/*/SKILL.md` frontmatter, not from the
fixture. Stub descriptions render as unavailable with their own reason:

- `discovery-and-binding`: not usable yet; its command surface has not
  shipped.
- `legacy-upgrade`: same reason.
- `lesson-authoring`: same reason.
- `media-intake`: same reason.

`absorb-book`, `author-bank`, `build-course`, `curriculum-design`,
`guiding-questions`, and `ocr` render runnable. A runnable row states its
contract in one line: it proposes a bounded diff of one file and writes
only on accept, once, through the journal.

### What the page renders

- Each of the four states with the machine's own `STATE_COPY` sentence,
  under "What a run does".
- Every adapter unavailable code with its `NEXT_ACTIONS` copy under
  "If a skill cannot reach a model", so the shipped no-active-profile
  state reads first-class and says studying, scoring and authored hints
  are unaffected.
- One sentence separating the two paths: the framed console is the
  open-ended one; this list is the one itembank drives.

### Deliberate deferral

Browser-clickable activation would need a served GET or POST route owned
by `server.py`. `server.py` is not in this plan's file list, so activation
from a browser is out of scope here. The run-propose-accept loop itself is
proven end to end against a stubbed endpoint in task 3. A page rendered
without a course root keeps the old fixture list, which is what the
prototype pages use.

