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

The bounded repair now sends provider-native chat requests and parses assistant
JSON through the shared adapter. Public seeding resolves the active settings
profile through that boundary. Unavailable director results retain the journal
operation id. Focused tests and guard pass.

The real rerun produced one valid, unbound director recommendation. Its
operation id is `70d3cdd7a1244833`. The disposable seeding run reached the
configured backend and the six-stage flow, but its draft failed deterministic
checks after the retry cap. Nothing was accepted and the canonical EMT course
was not changed. Phase 19C no longer blocks Phase 19D on backend connectivity.
