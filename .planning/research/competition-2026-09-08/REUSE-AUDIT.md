# Reuse audit: OpenMAIC generation and DeepTutor reader grounding

Date: 2026-09-08. Status: proposed prototype work. This audit inspected pinned source, without installing dependencies or running either service.

## Recommendation

**R1. Absorb DeepTutor's selection-window algorithm first, as a small Itembank-owned implementation.** Port the behavior of `normalized_with_map`, `selection_range`, and `grounding_context` from `deeptutor/reading/_grounding.py`, then place it behind one future reader-assistance request builder. The slice is about 70 lines of stdlib Python plus focused tests. It gives a model only a verified selection and a bounded source window. It does not import DeepTutor's server, extension protocol, LLM client, quiz generation, or assessment behavior.

This is the best first slice because Itembank is Python and already treats source locators, generated assistance, evidence, and hint authority as separate concerns. OpenMAIC's most reusable generation primitive is sound but TypeScript-only. Adding its package would also add its DSL and a JavaScript package boundary before proving a learner-facing use.

Acceptance gate for R1:

1. The server resolves source text from Itembank's canonical source binding and locator. Client-submitted `visible_text`, anchors, and selections are never trusted.
2. A requested selection must match the stored unit after whitespace normalization. If it does not, return an unavailable or validation result before any model call.
3. The model payload contains the verified selection and at most 6,000 source characters centered on it. Record the source object, locator, accepted revision fingerprint, window policy, backend class, and request fingerprint.
4. Assistance remains an unaccepted draft or permitted hint. `runtime.py:score_response` remains the only scoring authority. Constructed responses remain pending review.
5. A missing source, stale binding, invalid selection, model failure, cancel, or oversized unit preserves accepted content and emits a recoverable result. Retry is explicit and journaled, not an invisible second request.

Suggested Itembank tests, named before implementation:

- `tests/reader_grounding_roundtrip.py::test_whitespace_normalized_selection_maps_to_canonical_source_span`
- `tests/reader_grounding_roundtrip.py::test_forged_selection_does_not_invoke_adapter`
- `tests/reader_grounding_roundtrip.py::test_bounded_window_contains_verified_late_selection`
- `tests/reader_grounding_roundtrip.py::test_assistance_is_not_a_score_or_accepted_artifact`
- Existing `tests/agent_roundtrip.py` and the relevant `tests/*_roundtrip.py` gate for the chosen reader route.

## Inspected reuse candidates

| Candidate | Inspected evidence | Dependencies and license | Fit and disposition |
|---|---|---|---|
| DeepTutor `normalized_with_map`, `selection_range`, `grounding_context` | The algorithm maps collapsed whitespace back to the original source span and centers a bounded context window on a selection. Its two direct tests cover whitespace recovery and a late selection inside the 6,000-character window. | The module imports only `json` and typing, with `ReadingContext` needed only for `grounded_prompt`. DeepTutor is Apache-2.0. Preserve the Apache notice and attribution if code rather than behavior is copied. | **Prototype now.** Copy or independently implement the three pure functions. Do not copy `grounded_prompt`, which is tied to DeepTutor's Pydantic context model. |
| DeepTutor `_verified_selection` and `run_extension_action` | The API resolves unit text and source anchor from `ReadingStore`, rejects a required forged selection, caps the context schema, validates returned shapes, and returns recoverable 503s for broken or timed-out extensions. | Depends on FastAPI, Pydantic, `ReadingStore`, multi-user access checks, registry, and thread workers. DeepTutor's base install pulls a large app dependency set including providers, RAG, parsing, and web components. Apache-2.0 covers the repository. | **Pattern only.** Its server-owned-value rule and recoverable result contract should be retained. Do not import the router or extension framework. |
| OpenMAIC `withGenerationRetry`, `isRetryableGenerationError`, `isAbortError` | A cancellation-aware exponential retry helper classifies 408, 409, 425, 429, 5xx, transport failures, and nested provider errors as retryable. It treats abort and 400, 401, 403, 404, and 422 as final. Tests cover null results, no retry for 401, abort before work, abort during backoff, and nested errors. | The file itself has no package imports, but `@openmaic/generation` depends on `@openmaic/dsl`, `jsonrepair`, KaTeX, nanoid, and partial-json. The generation package is MIT. The DSL is also MIT. | **Prototype later.** Reuse its retry taxonomy only after Itembank has a bounded source-to-draft operation. Translate the behavior into Python instead of adding Node and the scene DSL. Keep Itembank's explicit retry and operation journal rules. |
| OpenMAIC `generateSceneOutlinesFromRequirements` | The public package uses caller-supplied `AICallFn`, returns parsed scene outlines, and keeps provider selection and persistence outside the package. The README states content generation can return `null` with `prompt-unavailable` or `invalid-model-output` callbacks. | Same generation package graph plus an OpenMAIC scene-outline and DSL contract. MIT applies to this package. | **Reference, not import.** Its output is slide-scene oriented and has no Itembank objective, source-rights, accepted-revision, or review contract. It must not directly create an accepted lesson, bank, or score. |

