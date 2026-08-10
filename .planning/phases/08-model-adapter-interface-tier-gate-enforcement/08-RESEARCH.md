# Phase 8: Model Adapter Interface & Tier-Gate Enforcement - Research

**Researched:** 2026-08-08
**Domain:** Provider-neutral tutoring-model adapter, fail-closed learner-output gate, and append-only review evidence
**Confidence:** MEDIUM

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

### Adapter contract
- **D-01:** One adapter request/response contract covers both hosted CLI and local OpenAI-compatible backends. Requests declare operation (`hint` or `rubric_review`), immutable interaction id, model/backend metadata, item context, learner response, permitted tier, and a version. Responses contain structured content, provider metadata, and refusal/error status; surfaces never parse provider-native output.
- **D-02:** Backend selection is exclusively configuration (`model_backend`); switching backend requires no caller changes. The hosted CLI is a subprocess adapter and the local endpoint is an HTTP adapter, both behind the same function boundary.
- **D-03:** Provider-specific options live under named backend profiles so multiple providers can coexist and the user can switch later. Secrets remain environment/config references and are never copied into evidence.
- **D-04:** Every call has a strict timeout and bounded output. Unreachable, malformed, timed-out, or refused calls return a typed unavailable result; authored hints, scoring, lessons, reports, and marking continue.

### Tier-gate enforcement
- **D-05:** Prompting is defense in depth, never the gate. The runtime validates model output after generation and before any surface receives it.
- **D-06:** The gate is a first-class, independently tested component with three layers: schema validation; deterministic checks against answer/key and content reserved for higher tiers; and a conservative ambiguity rule that drops uncertain output. It never rewrites a leaking hint into something that might change meaning.
- **D-07:** Model output is structured into claims/spans with source labels where possible, enabling the runtime to compare each claim with the facts permitted at the current tier. The planner/researcher must design and adversarially test the actual detection mechanism before adapter plumbing is considered complete.
- **D-08:** Gate outcomes are `pass`, `drop`, or `unavailable`, with machine-readable reasons. Only `pass` content may enter a learner-facing payload. A drop falls back to the authored tier if available and otherwise says the generated hint is unavailable without revealing why.
- **D-09:** The gate receives the full private item and the Phase 6 permitted tier, but the browser receives neither. Tier progression remains exclusively Phase 6 state; the adapter cannot request, infer, or advance it. — **Reversibility:** costly — this boundary is consumed by every future model operation and must be stable before publication.

### Error-specific hints
- **D-10:** Hint requests include the learner's most recent genuine wrong response and relevant authored analysis. The generated hint must address that error, not give a generic restatement.
- **D-11:** Generated hints augment one unlocked authored tier; they do not replace the authored ladder. Offline and model-disabled sessions remain pedagogically complete.
- **D-12:** At most one model generation is attempted for a given interaction id unless the user explicitly retries; retries retain a parent id so cost and repeated failures are visible.

### Rubric suggestions
- **D-13:** A rubric-review response is a per-point suggestion with pass/fail/uncertain and rationale. It appends a model-interaction event and a pending review proposal linked to the original short-answer response.
- **D-14:** Model rubric output never mutates the response score or creates an accepted mark. A human must explicitly accept or replace it through the existing mark event path; accepted evidence identifies the human action and may reference the proposal.

### Evidence, privacy, and observability
- **D-15:** Every attempted interaction is logged, including backend/profile, operation, timing, request fingerprint, outcome, gate result, permitted tier, and returned learner-facing content when passed. Raw secrets and provider credentials are never logged.
- **D-16:** Dropped output is recoverable for local audit only when it can be stored without exposing secrets through normal reports; normal learner/session retrieval returns the outcome and reason code, not leaked text. Research should decide the safest local audit representation.
- **D-17:** Hosted-provider transmission of item text is already accepted in PROJECT.md, but each interaction records whether it used a hosted or local backend so later audits can distinguish exposure.

### the agent's Discretion

These are delegated choices. The tier detector is explicitly not considered solved by this discussion: research and the planning model own its concrete algorithm and adversarial evaluation. They may combine compatible detectors, but must fail closed and preserve the runtime boundary.

### Deferred Ideas (OUT OF SCOPE)

