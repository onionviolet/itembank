# Synapse and seer: public primary-source review

**Accessed:** 2026-09-09. **Scope:** public web pages only. This report does not
inspect, request, reproduce, or infer access to either closed-source project.

## Identity and evidence quality

**Verified public match, with revised wording.** Thomas Havlik's portfolio,
[thavlik.dev](https://thavlik.dev/), has project headings "Synapse" and
lowercase "seer." It matches the screenshot's distinctive descriptions:
Synapse is an "AI-native LMS. Working title," and seer is a "Hybrid
neural/keyword search engine." The page says seer is Synapse's principal
search backend. It also identifies its author as a medical student and software
architect. These details make an unrelated same-name project unlikely.

**Source-version discrepancy.** The supplied screenshot describes seer's
multimodal ingestion through Kafka pipelines. The currently accessible
portfolio instead says NATS JetStream-backed pipelines. This is evidence of
different public descriptions or revisions, not evidence that a migration
occurred. The public material does not provide dates or implementation history
that resolve the discrepancy.

**Verified, author-reported claims.** The portfolio describes Synapse as an
institution-scale, medical-curriculum LMS with AI assistance, event-driven and
remote-learning support, and a Rust, NATS JetStream, Postgres, and Kubernetes
backend. It says a non-AI layer uses Lean and Prolog for answer correctness and
curriculum citations. It describes seer as multimodal retrieval across slides,
PDFs, video, images, and Anki decks, with NATS JetStream pipelines, a Rust,
Postgres, and Kubernetes core, plus cryptographically verifiable audit tokens.
The source calls both projects closed source and says details and demos are
available only on request. [Synapse and seer portfolio sections](https://thavlik.dev/#projects)

**Not independently verified.** No public repository, architecture document,
demo, test suite, deployment, benchmark, pilot protocol, curriculum corpus, or
third-party evaluation was found in the checked public source. Therefore,
claims about correctness, citations, privacy, throughput, latency, scale,
reproducibility, and positive pilot feedback are author statements, not
independently established results. Public repositories linked from the same
portfolio for other projects do not validate the closed projects.

## Transferable patterns for itembank

### P1. Citation-bearing learner answers, not citation-shaped confidence

**Pattern.** Make every generated learning explanation or source-grounded
answer carry stable source-binding and passage identifiers. The UI should let a
learner open the exact source passage, see a short quoted context, and learn
when no supported passage was retrieved.

**Why transfer.** This turns "where did that come from?" into an inspectable
learner action and fits itembank's existing source-binding and authority model.

**Limit.** A citation proves only that a system linked an answer to a passage.
It does not prove that the passage is current, applicable, correctly
interpreted, or that the model's claim follows from it. The source binding,
rights state, revision, and human review remain the factual-truth controls.

### P2. Small, explainable hybrid retrieval

**Pattern.** Start with metadata filters plus lexical full-text retrieval and
embedding retrieval over the same source chunks. Fuse a bounded candidate set,
retain per-channel rank and score, and return source passages rather than an
opaque answer. Hybrid search is a recognized pattern: Microsoft documents
parallel text and vector queries merged with reciprocal-rank fusion.
[Microsoft hybrid-search overview](https://learn.microsoft.com/en-us/azure/search/hybrid-search-overview)

**Why transfer.** Exact objective names, formulas, and terminology often need
lexical matching. Conceptual paraphrases can benefit from vector retrieval.
The rank provenance gives learners and reviewers a way to diagnose a bad result.

**Limit.** Do not assume hybrid is automatically accurate. Vector retrieval can
return a nearest result even for an off-topic query, and fusion weights,
chunking, metadata, corpus quality, and evaluation set decide usefulness.
[Microsoft vector-query limitations](https://learn.microsoft.com/en-us/azure/search/vector-search-how-to-query?tabs=query-2024-07-01%2Cfilter-2024-07-01)

### P3. Reproducible ingestion provenance, proportionally

**Pattern.** Record a source fingerprint, extractor version, chunking policy,
derived-chunk fingerprints, index revision, and failed-state reason for each
ingestion operation. Expose that lineage in staff or author review, not as
decorative cryptography in the learner UI.

**Why transfer.** It supports re-indexing, stale detection, rights review,
conflict recovery, and explanation of which revision produced a citation.

**Limit.** A signed or hashed event does not itself make an output
reproducible. Reproduction also needs retained source bytes or an authorized
reference, deterministic transforms where possible, versioned models, and a
record of configuration and access rights. The portfolio's audit-token behavior
is not publicly inspectable, so it is inspiration only.

### P4. Event-driven work only where the learner feels the gain

**Pattern.** Treat large PDF, slide, image, audio, or video extraction as
restartable background jobs with idempotency keys, visible states, and an
explicit last accepted index revision. Keep the normal course and assessment
path local and simple.

**Why transfer.** Learners can continue studying while a source is processed,
and a failed extractor cannot silently replace accepted source state.

**Limit.** NATS, Kubernetes, and distributed services are not a prerequisite
for this behavior. They add operational cost and new failure modes. Begin with
the operation journal and queue abstraction already justified by a concrete
long-running intake path, then test whether distributed workers are needed.

### P5. Formal methods at protocol boundaries, source review for facts

**Pattern.** Use deterministic runtime checks for response schema, scoring,
feedback disclosure, source-binding shape, and operation transitions. Consider
formal specification only for narrow, stable, high-consequence invariants.
Lean is an interactive theorem prover whose kernel checks proof terms, so it
can establish a stated formal property when the formalization is sound.
[Lean Language Reference](https://lean-lang.org/doc/reference/latest/)

**Why transfer.** It reinforces itembank's one-scorer boundary without asking a
model to certify itself.

**Limit.** Formal proof cannot establish that a medical statement is true from
the world, that a source is authoritative, or that a human-authored
formalization captured the intended curriculum claim. Prolog rules likewise
enforce the rules encoded, not factual medicine. For itembank, source
provenance, revision review, disclosed uncertainty, and reviewer acceptance
must remain separate from scoring correctness.

## Candidate disposition

P1 through P5 are candidate patterns for comparison. No new registration,
architecture, or upstream implementation is accepted by this report. If a
future owner chooses to prototype, the smallest credible candidate is P2 plus
P1 on a learner-owned, rights-cleared sample corpus, with source passage links,
explicit unsupported-result state, and a small judged retrieval set. It should
not claim factual verification, formal proof, or production-scale search.
