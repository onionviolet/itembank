# Phase 19C verification

**Status:** backend repair verified. The shared adapter now speaks the local
provider protocol, the public seeding flow resolves the active profile, and
unavailable director results retain their operation id. The real rerun accepted
nothing and left the disposable bank unchanged.

## 2026-09-07 repair rerun

- The real public director command reached `qwen3.5:4b` and returned a candidate
  that passed `director.validate_recommendation`. The result was intentionally
  not bound. Its operation id is `70d3cdd7a1244833`.
- The public seed command resolved `local-qwen` through
  `model_adapter.invoke` and executed the locked pipeline against the disposable
  EMT bank. The model draft failed deterministic checks after the retry cap, so
  the result was `0 drafted, 0 accepted, 0 skipped, 1 failed deterministic
  checks`. No write was offered or performed.
- The disposable bank fingerprint remained
  `7f9917e6e77d929be8829c34d685035bfd5282a4665b99004adf35daeac2ba09`.
- Focused gates passed: `tests/model_adapter_roundtrip.py`,
  `tests/director_roundtrip.py`, and `tests/seeding_roundtrip.py` (25 tests).
  `itembank guard .` passed with zero offending files.

The repaired CLI also prints the ordered stage path before presenting results,
so a learner or reviewer can see where a seeding run progressed. Candidate
quality remains model-dependent and the deterministic lint gate correctly
prevented a weak real draft from reaching acceptance.

## Environment and retained record

- Machine: Apple M5 MacBook Air, 16 GB, arm64.
- Endpoint: Ollama 0.31.1 at loopback port 11434.
- Installed model: `qwen3.5:4b`, 4.7B parameters, Q4_K_M.
- A direct OpenAI-compatible chat request returned `backend-ready`. This proves
  endpoint and model availability. It does not prove the product adapter.
- Diagnostic root:
  `/Users/weiwei/Documents/itembank-courses/_diagnostics/19c-backend-on`.
- Canonical EMT fingerprints before and after the run were identical:
  `course.md` `e7a432fd88a216167bf80be846d3835a77b6337a99f25de7bc3362aa5992d00f`,
  lesson `3cb2d6fea3f04519e548e42a43e1f982379e1ef84f73b40312692840d2d1064b`,
  and bank `7f9917e6e77d929be8829c34d685035bfd5282a4665b99004adf35daeac2ba09`.

| Record | SHA-256 | Inspected result |
|---|---|---|
| `director-recommend.txt` | `b2071f3f28c16244651632da3577f6b8282a5ff5e4e546c2fd4d8c1fb5d62695` | `adapter.http_error`, no recommendation, no binding. |
| `director-recommend-pass.txt` | `82eefd78e91791531ccd975318c66a6c6a65f240f4cf1cf250703c5550d602f9` | One objective in and one untreated entry out, reason `backend-unavailable`. |
| `seeding.txt` | `c9ded2f804b9b8cdbd49617780a5b860f127765d040c77127210b7543fdc86b0` | Public seed command refused with the named offline fallback before drafting. |

The director journal retained two local-only calls. Each disclosed one 37-byte
approved span and a 914-byte request. Operation ids were
`e41c64fa49fd41e0` and `68f3b7e07b004679`. No evidence was included.

## Plain judgment

The model itself is reachable and capable of answering a basic chat request.
The product cannot currently use it. This was not a weak recommendation that a
reviewer could reject. The director sent a request the endpoint rejected with
HTTP 400, so no candidate reached schema validation. The seeding command never
reached the active profile at all.

No generated treatment or question exists to accept. The useful result of 19C
is the first real diagnosis of the product-owned path, plus a safe active local
profile. Core reading, lint, scoring, evidence, and authored fallback behavior
remained available.

## Routed defects

### F19C-01: OpenAI-compatible transport does not speak the provider protocol

`model_adapter._transport_openai_compatible` posts the internal itembank request
envelope directly to `/v1/chat/completions`. Ollama accepts the endpoint when
given `model`, `messages`, and `stream`, but rejected the product request with
HTTP 400. The same transport also treats the whole provider response as the
candidate instead of extracting and parsing the assistant message.

- Owner: Phase 8 model-adapter transport and response normalization.
- Failure evidence: both director transcripts and journal entries 15 to 18.
- Required repair gate: a real local endpoint receives a provider-valid request,
  returns a candidate that passes `director.validate_recommendation`, and the
  retained egress record still describes the exact content sent.
- Scope ruling: not repaired in 19C because the phase seed forbids new backend
  capability and requires defects to be routed.

### F19C-02: seeding remains on its pre-Phase-8 private adapter seam

`surfaces.seeding.run_seeding_run` defaults to `NoBackendAdapter`. The public
CLI passes no adapter and never loads `itembank.json`, so activating
`local-qwen` cannot affect seeding. The module documentation still says Phase 8
is not built.

- Owner: Phase 03.2 seeding and Phase 8 adapter integration seam.
- Failure evidence: `seeding.txt` and the symbol path from
  `surfaces.cli.cmd_seed` to `run_seeding_run`.
- Required repair gate: the public seed command resolves the active registered
  backend through the one model-adapter boundary, reaches all six stages on a
  disposable real bank, and accepts nothing without the existing human gate.
- Scope ruling: not repaired in 19C because connecting a second adapter contract
  is implementation work beyond a settings-backed diagnostic.

### F19C-03: unavailable director output drops its recorded operation id

The journal records both failed operation ids, but `director.recommend_once`
returns no `operation_id` on its unavailable branch. The course surface then
prints an empty id beside undo instructions that refer to the id above.

- Owner: Phase 15A director return contract and the Phase 19A-05 surface that
  renders it.
- Failure evidence: `director-recommend.txt` plus journal entries 15 to 18.
- Required repair gate: an unavailable recommendation returns the recorded
  operation id, and replay or undo can address it from the surface response.
- Scope ruling: routed only. No Phase 19A file was changed.

## Deterministic gates

- `python3 tests/model_adapter_roundtrip.py`: pass.
- `python3 tests/local_harness_roundtrip.py`: pass.
- `python3 tests/director_roundtrip.py`: pass.
- `python3 tests/seeding_roundtrip.py`: pass, 24 tests.
- `python3 itembank.py guard .`: pass, zero offending files.
- `python3 scripts/preflight.py --quick`: pass after the summary-format repair;
  every quick gate that ran passed.
- `python3 scripts/preflight.py`: failed on the inherited concurrent 19A
  snapshot. `tests/binding_roundtrip.py` raises `course.CourseError` because
  source object `5c5bc6b17baa44c6` is no longer found in the course journal
  registry. The clean-tree gate also reports every inherited uncommitted file,
  including the active 19A implementation. The summary-format failure found in
  the same run was repaired locally. The full gate has not been rerun because
  the binding failure is unchanged and its owner is outside 19C.

## Gate verdict and next dependency

Phase 19C's diagnostic and repair gates pass. F19C-01, F19C-02, and F19C-03 are
repaired and covered by focused tests. The same real diagnostic was rerun. The
director produced a valid unbound recommendation, and seeding reached the
shared backend while deterministic validation refused its weak draft.

The plan commit is blocked until the concurrent 19A lane restores the full
preflight. Committing before that would violate the repository rule that a plan
commit follows its required green gate. Phase 19C changes remain isolated to
the seven files named by `19C-01-PLAN.md`.

Human legs: none are required to judge this diagnostic. Human review remains
required before any future model candidate becomes accepted course content.