- Model-authored bank changes and retry-to-clean authoring — Phase 11.
- Model-driven selection — out of scope; selection remains rule-based.
- Accepted automated scoring of prose — explicitly out of scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|---|---|---|
| TEACH-04 | The model writes an error-specific hint from the item, key, rationale, and wrong answer. | Bounded hint-plan contract ties the model-selected learner-response span to one permitted authored-tier fact. |
| TEACH-05 | Runtime drops output beyond the unlocked tier. | Fail-closed manifest gate and runtime-owned renderer; no provider text is sent to a learner. |
| TEACH-06 | A learner cannot prompt the model into revealing. | Provider output is treated as untrusted; schema, reference, and ambiguity checks execute after generation. |
| TEACH-07 | Generated hints are recoverable evidence. | New append-only interaction event records a passed rendered payload and a safe descriptor for drops. |
| TEACH-08 | `short` answers get per-rubric-point checklist evidence. | Keep proposal separate from the existing human mark and expose point-by-point pending suggestions. |
| TEACH-09 | Model rubric verdict is pending, never accepted evidence. | Add a proposal event/type; only existing `mark_event(..., marker="human")` can settle a mark. |
| MODEL-01 | Hosted CLI and local OpenAI-compatible endpoint share one interface. | One typed `invoke(request, profile)` boundary normalizes both transports. |
| MODEL-02 | Backend switch is configuration-only. | Named profile resolver under `model_backend`; caller receives no backend-specific type. |
| MODEL-03 | Model failure never blocks study. | Typed unavailable outcome and authored fallback in the runtime path. |
| MODEL-04 | Agent usage contract is explicit. | Publish permissions, disclosure, retry, evidence, and manual-marking constraints beside the adapter contract. |
| MODEL-05 | A model never scores structured work or writes accepted evidence. | Proposal-only rubric path; no model result reaches `score_response()` or the human mark writer. |
</phase_requirements>

## Summary

Phase 8 is primarily a trusted-boundary phase, not an HTTP or subprocess phase. The repository already assigns all scoring and learner-visible private/public separation to the runtime: `public_item()` constructs the pre-answer payload and `explain_payload()` is the post-answer boundary. [VERIFIED: runtime.py:27-48,258-283] The new adapter must therefore be an optional runtime capability whose inputs may contain the private item, but whose provider-native output is never a surface payload. The roadmap explicitly requires the same behavior when the backend is offline: only generated augmentation goes quiet. [VERIFIED: .planning/ROADMAP.md:429-433]

The recommended detector is deliberately stronger than a post-hoc free-text keyword filter: make the model return a **bounded hint plan**, not learner-visible free prose. The gate resolves every referenced learner-response span and authored-fact ID against a manifest built by the runtime for exactly the unlocked Phase 6 tier. It accepts only an exact schema with no unknown fields, one response-specific focus span, and allowed facts; it drops every malformed, unknown, higher-tier, or ungrounded result. The runtime then renders the small fixed set of tutoring moves from that plan. [ASSUMED] This is the only deterministic design here that can make the requested no-leak guarantee without trusting a second model to judge the first.

