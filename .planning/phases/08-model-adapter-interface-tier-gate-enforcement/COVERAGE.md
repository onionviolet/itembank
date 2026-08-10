# Phase 8 API Coverage Matrix

**Deterministic scan result:** `{"detected": false}` on the pre-replan plan text plus the ROADMAP phase body. Manual scope inspection of `08-CONTEXT.md` D-01..D-04/D-17/D-18 and `08-AI-SPEC.md` confirms this phase **does** integrate external model services: a hosted Claude-Code-class CLI and a local OpenAI-compatible HTTP endpoint, both behind one adapter boundary. The detector's verb/noun co-occurrence scan misses this because the contracts speak of "profiles", "transports", and "provider" rather than "API integration". This matrix is the binding record; the scan result is recorded so the discrepancy is not silently papered over.

| External API / service capability | Decision | Reason |
|---|---|---|
| Hosted CLI model invocation (Claude Code-class executable) | INTEGRATE | The design-target default backend (D-18); `model_adapter.py` subprocess transport with `shell=False`, bounded timeout/output, typed request/result envelope (D-01/D-02, AI-SPEC §2). |
| Local OpenAI-compatible HTTP endpoint (llama.cpp / Ollama / Qwen) | INTEGRATE | Additional registration behind the same `invoke(request, profile)` boundary; parity proven by loopback fixtures (D-02/D-18, MODEL-01/MODEL-02). |
| Provider SDKs / agent frameworks (OpenAI SDK, LangChain, etc.) | OPT-OUT | Research Standard Stack rejects SDKs: they break hosted/local parity and add runtime dependencies (08-RESEARCH.md "Alternatives Considered"; AI-SPEC §2). |
| Third-party tracing / telemetry export (Arize Phoenix, hosted gradebook) | OPT-OUT | AI-SPEC §5 selects the local append-only evidence store for traces; Directive §4.3 forbids telemetry and hosted storage. |
| Raw dropped-output retrieval API | OPT-OUT | D-16 ships descriptor-only audit (fingerprint, byte count, reason codes); raw transcript recovery is an OPEN item needing a separate security decision (08-UI-SPEC "Unresolved and Do Not Build"). |
| Live provider acceptance testing | OPT-OUT (deferred to user config) | No executable/credential is configured in this environment; profiles ship disabled by default and are exercised with fake CLI executables and loopback servers (08-RESEARCH.md Environment Availability; UI-SPEC OPEN). |

**Capability surface integrated:** `hint` (error-specific guidance) and `rubric_review` (pending per-point short-answer suggestions), one typed request/result envelope, versioned JSON Schema contracts, strict timeout and output caps, typed `unavailable` degradation, and append-only interaction/proposal evidence. Provider-native output never reaches a learner payload (D-05..D-08).
