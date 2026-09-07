# 19C-01 summary

## Why this summary exists

A measured fact contradicted the plan: the local endpoint and model work, but
the product's adapter request is rejected and seeding never consults it.

Phase 19C activated the shipped loopback `local-qwen` profile with the installed
`qwen3.5:4b` model and ran the director, recommendation pass, and seeding entry
point against a disposable copy of the real EMT unit. The endpoint and model
worked directly, while the product paths exposed three retained defects: the
OpenAI-compatible transport sends the wrong provider request shape, seeding is
still disconnected from the shared adapter, and unavailable director responses
drop their recorded operation id.

The canonical EMT course was not changed. No diagnostic output was accepted.
Verbatim records and their hashes are in `19C-VERIFICATION.md`. The Phase 19C
diagnostic gate is complete, but Phase 19D must wait for the two backend-path
repairs and a successful rerun. The shared `STATE.md` and roadmap checkbox were
left untouched because a concurrent Phase 19A course-shell task owns that
planning lane. The one plan commit is also deferred because that concurrent
snapshot currently fails the required full preflight in
`tests/binding_roundtrip.py`.