OWASP identifies LLM output as an untrusted boundary and recommends validating outputs before returning them, using structured schemas and allowlisted actions where possible. [CITED: https://cheatsheetseries.owasp.org/cheatsheets/RAG_Security_Cheat_Sheet.html] Its sensitive-disclosure guidance also says prompt restrictions can be bypassed, which directly supports D-05's runtime gate rather than prompt-only approach. [CITED: https://genai.owasp.org/llmrisk/llm022025-sensitive-information-disclosure/]

**Primary recommendation:** Use a stdlib-only, provider-neutral `invoke` boundary plus a first-class fail-closed `tier_gate`; providers return a constrained plan and the runtime, not a model, renders the learner-facing augmentation.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|---|---|---|---|
| Backend profile selection and secret reference resolution | API / Backend | — | Configuration is read inside the local runtime; browser input must not choose a backend or supply credentials. [VERIFIED: surfaces/settings.py:86-125; .planning/phases/08-model-adapter-interface-tier-gate-enforcement/08-CONTEXT.md:17-20] |
| Hosted CLI/local HTTP transport normalization | API / Backend | External provider process/service | Only the adapter knows transport details; all callers receive one typed response shape. [VERIFIED: .planning/phases/08-model-adapter-interface-tier-gate-enforcement/08-CONTEXT.md:17-20] |
| Tier manifest construction and gate decision | API / Backend | — | It requires the private item plus Phase 6 state, both intentionally withheld from the browser. [VERIFIED: .planning/phases/08-model-adapter-interface-tier-gate-enforcement/08-CONTEXT.md:23-27] |
| Learner-facing generated augmentation | API / Backend | Browser / Client | Runtime renders the accepted plan and sends only that payload; browser only presents it. [ASSUMED] |
| Model interaction/proposal audit trail | Database / Storage | API / Backend | The append-only evidence log remains the authoritative record. [VERIFIED: evidence.py:1-14,398-403] |
| Human acceptance/replacement of rubric suggestions | API / Backend | Browser / Client | Existing marks are separate facts about a response and only accept `marker="human"`. [VERIFIED: evidence.py:1027-1080] |

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---|---|---|---|
| Python standard library | Python 3.13.5 installed; CI runs 3.11 | Adapter, schema validation, subprocess transport, HTTP transport, JSON and evidence serialization | The project constraint is stdlib-only and CI proves the supported floor is Python 3.11. [VERIFIED: environment probe; .github/workflows/ci.yml:7-13] |
| `schema_validate.py` | in-repo | Strictly validate the adapter's bounded response/plan schema | It rejects any schema keyword it does not implement rather than silently claiming validation. Quote: `SUPPORTED = frozenset([ "type", "properties", "required", "additionalProperties", "enum", "const", "items", "minItems", "minLength", "minimum", "maximum", "$defs", "$ref", "oneOf", ])`. [VERIFIED: schema_validate.py:23-33] |
| `evidence.py` | in-repo | Append interaction and proposal events through the sole writer | `append_event()` is the one place that decides recorded versus duplicate evidence. [VERIFIED: evidence.py:398-403] |

### Supporting

| Library | Version | Purpose | When to Use |
|---|---|---|---|
| `subprocess` | Python stdlib | Hosted CLI adapter | Pass a configured argument vector, `shell=False`, a timeout, and bounded captured output; never interpolate a learner response into a shell command. [CITED: https://docs.python.org/3.11/library/subprocess.html] |
| `urllib.request` / `urllib.error` | Python stdlib | Local OpenAI-compatible HTTP adapter | POST a bounded JSON body and convert `HTTPError`, `URLError`, timeout, malformed JSON, and oversized body to the typed unavailable result. [CITED: https://docs.python.org/3/library/urllib.request.html; https://docs.python.org/3/howto/urllib2.html] |
| `hashlib` | Python stdlib | Request/output fingerprints and safe audit descriptors | Use only a digest for correlation/audit; do not use it as a secrecy claim. The existing project uses SHA-256 as change detection, not a security boundary. [VERIFIED: evidence.py:16-18] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|---|---|---|
| Bounded plan + runtime renderer | Free-form model hint plus keyword/embedding filter | Reject. A finite lexical detector cannot establish that arbitrary prose does not paraphrase a key; prompt instructions are bypassable. [CITED: https://genai.owasp.org/llmrisk/llm022025-sensitive-information-disclosure/] |
| `subprocess` plus `urllib` | Provider SDKs | Reject: they violate the project's no-external-dependency constraint and make hosted/local paths less uniform. [VERIFIED: .planning/PROJECT.md:223-230] |
| Array of named profiles with runtime lookup | Object keyed by arbitrary profile name | Use the array. The current in-repo validator does not implement `patternProperties` or value-valued `additionalProperties`; a dynamic object map would look validated while not being enforceable. Quote: `SUPPORTED = frozenset([... "additionalProperties", ...])`. [VERIFIED: schema_validate.py:23-33] |

**Installation:** None — do not add a package. [VERIFIED: .planning/PROJECT.md:223-230]

## Architecture Patterns

### System Architecture Diagram

```text
CLI hint / daemon hint route
            |
            v
  Runtime loads private item + Phase 6 permitted tier
            |
            +--> manifest builder (allowed fact IDs, protected facts, learner spans)
            |
            v
 provider-neutral adapter request (immutable interaction ID)
            |
       +----+--------------------------+
       |                               |
       v                               v
 hosted CLI subprocess           local OpenAI-compatible HTTP
       |                               |
       +---------- normalized typed adapter response ----------+
                                                        |
                                                        v
                                            tier gate: schema -> references
                                            -> deterministic policy -> ambiguity
                                                        |
                         +------------------------------+-----------------------------+
                         |                              |                             |
                         v                              v                             v
                    pass: runtime renders          drop: authored tier          unavailable: authored
                    bounded hint-plan              fallback/no disclosure       tier fallback/no disclosure
                         |                              |                             |
                         +------------------------------+-----------------------------+
                                                        |
                                                        v
                                        explicit learner payload (browser has no key/tier)
                                                        |
                                                        v
                         append-only model-interaction/proposal evidence (no secret/raw drop text)
```

### Recommended Project Structure

```text
model_adapter.py       # typed request/result, profile resolution, subprocess + HTTP transports
tier_gate.py           # manifest builder, strict plan schema, gate result and fixed renderer
schemas/
  model_adapter.schema.json   # request/response contract consumed by the in-repo validator
  response.schema.json        # additive evidence-event definitions
surfaces/
  session.py           # runtime-facing hint/rubric operations and CLI commands
  daemon.py            # identifier-safe JSON routes only; no provider parsing
tests/
  model_adapter_roundtrip.py  # both transports normalize into the same typed result
  tier_gate_roundtrip.py      # adversarial pass/drop/unavailable corpus
```

### Pattern 1: Bounded Hint Plan and Runtime Renderer

**What:** The provider may choose a `focus_span`, an allowed authored-fact reference, and a finite tutoring move; the runtime resolves references and writes the learner text. It does not receive or render a provider-supplied `text` property. [ASSUMED]

**When to use:** Every learner-facing model hint. Rubric-review proposals use their own pending-only contract because they are review artifacts, never score input. [VERIFIED: .planning/phases/08-model-adapter-interface-tier-gate-enforcement/08-CONTEXT.md:34-36]

**Gate algorithm (must be a planned and independently tested deliverable):**

1. Build a manifest from the private item, most recent genuine wrong response, and current Phase 6 tier. Each allowed source receives a stable internal fact ID; all answer/key and higher-tier material is protected. [ASSUMED]
2. Validate provider JSON with `additionalProperties: false`, fixed operation/version, bounded arrays/strings, and finite move/source enums. Any validation error is `drop` with a reason code. [ASSUMED]
3. Resolve every span against the exact learner response and every fact ID against this manifest. Require at least one exact learner-response span, which makes the plan error-specific; never trust a provider-supplied source label by itself. [ASSUMED]
4. Reject any reference not permitted for the current tier, unknown source, duplicate/overlong plan, raw free-text field, attempt to set a tier, or unsupported operation. This is the conservative ambiguity rule. [ASSUMED]
5. For `pass`, render a fixed template using only the resolved learner span and allowed authored fact. For `drop` or `unavailable`, return only the authored fallback / generic unavailable payload; never explain what leaked. [VERIFIED: .planning/phases/08-model-adapter-interface-tier-gate-enforcement/08-CONTEXT.md:23-27]

The binding decision values are quoted here verbatim: “Gate outcomes are `pass`, `drop`, or `unavailable`, with machine-readable reasons. Only `pass` content may enter a learner-facing payload.” [VERIFIED: .planning/phases/08-model-adapter-interface-tier-gate-enforcement/08-CONTEXT.md:26]

### Pattern 2: Typed Unavailable, Never Exception Leakage

**What:** The adapter converts disabled profile, executable-not-found, nonzero CLI exit, timeout, HTTP/URL error, invalid JSON, oversized stdout/body, provider refusal, and transport/schema mismatch into one typed unavailable result. [ASSUMED]

**When to use:** Every model call before touching evidence or a surface. An unavailable adapter is not an error path for sitting, scoring, lessons, authored hints, reporting, or human marking. [VERIFIED: .planning/REQUIREMENTS.md:140-144]

**Example:**

```python
# Source: https://docs.python.org/3.11/library/subprocess.html
completed = subprocess.run(
    command_vector, input=request_json, text=True, capture_output=True,
    timeout=timeout_seconds, shell=False,
)
```

`subprocess.run` supports a timeout and captured output; Python warns that shell invocation moves metacharacter quoting responsibility to the application. [CITED: https://docs.python.org/3.11/library/subprocess.html]

```python
# Source: https://docs.python.org/3/library/urllib.request.html
request = urllib.request.Request(endpoint, data=request_json, method="POST")
with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
    body = response.read(max_response_bytes + 1)
```

Reject a response once it exceeds the cap; catch `HTTPError` before `URLError` because the former is a subclass of the latter. [CITED: https://docs.python.org/3/howto/urllib2.html]

### Pattern 3: Proposal Is Not a Mark

**What:** Store a rubric-review response as a separate `model_review_proposal` event that names the original short-response event and contains one suggestion per authored rubric point; it remains pending until a human uses the existing mark path. [ASSUMED]

**When to use:** `rubric_review` only. Do not pass proposal booleans to `runtime.score_response()` and do not relax the human marker validation. Current source quote: `if marker != "human":` and `"a model verdict is not accepted evidence until Phase 8 (TEACH-09)"`. [VERIFIED: evidence.py:1057-1061]

### Anti-Patterns to Avoid

- **Free-form learner text from the provider:** A filter cannot prove semantic non-disclosure; it violates the gate guarantee. [ASSUMED]
- **Provider-specific parsing in a surface:** It forks the CLI/daemon behavior and violates the required common contract. [VERIFIED: .planning/phases/08-model-adapter-interface-tier-gate-enforcement/08-CONTEXT.md:17-18]
- **Model proposal written as a `mark` event:** Existing marks are human-only accepted facts. [VERIFIED: evidence.py:1035-1080]
- **Raw dropped text in normal evidence/report rendering:** It can itself leak protected facts or a credential-like string. [CITED: https://genai.owasp.org/llmrisk/llm052025-improper-output-handling/]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| Runtime output validation | An LLM-as-judge or a prompt-only prohibition | In-repo strict schema validator + manifest reference resolution + finite runtime templates | A second model is another untrusted generator; structured allowlisting makes a deterministic fail-closed boundary possible. [CITED: https://cheatsheetseries.owasp.org/cheatsheets/RAG_Security_Cheat_Sheet.html] |
| Hosted process execution | A shell command string | `subprocess.run` with a configured argument vector, timeout, captured output, `shell=False` | Python does not implicitly invoke a shell; interpolated strings create a shell-injection boundary. [CITED: https://docs.python.org/3.11/library/subprocess.html] |
| Local HTTP client | A new third-party SDK | `urllib.request.Request` / `urlopen` and `urllib.error` | It meets the locked stdlib-only constraint and supports explicit timeouts/errors. [CITED: https://docs.python.org/3/library/urllib.request.html] |
| Accepted rubric evidence | A second scoring or marking path | Existing human `mark_event` after a pending proposal | The existing mark is a separate append-only fact about a response, not a mutation. [VERIFIED: evidence.py:1027-1080] |
| Dropped-output retention | Full raw provider transcript in normal JSONL | Digest, byte count, reason codes, backend/profile, and request/output fingerprints only | It supports local correlation without re-exposing dropped content through reports. [ASSUMED] |

**Key insight:** Deterministic tier enforcement and arbitrary learner-facing generative prose are incompatible under this phase's no-leak promise; retain generation as a constrained plan, and retain expressive free prose for later only if the guarantee is explicitly reconsidered. [ASSUMED]

## Common Pitfalls

### Pitfall 1: Treating model source labels as evidence

**What goes wrong:** A provider returns `source: "allowed"` while its text or reference actually uses a key/higher-tier fact.

**Why it happens:** Labels originate in the untrusted response.

**How to avoid:** Derive valid IDs from the runtime manifest and compare references/spans to that manifest; refuse unknown IDs and arbitrary text. [ASSUMED]

**Warning signs:** A gate test passes after changing only the provider-supplied label. [ASSUMED]

### Pitfall 2: Free-form text sneaks through a structural schema

**What goes wrong:** A `message`, `rationale`, or unbounded nested object becomes a learner-visible escape hatch.

**Why it happens:** “Structured JSON” is mistaken for a bounded policy language.

**How to avoid:** Make the hint plan `additionalProperties: false`, forbid raw learner-facing text, and render only finite runtime templates. [ASSUMED]

**Warning signs:** Tests can insert “the answer is …” in any field and still obtain `pass`. [ASSUMED]

### Pitfall 3: Dynamic named profiles are not representable by the current validator

**What goes wrong:** A `profiles` object permits arbitrary key names but the custom validator cannot enforce its value schema.

**Why it happens:** The validator deliberately supports a small keyword set. Quote: `SUPPORTED = frozenset([ "type", "properties", "required", "additionalProperties", "enum", "const", "items", "minItems", "minLength", "minimum", "maximum", "$defs", "$ref", "oneOf", ])`. [VERIFIED: schema_validate.py:23-33]

**How to avoid:** Use an array of profile records with fixed properties and runtime validation for unique names/active-profile resolution; add test cases for duplicates, absent active profile, and invalid secret references. [ASSUMED]

**Warning signs:** A profile is accepted but lacks a required transport field.

### Pitfall 4: Adding events without every reader knowing them

**What goes wrong:** A new model-interaction/proposal event is written successfully but existing readers skip it as unknown.

**Why it happens:** Current allowed event types are `("response", "retraction", "mark", "day_tick", "term_lookup", "key_review")` — `term_lookup` and `key_review` were added by Phase 3.1, so the inventory must be read live, never assumed. [VERIFIED: evidence.py:43-44]

**How to avoid:** Update the known-type inventory, raw/event schema definitions, index rebuild behavior, session retrieval, and dedicated event tests together. [ASSUMED]

**Warning signs:** The log contains an event but a session evidence query cannot find its interaction outcome. [ASSUMED]

### Pitfall 5: Confusing a pending model proposal with human acceptance

**What goes wrong:** A short-answer suggestion alters `score`, `review_state`, or a human mark before review.

**Why it happens:** The proposal shape resembles the existing rubric mark shape.

**How to avoid:** Preserve the existing human-only mark restriction, make proposal event type distinct, and test that a model result leaves the original response pending. The present response event writes `"review_state": "pending" if q["type"] == "short" else "n/a"`. [VERIFIED: evidence.py:371-395]

**Warning signs:** A model-only test makes `marks_by_event()` return a settled mark. [ASSUMED]

### Pitfall 6: A timeout becomes a broken sitting

**What goes wrong:** CLI process, local endpoint, malformed response, or unavailable hardware throws through a hint/submit handler.

**Why it happens:** Adapter exceptions escape before the authored fallback is selected.

**How to avoid:** Normalize every listed failure into typed unavailable before the session/daemon returns. Python documents both timeout and `URLError`/`HTTPError` paths. [CITED: https://docs.python.org/3.11/library/subprocess.html; https://docs.python.org/3/howto/urllib2.html]

**Warning signs:** A fake timed-out backend causes a nonzero `hint` command or HTTP 500 rather than an unchanged authored tier. [ASSUMED]

### Pitfall 7: Leaking dropped output through audit and error messages

**What goes wrong:** The user sees the prohibited hint in an evidence report, exception, or browser error.

**Why it happens:** Engineers log “debug text” before the gate.

**How to avoid:** Default to a non-text quarantine descriptor: fingerprint, byte count, backend/profile, outcome, gate code, and timing. Never render raw drop text; an explicit later forensic export would require a separate security decision. [ASSUMED]

**Warning signs:** A `drop` fixture's forbidden phrase appears in any normal report, `/api/*` response, or test failure output. [ASSUMED]

## Code Examples

Verified transport patterns from official sources:

### Hosted CLI invocation

```python
# Source: https://docs.python.org/3.11/library/subprocess.html
try:
    completed = subprocess.run(
        command_vector, input=request_json, text=True, capture_output=True,
        timeout=timeout_seconds, shell=False,
    )
except subprocess.TimeoutExpired:
    return unavailable_result
```

The adapter must cap input and post-capture output before parsing; `communicate`/`run` avoids pipe-buffer deadlocks associated with manually reading both pipes. [CITED: https://docs.python.org/3.11/library/subprocess.html]

### Local endpoint invocation

```python
# Source: https://docs.python.org/3/library/urllib.request.html
try:
    request = urllib.request.Request(endpoint, data=request_json, method="POST")
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        response_bytes = response.read(max_response_bytes + 1)
except urllib.error.HTTPError:
    return unavailable_result
except urllib.error.URLError:
    return unavailable_result
```

The `HTTPError` branch must precede `URLError`, because HTTP errors subclass URL errors. [CITED: https://docs.python.org/3/howto/urllib2.html]

### Gate contract skeleton

```text
provider bytes
  -> strict bounded-plan schema
  -> resolve spans + fact IDs against runtime manifest
  -> reject unknown/protected/higher-tier/ambiguous plans
  -> runtime template renderer
  -> learner-facing payload only on gate pass
```

This is an implementation skeleton, not a published API; exact new field names are intentionally [ASSUMED] until the first plan locks the additive schema.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|---|---|---|---|
| System prompt asks a model not to reveal an answer | Structured output validation and runtime policy enforcement | OWASP LLM guidance current as accessed 2026-08-08 | Treat model output as untrusted and validate it before user/downstream delivery. [CITED: https://cheatsheetseries.owasp.org/cheatsheets/RAG_Security_Cheat_Sheet.html] |
| Vendor SDK per model | Provider-neutral contract over local process/HTTP boundaries | Project Phase 8 decision | Hosted and local adapter paths can share fixtures and callers. [VERIFIED: .planning/phases/08-model-adapter-interface-tier-gate-enforcement/08-CONTEXT.md:17-20] |

**Deprecated/outdated:**

- Prompt-only answer withholding: unsuitable as a security or pedagogical gate because restrictions can be bypassed. [CITED: https://genai.owasp.org/llmrisk/llm022025-sensitive-information-disclosure/]
- A generic free-text “leak detector”: insufficient for the strict guarantee unless it degrades into the bounded-plan design above. [ASSUMED]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|---|---|---|
| A1 | A bounded hint plan plus fixed runtime templates fulfills the requested “generated hint” UX while providing a deterministic no-leak boundary. | Summary / Architecture Patterns | Product may require freer prose than the contract permits. |
| A2 | A runtime manifest can identify allowed authored facts and exact learner-response spans from the Phase 6 payload/state. | Architecture Patterns | Phase 6 may need a small additive runtime seam before Phase 8 can call it. |
| A3 | An array of named backend profiles is preferable to a keyed map under the current custom schema subset. | Standard Stack / Pitfalls | Settings UX may need a different, explicitly implemented validation mechanism. |
| A4 | A non-text quarantine descriptor is the safest default representation of a dropped response. | Don't Hand-Roll / Pitfalls | Local audit may need fuller raw output, requiring an explicit new disclosure control. |
| A5 | New event/type and schema names (`model_review_proposal`, adapter schemas, test filenames) are proposed names, not existing contract values. | Architecture / Validation | Planner must lock names in its first implementation task. |

## Open Questions (RESOLVED)

1. **Does Phase 6 expose a callable permitted-tier/allowed-fact seam when it is implemented?**
   - What we know: Phase 6 makes its policy state machine the sole source of tier progression and defines the authored ladder. [VERIFIED: .planning/phases/06-hint-ladder-cursor-hold-feedback-modes/06-CONTEXT.md:18-31]
   - What's unclear: The Phase 6 work is currently planning context, not present runtime code; no finalized callable manifest exists in this checkout.
   - Recommendation: Make Phase 8 Plan 1 declare the minimal `permitted_hint_context` input contract and add a cross-phase integration test; execution remains dependent on Phase 6 implementation.

2. **Should a human-only forensic export ever retrieve raw dropped output?**
   - What we know: Normal retrieval must not reveal dropped text, and credentials may never enter evidence. [VERIFIED: .planning/phases/08-model-adapter-interface-tier-gate-enforcement/08-CONTEXT.md:38-41]
   - What's unclear: “Recoverable for local audit only when safe” does not define a user-approved local disclosure mechanism.
   - Recommendation: Ship descriptor-only audit in this phase; defer raw recovery until a separate explicit security/UI decision.

3. **What exact hosted CLI executable/protocol will the user configure first?**
   - What we know: The contract must support hosted CLI and local OpenAI-compatible HTTP without caller changes. [VERIFIED: .planning/phases/08-model-adapter-interface-tier-gate-enforcement/08-CONTEXT.md:17-20]
   - What's unclear: No executable or credential source is configured in this environment.
   - Recommendation: Treat executable path/arguments and environment-variable key as profile data, test them using a fake local executable, and keep the default backend disabled.

**Resolutions (plan-time):** Q1 — Plan 08-01 declares the Phase 6 seam (`runtime.teaching_transition`, `runtime.authored_hint`) and preconditions execution on it; Plan 08-06 asserts the cross-phase integration end to end. Q2 — descriptor-only drop audit ships per D-16; raw dropped-output recovery stays deferred until a separate explicit security/UI decision. Q3 — the hosted CLI is the design-target profile built first and the default when a backend is enabled (D-18); executable/args/secret remain profile data tested with a fake executable, and the checked-in default backend stays `disabled` and credential-free.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|---|---|---|---|---|
| Python | Runtime, adapter, tests | ✓ | 3.13.5 | CI retains Python 3.11 compatibility. [VERIFIED: environment probe; .github/workflows/ci.yml:7-13] |
| Git | Existing project workflow only | ✓ | 2.54.0.windows.1 | Not required for an adapter call. [VERIFIED: environment probe] |
| Hosted model CLI | Hosted adapter live use | ✗ / not configured | — | Typed unavailable result; authored offline loop remains complete. [VERIFIED: .planning/REQUIREMENTS.md:140-144] |
| OpenAI-compatible local endpoint | Local adapter live use | ✗ / not running | — | Typed unavailable result; no install or service is required for core study. [VERIFIED: .planning/REQUIREMENTS.md:140-144] |

**Missing dependencies with no fallback:** None for implementation or core study; live provider acceptance is deferred to user configuration.

**Missing dependencies with fallback:** Hosted CLI and local endpoint both fall back to the authored loop.

## Validation Architecture

### Test Framework

| Property | Value |
|---|---|
| Framework | Standalone stdlib Python roundtrip scripts using plain assertions / failure exits. [VERIFIED: .planning/codebase/TESTING.md:5-26] |
| Config file | none |
| Quick run command | `python tests/tier_gate_roundtrip.py` [ASSUMED: Wave 0 file] |
| Full suite command | `for t in tests/*.py; do python "$t" || exit 1; done` [VERIFIED: .github/workflows/ci.yml:66-74] |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|---|---|---|---|---|
| TEACH-04 | Exact wrong-response span produces a specific rendered augmentation from one allowed tier. | unit + integration | `python tests/tier_gate_roundtrip.py` | ❌ Wave 0 |
| TEACH-05 / TEACH-06 | Key, correct option, higher-tier fact, fake source, raw text field, and malformed response all drop. | adversarial unit | `python tests/tier_gate_roundtrip.py` | ❌ Wave 0 |
| TEACH-07 | Pass/drop/unavailable interaction records retrieve by session without leaked drop text. | integration | `python tests/model_adapter_roundtrip.py` | ❌ Wave 0 |
| TEACH-08 | One short response yields a complete pending per-rubric-point proposal. | integration | `python tests/model_adapter_roundtrip.py` | ❌ Wave 0 |
| TEACH-09 / MODEL-05 | Proposal never sets score/accepted mark; explicit human mark remains the only settle path. | integration | `python tests/model_adapter_roundtrip.py` | ❌ Wave 0 |
| MODEL-01 / MODEL-02 | Fake hosted executable and fake loopback HTTP return exactly the same normalized result from switched config profiles. | contract integration | `python tests/model_adapter_roundtrip.py` | ❌ Wave 0 |
| MODEL-03 | disabled, timeout, malformed, refused, and unreachable backends preserve authored hint/session behavior. | integration | `python tests/model_adapter_roundtrip.py` | ❌ Wave 0 |
| MODEL-04 | Usage contract is printed/committed and prohibits direct score/accepted evidence. | contract test | `python tests/model_adapter_roundtrip.py` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `python tests/tier_gate_roundtrip.py` [ASSUMED: Wave 0 file]
- **Per wave merge:** `for t in tests/*.py; do python "$t" || exit 1; done` [VERIFIED: .github/workflows/ci.yml:66-74]
- **Phase gate:** Full suite green, schema validations green, and adversarial corpus all `drop` before `$gsd-verify-work`. [ASSUMED]

### Wave 0 Gaps

- [ ] `tests/tier_gate_roundtrip.py` — deterministic manifest, strict-schema, pass/drop/unavailable, and adversarial leakage corpus.
- [ ] `tests/model_adapter_roundtrip.py` — hosted fake executable + local loopback fake server, unavailable cases, evidence/proposal retrieval, and no-score invariant.
- [ ] Adapter request/result JSON schema plus schema-validator tests — validates bounded plans before any transport plumbing.
- [ ] Cross-phase fixture/seam from Phase 6 — exposes permitted tier and authored fact manifest without sending either private data or tier state to the browser.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---|---|---|
| V2 Authentication | no | Single-user local project has no accounts/login; do not invent auth in this phase. [VERIFIED: .planning/PROJECT.md:231-234] |
| V3 Session Management | yes | Treat server session IDs as opaque allowlist keys; preserve existing server-side session resolution. [VERIFIED: surfaces/daemon.py:673-760] |
| V4 Access Control | yes | Runtime owns access to private item/key/tier and gates any learner-visible capability at that trusted boundary. [VERIFIED: runtime.py:8-10; .planning/phases/08-model-adapter-interface-tier-gate-enforcement/08-CONTEXT.md:23-27] |
| V5 Input Validation | yes | Strict adapter-plan schema, exact manifest-reference resolution, output-size caps, and refusal of unknown fields. [CITED: https://cheatsheetseries.owasp.org/cheatsheets/RAG_Security_Cheat_Sheet.html] |
| V6 Stored Cryptography | no | No new encrypted store is proposed; use fingerprints only for safe audit correlation, never as encryption. [ASSUMED] |

OWASP ASVS is current at version 5.0.0 and identifies V4 Access Control and V5 Validation/Sanitization/Encoding as applicable verification categories. [CITED: https://owasp.org/www-project-application-security-verification-standard/; https://devguide.owasp.org/en/03-requirements/04-security-rat/]

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---|---|---|
| Learner prompt injection asks provider to reveal the key | Information Disclosure | Provider result is untrusted; manifest gate and renderer have no free-text pass path. [CITED: https://genai.owasp.org/llmrisk/llm022025-sensitive-information-disclosure/] |
| Provider output leaks higher-tier/key fact | Information Disclosure | Exact allowed-fact references only; unknown/ambiguous plan is `drop`. [ASSUMED] |
| Hosted CLI argument injection | Tampering / Elevation | Configured argument vector, no learner values in command construction, `shell=False`. [CITED: https://docs.python.org/3.11/library/subprocess.html] |
| Local endpoint timeout/malformed payload | Denial of Service | Timeout, request/response size bounds, typed unavailable and authored fallback. [CITED: https://docs.python.org/3/library/urllib.request.html] |
| Provider credential or dropped text appears in evidence | Information Disclosure | Secret references only; descriptor-only dropped audit; normal reports never include raw provider bytes. [VERIFIED: .planning/phases/08-model-adapter-interface-tier-gate-enforcement/08-CONTEXT.md:38-41] |
| Proposal treated as accepted score | Tampering | Distinct proposal event and existing `marker="human"` accepted-mark path. [VERIFIED: evidence.py:1057-1080] |

## Sources

### Primary (HIGH confidence)

- [Python subprocess documentation](https://docs.python.org/3.11/library/subprocess.html) — timeout, captured output, shell and pipe-safety rules.
- [Python urllib.request documentation](https://docs.python.org/3/library/urllib.request.html) and [urllib exception HOWTO](https://docs.python.org/3/howto/urllib2.html) — timeout, request, HTTP/URL error behavior.
- [OWASP LLM05: Improper Output Handling](https://genai.owasp.org/llmrisk/llm052025-improper-output-handling/) and [OWASP RAG Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/RAG_Security_Cheat_Sheet.html) — validate model output before users/downstream systems and prefer structured allowed actions.
- In-repo source-of-truth: `runtime.py`, `evidence.py`, `schema_validate.py`, `schemas/settings.schema.json`, `schemas/response.schema.json`, `surfaces/session.py`, `surfaces/daemon.py`, and Phase 8 CONTEXT/requirements cited inline.

### Secondary (MEDIUM confidence)

- [OWASP LLM02: Sensitive Information Disclosure](https://genai.owasp.org/llmrisk/llm022025-sensitive-information-disclosure/) — prompt restrictions may be bypassed and output disclosure risk.
- [OWASP ASVS project](https://owasp.org/www-project-application-security-verification-standard/) — ASVS 5.0.0 release/current categories.

### Tertiary (LOW confidence)

- None. Original bounded-plan and audit-descriptor design claims are explicitly marked `[ASSUMED]` pending implementation validation.

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH — project constraint, installed runtime, CI floor, and stdlib docs are directly verified.
- Architecture: MEDIUM — repository boundaries are verified; the bounded-plan detector is an original, explicitly labeled design recommendation.
- Pitfalls: HIGH — source-level evidence, official Python transport docs, and OWASP output-boundary guidance agree.

**Research date:** 2026-08-08
**Valid until:** 2026-09-07 for stable stdlib/repository contracts; reconfirm provider protocol details when a real CLI profile is selected.
