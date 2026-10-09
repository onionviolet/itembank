# Source-question adapter proposal, October 3

Status: concrete additive v1 proposal for direct review. It is not registered
production syntax. Owner: coordinator, with L1 implementing the native surface.

The existing adapter has hint, rubric_review, author and treatment_recommend
operations. None represents a learner question about explicitly selected
sources. Reusing a hint without a runtime tier or treating an author draft as a
chat answer would misstate authority. Add `source_question` to the same adapter
and `context_request` to its closed payload vocabulary after direct acceptance.

## Concrete request and candidate

The existing adapter envelope remains version 1. The proposed operation uses:

```json
{
  "operation": "source_question",
  "payload": {
    "context_request": {
      "schema_version": 1,
      "course_object_id": "course-example",
      "question": "How do these two source claims differ?",
      "source_spans": [
        {"citation_id": "source-1", "source_id": "source-example", "locator_id": "passage-example", "fingerprint": "accepted-source-fingerprint", "text": "Exact admitted passage."}
      ],
      "learner_notes": [],
      "attempt": 1
    }
  }
}
```

The full adapter envelope also retains its required immutable interaction ID,
profile and version fields. The untrusted provider candidate is exactly:

```json
{
  "schema_version": 1,
  "answer": "A cited explanation labeled as generated synthesis.",
  "citations": [{"citation_id": "source-1", "quote": "Exact admitted passage."}],
  "uncertainty": "What the selected sources do not establish."
}
```

Closed objects reject unknown fields. Question is nonempty and at most 2000
characters. Each selected source/note keeps its existing owner's size limits;
the full preview and request have a 24 KiB byte budget rather than silent
truncation. Answer is at most 8 KiB and uncertainty at most 2 KiB. At least
one admitted source passage is required; private notes
are optional and visibly separate. Citation IDs are request-local and unique.
At least one source citation is required; every citation must identify a sent
span/note and quote an exact nonempty substring of at most 2000 characters.
There are one to 16 citations and at most 16 KiB of serialized candidate bytes.
Quote validation proves local
traceability, not that the explanation is true. Answer and uncertainty remain
generated advisory text and cannot contain accepted marks or commands.

## Authority, rights and recovery

Only pure source-question help is admitted. Assessment-linked requests are
refused before invocation; this does not expand runtime hint disclosure.
No private bank/key content enters the corpus. Read, quote and transform grants are
revalidated for every selected source. Any remote processing also requires its
separate grant. Notes remain learner-owned, never source truth.

An explicit preview names provider/profile, transport/destination, question,
exact source passages and optional included private-note text. Only deliberate
submission of that preview may invoke the configured backend. Configuration
does not itself authorize egress. Tests use synthetic material/transports;
this implementation request authorizes no live paid or private-data invocation.

Existing adapter unavailable/error envelopes remain authoritative. Surface
validation refuses malformed or unsupported candidates. Cancel retains input;
late results never display. Revalidate source/rights/revision after invocation,
then show cited synthesis and exact task return. Restart without the process
handle reports unresolved outcome and requires an explicit retry with provider
cost disclosure. No accepted artifact, note, response or score is created.

Decision Q4: accept this bounded additive operation, request a revision, or
implement selection/preview only and retain model invocation as a prototype.
Production, served/native behavior and human acceptance require their own
evidence after the format decision.

## Prior-implementation refinement

The [October 3 continuation](../prior-implementation-improvements-2026-10-03.md)
adds an executable closed request specimen at
[`source_question.schema.json`](../../../prototypes/prior-improvements-20261003/source_question.schema.json).
Two synthetic readiness checks exercise this shape through a temporary adapter
overlay and the existing exact-citation validator. The overlay is restored
after the test. It grants no provider/egress authority and does not register a
production operation. The exact direct Q4 choice remains pending.