## Boundary comparison

| Concern | Verified upstream behavior | Required Itembank handling |
|---|---|---|
| Grounding | DeepTutor's router ignores browser `visible_text`, loads stored text by material and locator, and verifies selection against it. | Resolve source content through the canonical binding and locator. Keep the browser as a requestor only. |
| Failure and recovery | DeepTutor returns recoverable unavailability for extension failures. A timed-out synchronous extension opens its private circuit because Python cannot safely kill the worker. OpenMAIC aborts rather than retrying a canceled operation. | Preserve Itembank's last accepted revision. Return a typed unavailable, invalid-selection, stale-binding, or canceled state. Record the operation so retry has a parent and cannot duplicate a durable write. |
| Generation | OpenMAIC has a caller-owned model seam and a retry helper. Its larger generators parse model JSON into its own scene format. | Generator output is a candidate. Require source citations, objective mapping, deterministic validation, visible review, and compare-and-swap acceptance before it becomes a course artifact. |
| Scoring | DeepTutor reader extensions can return a quiz-shaped result. OpenMAIC has separate choice and LLM short-answer grading paths. | Neither upstream scoring path may enter Itembank. The runtime owns score, session, keyed disclosure, and evidence. A model may offer advisory feedback only within the existing disclosure tier. |

## Exact source pointers

All links are pinned to the inspected revisions.

- [DeepTutor grounding helpers](https://github.com/HKUDS/DeepTutor/blob/7a96bba1ae03401644c17763a2411c28aff3dcc9/deeptutor/reading/_grounding.py) and [their focused tests](https://github.com/HKUDS/DeepTutor/blob/7a96bba1ae03401644c17763a2411c28aff3dcc9/tests/reading/test_grounding.py).
- [DeepTutor selection-verifying route](https://github.com/HKUDS/DeepTutor/blob/7a96bba1ae03401644c17763a2411c28aff3dcc9/deeptutor/api/routers/reading_extensions.py), [failure and timeout tests](https://github.com/HKUDS/DeepTutor/blob/7a96bba1ae03401644c17763a2411c28aff3dcc9/tests/reading/test_extension_router.py), and [Apache-2.0 license](https://github.com/HKUDS/DeepTutor/blob/7a96bba1ae03401644c17763a2411c28aff3dcc9/LICENSE).
- [OpenMAIC generation API](https://github.com/THU-MAIC/OpenMAIC/blob/29735f10d0081859ac3db1a50a0cc92f46436004/packages/%40openmaic/generation/README.md), [retry implementation](https://github.com/THU-MAIC/OpenMAIC/blob/29735f10d0081859ac3db1a50a0cc92f46436004/packages/%40openmaic/generation/src/generation-retry.ts), [retry tests](https://github.com/THU-MAIC/OpenMAIC/blob/29735f10d0081859ac3db1a50a0cc92f46436004/packages/%40openmaic/generation/test/generation-retry.test.ts), and [MIT license](https://github.com/THU-MAIC/OpenMAIC/blob/29735f10d0081859ac3db1a50a0cc92f46436004/LICENSE).
- [OpenMAIC generation package manifest](https://github.com/THU-MAIC/OpenMAIC/blob/29735f10d0081859ac3db1a50a0cc92f46436004/packages/%40openmaic/generation/package.json) and [DSL manifest](https://github.com/THU-MAIC/OpenMAIC/blob/29735f10d0081859ac3db1a50a0cc92f46436004/packages/%40openmaic/dsl/package.json).

## Documentation claims and unverified unknowns

Verified source evidence supports the symbols, package manifests, licenses, and tests named above. The prior ecosystem comparison's statements about broader OpenMAIC and DeepTutor product behavior were documentation and repository claims unless linked to a symbol here.

This audit did not install package artifacts, resolve transitive lockfiles, run upstream tests, inspect published npm tarballs, exercise model calls, inspect license metadata for every transitive dependency, test a source with a real Itembank reader route, or perform an accessibility and clean-machine recovery review. The pinned repository licenses cover the inspected repositories, not learner sources, model providers, generated media, or all vendored and transitive assets. OpenMAIC's root README identifies a separately licensed LGPL `mathml2omml` workspace package. It is outside the recommended slices and must stay outside any copied dependency graph.

No upstream code, dependency, service, fork, or package was added. The next decision is whether to implement R1 as a bounded Itembank prototype with the stated acceptance gate.
